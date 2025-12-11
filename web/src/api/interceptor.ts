import axios from 'axios';
import type { AxiosRequestConfig, AxiosResponse } from 'axios';
import { Message, Modal } from '@arco-design/web-vue';
import { useUserStore } from '@/store';
import { getToken } from '@/utils/auth';

export interface HttpResponse<T = unknown> {
  status: number;
  msg: string;
  code: number;
  data: T;
}

if (import.meta.env.VITE_API_BASE_URL) {
  axios.defaults.baseURL = import.meta.env.VITE_API_BASE_URL;
}

axios.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    // let each request carry token
    // this example using the JWT token
    // Authorization is a custom headers key
    // please modify it according to the actual situation
    const token = getToken();
    if (token) {
      if (!config.headers) {
        config.headers = {};
      }
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    // do something
    return Promise.reject(error);
  }
);
// add response interceptors
axios.interceptors.response.use(
  (response: AxiosResponse<HttpResponse | any>) => {
    const res = response.data;

    // 对于认证接口（登录/注册），直接返回响应，让组件自己处理
    const isAuthEndpoint = response.config.url?.includes('/api/auth/');

    // 对于直接返回数据的接口（如 dashboard/stats），如果没有 code 字段，直接返回数据
    const isDirectDataEndpoint =
      response.config.url?.includes('/api/dashboard/stats') ||
      response.config.url?.includes('/api/equipment/inventory') ||
      response.config.url?.includes('/api/equipment/inbound') ||
      response.config.url?.includes('/api/equipment/outbound') ||
      response.config.url?.includes('/api/rental/') ||
      response.config.url?.includes('/api/settlement/');

    // 如果响应没有 code 字段，说明是直接返回的数据对象
    if (!('code' in res) && !isAuthEndpoint) {
      return res;
    }

    // 兼容后端响应格式：code 200 或 20000 都算成功
    // 后端使用 code: 200, message 字段
    // 旧接口可能使用 code: 20000, msg 字段
    const isSuccess = res.code === 200 || res.code === 20000;

    if (!isSuccess && !isAuthEndpoint) {
      const errorMsg = res.msg || res.message || 'Error';
      Message.error({
        content: errorMsg,
        duration: 5 * 1000,
      });
      // 50008: Illegal token; 50012: Other clients logged in; 50014: Token expired;
      if (
        [50008, 50012, 50014].includes(res.code) &&
        response.config.url !== '/api/user/info'
      ) {
        Modal.error({
          title: 'Confirm logout',
          content:
            'You have been logged out, you can cancel to stay on this page, or log in again',
          okText: 'Re-Login',
          async onOk() {
            const userStore = useUserStore();

            await userStore.logout();
            window.location.reload();
          },
        });
      }
      return Promise.reject(new Error(errorMsg));
    }
    // 对于认证接口，返回完整的 response，让组件可以访问 response.data
    if (isAuthEndpoint) {
      return response;
    }
    return res;
  },
  (error) => {
    // 处理 HTTP 错误响应（如 401, 400 等）
    const errorMsg =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.response?.data?.msg ||
      error.msg ||
      'Request Error';
    // 对于认证接口的错误，不在这里显示消息，让组件自己处理
    const isAuthEndpoint = error.config?.url?.includes('/api/auth/');
    if (!isAuthEndpoint) {
      Message.error({
        content: errorMsg,
        duration: 5 * 1000,
      });
    }
    return Promise.reject(error);
  }
);
