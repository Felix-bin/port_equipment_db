<template>
  <a-card v-if="showDebug" title="调试信息" class="debug-card">
    <a-descriptions :column="1" bordered>
      <a-descriptions-item label="UserStore AccountId">
        {{ userStore.accountId || '未设置' }}
      </a-descriptions-item>
      <a-descriptions-item label="UserStore Name">
        {{ userStore.name || '未设置' }}
      </a-descriptions-item>
      <a-descriptions-item label="UserStore Email">
        {{ userStore.email || '未设置' }}
      </a-descriptions-item>
      <a-descriptions-item label="UserStore Phone">
        {{ userStore.phone || '未设置' }}
      </a-descriptions-item>
      <a-descriptions-item label="UserStore Role">
        {{ userStore.role || '未设置' }}
      </a-descriptions-item>
      <a-descriptions-item label="LocalStorage UserInfo">
        <pre>{{ localStorageInfo }}</pre>
      </a-descriptions-item>
      <a-descriptions-item label="SessionStorage UserInfo">
        <pre>{{ sessionStorageInfo }}</pre>
      </a-descriptions-item>
      <a-descriptions-item label="Token">
        {{ tokenInfo || '未设置' }}
      </a-descriptions-item>
    </a-descriptions>
    
    <a-space style="margin-top: 16px">
      <a-button type="primary" @click="refreshStore">刷新Store</a-button>
      <a-button @click="clearStorage">清除存储</a-button>
    </a-space>
  </a-card>
</template>

<script lang="ts" setup>
  import { ref, computed, onMounted } from 'vue';
  import { Message } from '@arco-design/web-vue';
  import { useUserStore } from '@/store';
  import { getToken } from '@/utils/auth';

  const userStore = useUserStore();
  const showDebug = ref(true);

  const localStorageInfo = computed(() => {
    const info = localStorage.getItem('userInfo');
    if (!info) return '空';
    try {
      return JSON.stringify(JSON.parse(info), null, 2);
    } catch {
      return info;
    }
  });

  const sessionStorageInfo = computed(() => {
    const info = sessionStorage.getItem('userInfo');
    if (!info) return '空';
    try {
      return JSON.stringify(JSON.parse(info), null, 2);
    } catch {
      return info;
    }
  });

  const tokenInfo = computed(() => {
    return getToken();
  });

  const refreshStore = () => {
    const userInfoStr = localStorage.getItem('userInfo') || sessionStorage.getItem('userInfo');
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
        Message.success('Store已刷新，accountId: ' + userInfo.user_id);
      } catch (err) {
        Message.error('刷新失败: ' + err.message);
      }
    } else {
      Message.warning('未找到用户信息');
    }
  };

  const clearStorage = () => {
    localStorage.removeItem('userInfo');
    sessionStorage.removeItem('userInfo');
    userStore.resetInfo();
    Message.success('存储已清除');
  };

  onMounted(() => {
    console.log('=== Debug Info Component Mounted ===');
    console.log('UserStore state:', {
      accountId: userStore.accountId,
      name: userStore.name,
      email: userStore.email,
      phone: userStore.phone,
      role: userStore.role,
    });
    console.log('LocalStorage userInfo:', localStorage.getItem('userInfo'));
    console.log('SessionStorage userInfo:', sessionStorage.getItem('userInfo'));
    console.log('Token:', getToken());
  });
</script>

<style scoped lang="less">
  .debug-card {
    margin-bottom: 24px;
    border: 2px dashed rgb(var(--warning-6));
    
    pre {
      font-size: 12px;
      max-height: 200px;
      overflow: auto;
      background: var(--color-fill-2);
      padding: 8px;
      border-radius: 4px;
    }
  }
</style>

