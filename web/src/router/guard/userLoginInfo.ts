import type { Router, LocationQueryRaw } from 'vue-router';
import NProgress from 'nprogress'; // progress bar

import { useUserStore } from '@/store';
import { isLogin } from '@/utils/auth';

export default function setupUserLoginInfoGuard(router: Router) {
  router.beforeEach(async (to, from, next) => {
    NProgress.start();
    const userStore = useUserStore();
    if (isLogin()) {
      if (userStore.role) {
        next();
      } else {
        // 尝试从 localStorage/sessionStorage 恢复用户信息
        const userInfoStr =
          localStorage.getItem('userInfo') ||
          sessionStorage.getItem('userInfo');
        if (userInfoStr) {
          try {
            const userInfo = JSON.parse(userInfoStr);
            userStore.setInfo({
              name: userInfo.real_name || userInfo.username,
              accountId: userInfo.user_id?.toString(),
              email: userInfo.email,
              phone: userInfo.phone,
              role: userInfo.role || 'operator',
            });
            next();
          } catch (error) {
            // 如果解析失败，尝试调用 API（如果存在）
            try {
              await userStore.info();
              next();
            } catch (apiError) {
              // API 不存在或失败时，仍然允许访问
              console.warn('Failed to fetch user info:', apiError);
              next();
            }
          }
        } else {
          // 没有存储的用户信息，尝试调用 API（如果存在）
          try {
            await userStore.info();
            next();
          } catch (error) {
            // API 不存在或失败时，仍然允许访问
            console.warn('Failed to fetch user info:', error);
            next();
          }
        }
      }
    } else {
      // 未登录时允许访问所有页面
      next();
    }
  });
}
