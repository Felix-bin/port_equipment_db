<template>
  <a-card :bordered="false" class="user-panel-card">
    <a-spin :loading="loading" style="width: 100%">
      <div class="user-panel">
        <div class="user-avatar-section">
          <div class="avatar-wrapper">
            <a-avatar :size="100" class="user-avatar">
              <img v-if="userInfo.avatar" :src="getAvatarUrl(userInfo.avatar)" alt="avatar" />
              <icon-user v-else />
            </a-avatar>
            <a-upload
              :custom-request="handleUploadAvatar"
              :show-file-list="false"
              accept="image/*"
            >
              <template #upload-button>
                <a-button type="text" class="upload-btn">
                  <icon-camera />
                  {{ $t('userSetting.label.uploadAvatar') }}
                </a-button>
              </template>
            </a-upload>
          </div>
        </div>

        <div class="user-info-section">
          <div class="info-row">
            <div class="info-label">{{ $t('userSetting.label.username') }}：</div>
            <div class="info-value">{{ userInfo.username || '-' }}</div>
          </div>
          <div class="info-row">
            <div class="info-label">{{ $t('userSetting.label.realName') }}：</div>
            <div class="info-value">{{ userInfo.real_name || '-' }}</div>
          </div>
          <div class="info-row">
            <div class="info-label">{{ $t('userSetting.label.role') }}：</div>
            <div class="info-value">
              <a-tag :color="getRoleColor(userInfo.role)">
                {{ getRoleLabel(userInfo.role) }}
              </a-tag>
            </div>
          </div>
          <div class="info-row">
            <div class="info-label">{{ $t('userSetting.label.status') }}：</div>
            <div class="info-value">
              <a-tag :color="userInfo.status === 'active' ? 'green' : 'red'">
                {{ userInfo.status === 'active' ? $t('userSetting.status.active') : $t('userSetting.status.inactive') }}
              </a-tag>
            </div>
          </div>
          <div class="info-row">
            <div class="info-label">{{ $t('userSetting.label.email') }}：</div>
            <div class="info-value">{{ userInfo.email || '-' }}</div>
          </div>
          <div class="info-row">
            <div class="info-label">{{ $t('userSetting.label.phone') }}：</div>
            <div class="info-value">{{ userInfo.phone || '-' }}</div>
          </div>
        </div>
      </div>
    </a-spin>
  </a-card>
</template>

<script lang="ts" setup>
  import { ref, onMounted } from 'vue';
  import { Message } from '@arco-design/web-vue';
  import { useUserStore } from '@/store';
  import { getUserInfo, userUploadApi } from '@/api/user-center';
  import { getAvatarUrl } from '@/utils/image';

  const userStore = useUserStore();
  const loading = ref(false);
  
  const userInfo = ref({
    username: '',
    real_name: '',
    role: '',
    status: '',
    email: '',
    phone: '',
    avatar: '',
    nickname: '',
  });

  // 获取角色颜色
  const getRoleColor = (role: string) => {
    const colorMap: Record<string, string> = {
      admin: 'red',
      warehouse: 'blue',
      finance: 'green',
      operator: 'orange',
    };
    return colorMap[role] || 'gray';
  };

  // 获取角色标签
  const getRoleLabel = (role: string) => {
    const labelMap: Record<string, string> = {
      admin: '管理员',
      warehouse: '仓管员',
      finance: '财务',
      operator: '操作员',
    };
    return labelMap[role] || role;
  };

  // 加载用户信息
  const loadUserInfo = async () => {
    if (!userStore.accountId) {
      Message.warning('未获取到用户ID，请重新登录');
      return;
    }
    
    loading.value = true;
    try {
      const userId = parseInt(userStore.accountId);
      const response = await getUserInfo(userId);
      const userData = response?.data || response;
      
      userInfo.value = {
        username: userData.username || '',
        real_name: userData.real_name || '',
        role: userData.role || '',
        status: userData.status || '',
        email: userData.email || '',
        phone: userData.phone || '',
        avatar: userData.avatar || '',
        nickname: userData.nickname || '',
      };
    } catch (err) {
      console.error('加载用户信息失败:', err);
      Message.error('加载用户信息失败: ' + (err.response?.data?.detail || err.message));
    } finally {
      loading.value = false;
    }
  };

  // 上传头像
  const handleUploadAvatar = async (options: any) => {
    const { fileItem, onSuccess, onError } = options;
    
    if (!userStore.accountId) {
      Message.warning('请先登录');
      onError();
      return;
    }

    try {
      const formData = new FormData();
      formData.append('file', fileItem.file);
      formData.append('user_id', userStore.accountId);
      
      const response = await userUploadApi(formData);
      const result = response?.data || response;
      
      // 后端返回格式: { code: 200, message: "上传成功", data: { url: "/uploads/avatars/xxx.jpg" } }
      if (result.data?.url || result.url) {
        const avatarUrl = result.data?.url || result.url;
        userInfo.value.avatar = avatarUrl;
        Message.success('头像上传成功');
        onSuccess();
        
        // 刷新用户信息
        await loadUserInfo();
      } else {
        throw new Error('上传失败');
      }
    } catch (err) {
      console.error('上传头像失败:', err);
      Message.error('上传头像失败');
      onError();
    }
  };
  
  // 页面加载时获取用户信息
  onMounted(() => {
    loadUserInfo();
  });
</script>

<style scoped lang="less">
  .user-panel-card {
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    transition: box-shadow 0.3s ease;
    
    &:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
    }
  }

  .user-panel {
    display: flex;
    gap: 40px;
    padding: 24px;
    
    @media (max-width: 768px) {
      flex-direction: column;
      gap: 24px;
    }
  }

  .user-avatar-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    
    .avatar-wrapper {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 12px;
      
      .user-avatar {
        background: linear-gradient(135deg, rgb(var(--primary-6)), rgb(var(--primary-4)));
        font-size: 40px;
        
        img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
      }
      
      .upload-btn {
        font-size: 12px;
        color: rgb(var(--primary-6));
        
        &:hover {
          background: var(--color-fill-2);
        }
      }
    }
  }

  .user-info-section {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 16px;
    
    .info-row {
      display: flex;
      align-items: center;
      
      .info-label {
        min-width: 100px;
        font-weight: 500;
        color: rgb(var(--gray-7));
      }
      
      .info-value {
        flex: 1;
        color: rgb(var(--gray-10));
      }
    }
  }
</style>
