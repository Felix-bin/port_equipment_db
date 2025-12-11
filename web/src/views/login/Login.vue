<template>
  <div class="login-container">
    <div class="login-content">
      <!-- Left Side: Image and Branding -->
      <div class="login-left">
        <div class="brand-overlay">
          <div class="brand-header">
            <div class="logo-icon">
              <span class="icon-container"><icon-box /></span>
            </div>
            <span class="brand-name">海洋装备管理</span>
          </div>

          <div class="brand-content">
            <h1 class="brand-title">智能化船舶装备<br />租赁与仓储平台</h1>
            <p class="brand-subtitle"
              >为港口管理、设备租赁和仓储运营提供专业的数字化解决方案</p
            >

            <div class="brand-stats">
              <div class="stat-item">
                <div class="stat-value">1000+</div>
                <div class="stat-label">装备类型</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">50+</div>
                <div class="stat-label">合作港口</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">99.9%</div>
                <div class="stat-label">系统可用性</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Side: Login Form -->
      <div class="login-right">
        <div class="login-form-container">
          <div class="form-header">
            <h2 class="form-title">登录您的账户</h2>
            <p class="form-subtitle">输入您的凭据以访问仓储管理系统</p>
          </div>

          <a-form
            :model="formState"
            name="basic"
            autocomplete="off"
            layout="vertical"
            @submit="onFinish"
          >
            <a-form-item
              field="username"
              label="用户名或邮箱"
              :rules="[{ required: true, message: '请输入用户名或邮箱!' }]"
            >
              <a-input
                v-model="formState.username"
                placeholder="your.email@company.com"
                size="large"
              />
            </a-form-item>

            <a-form-item
              field="password"
              label="密码"
              :rules="[{ required: true, message: '请输入密码!' }]"
            >
              <a-input-password
                v-model="formState.password"
                placeholder="........"
                size="large"
              />
            </a-form-item>

            <a-form-item field="remember">
              <a-checkbox v-model="formState.remember">保持登录状态</a-checkbox>
            </a-form-item>

            <a-form-item class="login-button-wrapper">
              <a-button
                type="primary"
                html-type="submit"
                size="large"
                class="login-button"
                :loading="loading"
              >
                登录系统
              </a-button>
            </a-form-item>
          </a-form>

          <div class="register-link-wrapper">
            <span>还没有账户?</span>
            <a class="register-link" @click="goToRegister">立即注册</a>
          </div>

          <div class="login-footer">
            <p>需要帮助? <a href="#">联系技术支持</a></p>
            <p class="copyright">© 2025 海洋装备管理系统 · 版本 2.0</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { reactive, ref } from 'vue';
  import { useRouter } from 'vue-router';
  import { Message } from '@arco-design/web-vue';
  import { login as loginApi } from '@/api/auth';
  import { setToken } from '@/utils/auth';
  import { useUserStore } from '@/store';
  import bgImage from '@/assets/images/modern-shipping-port-with-containers-and-cranes-at.jpg';

  const router = useRouter();
  const userStore = useUserStore();
  const loading = ref(false);
  const bgImageUrl = `url(${bgImage})`;

  const formState = reactive({
    username: '',
    password: '',
    remember: false,
  });

  const onFinish = async (data) => {
    // Arco Design 的 @submit 事件会传递 { values, errors } 对象
    const { values, errors } = data;

    if (errors) {
      console.log('Form validation failed:', errors);
      return;
    }

    loading.value = true;
    try {
      const response = await loginApi({
        username: values.username,
        password: values.password,
      });

      if (response.data.code === 200) {
        Message.success(response.data.message || '登录成功');

        // 存储用户信息到 localStorage/sessionStorage（先存储，setToken 会检查）
        if (values.remember) {
          localStorage.setItem('userInfo', JSON.stringify(response.data.data));
        } else {
          sessionStorage.setItem(
            'userInfo',
            JSON.stringify(response.data.data)
          );
        }

        // 设置 token（使用工具函数，确保 isLogin() 能正确检测）
        const token =
          response.data.data?.user_id?.toString() ||
          response.data.token ||
          'authenticated';
        setToken(token);

        // 更新用户 store 信息
        if (response.data.data) {
          userStore.setInfo({
            name: response.data.data.real_name || response.data.data.username,
            accountId: response.data.data.user_id?.toString(),
            email: response.data.data.email,
            phone: response.data.data.phone,
            role: response.data.data.role || 'operator',
          });
        }

        // 跳转到工作台主界面
        router.push('/dashboard/workplace').catch((err) => {
          // 忽略重复导航错误
          if (err.name !== 'NavigationDuplicated') {
            console.error('Navigation error:', err);
          }
        });
      } else {
        Message.error(response.data.message || '登录失败');
      }
    } catch (error) {
      const errorMessage =
        error.response?.data?.detail ||
        error.response?.data?.message ||
        '登录失败，请检查用户名和密码';
      Message.error(errorMessage);
    } finally {
      loading.value = false;
    }
  };

  const goToRegister = () => {
    router.push('/register');
  };
