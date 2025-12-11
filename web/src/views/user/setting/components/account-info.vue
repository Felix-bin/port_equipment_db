<template>
  <a-spin :loading="loading" style="width: 100%">
    <a-descriptions
      :data="accountData"
      :column="1"
      bordered
      size="large"
      class="account-descriptions"
      :label-style="{ width: '180px', fontWeight: 500 }"
    />
  </a-spin>
</template>

<script lang="ts" setup>
  import { ref, onMounted, computed } from 'vue';
  import { Message } from '@arco-design/web-vue';
  import { getUserInfo } from '@/api/user-center';
  import { useUserStore } from '@/store';
  import { useI18n } from 'vue-i18n';

  const userStore = useUserStore();
  const loading = ref(false);
  const { t } = useI18n();
  
  const userInfo = ref({
    user_id: '',
    username: '',
    role: '',
    status: '',
    created_at: '',
    updated_at: '',
    last_login: '',
  });

  // 获取角色标签
  const getRoleLabel = (role: string) => {
    const labelMap: Record<string, string> = {
      admin: t('userSetting.role.admin'),
      warehouse: t('userSetting.role.warehouse'),
      finance: t('userSetting.role.finance'),
      operator: t('userSetting.role.operator'),
    };
    return labelMap[role] || role;
  };

  // 获取状态标签
  const getStatusLabel = (status: string) => {
    return status === 'active' ? t('userSetting.status.active') : t('userSetting.status.inactive');
  };

  // 格式化日期
  const formatDate = (dateStr: string | Date | null | undefined): string => {
    if (!dateStr) return '-';
    
    try {
      const date = typeof dateStr === 'string' ? new Date(dateStr) : dateStr;
      if (isNaN(date.getTime())) return '-';
      
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      const seconds = String(date.getSeconds()).padStart(2, '0');
      
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    } catch (err) {
      console.error('日期格式化失败:', err);
      return '-';
    }
  };

  // 账户数据
  const accountData = computed(() => [
    {
      label: t('userSetting.accountInfo.label.userId'),
      value: userInfo.value.user_id || '-',
    },
    {
      label: t('userSetting.accountInfo.label.username'),
      value: userInfo.value.username || '-',
    },
    {
      label: t('userSetting.accountInfo.label.role'),
      value: getRoleLabel(userInfo.value.role),
    },
    {
      label: t('userSetting.accountInfo.label.status'),
      value: getStatusLabel(userInfo.value.status),
    },
    {
      label: t('userSetting.accountInfo.label.createdAt'),
      value: formatDate(userInfo.value.created_at),
    },
    {
      label: t('userSetting.accountInfo.label.updatedAt'),
      value: formatDate(userInfo.value.updated_at),
    },
    {
      label: t('userSetting.accountInfo.label.lastLogin'),
      value: formatDate(userInfo.value.last_login),
    },
  ]);

  // 加载用户信息
  const loadUserInfo = async () => {
    if (!userStore.accountId) {
      Message.warning('请先登录');
      return;
    }

    loading.value = true;
    try {
      const userId = parseInt(userStore.accountId);
      const response = await getUserInfo(userId);
      const userData = response?.data || response;
      
      userInfo.value = {
        user_id: userData.user_id?.toString() || '',
        username: userData.username || '',
        role: userData.role || '',
        status: userData.status || '',
        created_at: userData.created_at || '',
        updated_at: userData.updated_at || '',
        last_login: userData.last_login || '',
      };
    } catch (err) {
      console.error('获取用户信息失败:', err);
      Message.error('获取用户信息失败');
    } finally {
      loading.value = false;
    }
  };

  onMounted(() => {
    loadUserInfo();
  });
</script>

<style scoped lang="less">
  .account-descriptions {
    max-width: 800px;
    margin: 0 auto;
    
    :deep(.arco-descriptions-item-label) {
      background-color: var(--color-fill-2);
    }
    
    :deep(.arco-descriptions-item-value) {
      color: rgb(var(--gray-10));
    }
    
    @media (max-width: 768px) {
      max-width: 100%;
    }
  }
</style>