</script>

<style scoped>
  .login-container {
    height: 100vh;
    width: 100vw;
    overflow: hidden;
    background: #f0f2f5;
  }

  .login-content {
    display: flex;
    height: 100%;
  }

  .login-left {
    flex: 1;
    background-image: v-bind('bgImageUrl');
    background-size: cover;
    background-position: center;
    position: relative;
    display: flex;
    flex-direction: column;
  }

  .login-left::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(
      135deg,
      rgba(16, 44, 87, 0.75) 0%,
      rgba(13, 31, 60, 0.7) 100%
    );
  }

  .brand-overlay {
    position: relative;
    z-index: 1;
    padding: 40px;
    height: 100%;
    display: flex;
    flex-direction: column;
    color: white;
  }

  .brand-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: auto;
  }

  .icon-container {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 6px;
  }

  .brand-name {
    font-size: 18px;
    font-weight: 600;
    letter-spacing: 0.5px;
  }

  .brand-content {
    margin-bottom: 60px;
    padding-right: 20%;
  }

  .brand-title {
    font-size: 42px;
    font-weight: 700;
    line-height: 1.2;
    margin-bottom: 24px;
    color: white;
  }

  .brand-subtitle {
    font-size: 16px;
    line-height: 1.6;
    opacity: 0.85;
    margin-bottom: 48px;
  }

  .brand-stats {
    display: flex;
    gap: 48px;
  }

  .stat-value {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 4px;
  }

  .stat-label {
    font-size: 14px;
    opacity: 0.7;
  }

  .login-right {
    flex: 1;
    max-width: 600px;
    background: white;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 40px;
  }

  .login-form-container {
    width: 100%;
    max-width: 400px;
  }

  .form-header {
    margin-bottom: 40px;
  }

  .form-title {
    font-size: 28px;
    font-weight: 700;
    color: #1a1a1a;
    margin-bottom: 8px;
  }

  .form-subtitle {
    color: #666;
    font-size: 14px;
  }

  /* Customizing Ant Design Form */
  :deep(.ant-form-item-label > label) {
    font-weight: 500;
    color: #333;
  }

  :deep(.arco-form-item-label-col) {
    width: 100%;
  }

  .form-label-wrapper {
    display: flex;
    justify-content: space-between;
    width: 100%;
    align-items: center;
  }

  .form-label-wrapper span {
    font-weight: 500;
    color: #333;
  }

  .forgot-password-link {
    color: #165dff;
    font-size: 13px;
    cursor: pointer;
    text-decoration: none;
  }

  .forgot-password-link:hover {
    text-decoration: underline;
  }

  .login-button-wrapper {
    text-align: center;
  }

  .login-button {
    background: #0d3f66;
    border-color: #0d3f66;
    height: 48px;
    font-size: 16px;
    margin-top: 12px;
    border-radius: 4px;
    max-width: 100%;
    display: inline-block;
    margin-left: auto;
    margin-right: auto;
  }

  .login-button:hover {
    background: #104a7a;
    border-color: #104a7a;
  }

  .register-link-wrapper {
    text-align: center;
    margin-top: 24px;
    margin-bottom: 32px;
    color: #666;
    font-size: 14px;
  }

  .register-link {
    color: #165dff;
    cursor: pointer;
    margin-left: 4px;
    font-weight: 500;
    text-decoration: none;
    transition: color 0.2s;
  }

  .register-link:hover {
    color: #0e42d2;
    text-decoration: underline;
  }

  .login-footer {
    text-align: center;
    color: #666;
    font-size: 14px;
  }

  .login-footer a {
    color: #1890ff;
    cursor: pointer;
  }

  .login-footer a:hover {
    text-decoration: underline;
  }

  .copyright {
    margin-top: 12px;
    color: #999;
    font-size: 12px;
  }

  @media (max-width: 992px) {
    .login-left {
      display: none;
    }

    .login-right {
      max-width: 100%;
    }
  }
</style>
