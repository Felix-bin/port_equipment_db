<template>
  <a-card :bordered="false">
    <a-space :size="54">
      <a-upload
        :custom-request="customRequest"
        list-type="picture-card"
        :file-list="fileList"
        :show-upload-button="true"
        :show-file-list="false"
        @change="uploadChange"
      >
        <template #upload-button>
          <a-avatar :size="100" class="info-avatar">
            <template #trigger-icon>
              <icon-camera />
            </template>
            <img v-if="fileList.length" :src="fileList[0].url" />
          </a-avatar>
        </template>
      </a-upload>
      <a-descriptions
        :data="renderData"
        :column="2"
        align="right"
        layout="inline-horizontal"
        :label-style="{
          width: '140px',
          fontWeight: 'normal',
          color: 'rgb(var(--gray-8))',
        }"
        :value-style="{
          width: '200px',
          paddingLeft: '8px',
          textAlign: 'left',
        }"
      >
        <template #label="{ label }">{{ $t(label) }} :</template>
        <template #value="{ value }">
          <span>{{ value }}</span>
        </template>
      </a-descriptions>
    </a-space>
  </a-card>
</template>

<script lang="ts" setup>
  import { ref, onMounted, computed } from 'vue';
  import type {
    FileItem,
    RequestOption,
  } from '@arco-design/web-vue/es/upload/interfaces';
  import { useUserStore } from '@/store';
  import { userUploadApi, getUserInfo } from '@/api/user-center';
  import type { DescData } from '@arco-design/web-vue/es/descriptions/interface';

  const userStore = useUserStore();
  
  // 动态计算头像URL
  const avatarUrl = computed(() => {
    if (userStore.avatar) {
      // 如果是相对路径，添加后端地址
      if (userStore.avatar.startsWith('/uploads')) {
        return `http://127.0.0.1:8000${userStore.avatar}`;
      }
      return userStore.avatar;
    }
    return '';
  });
  
  const file = computed(() => ({
    uid: '-2',
    name: 'avatar.png',
    url: avatarUrl.value,
  }));
  
  const renderData = computed(() => [
    {
      label: 'userSetting.label.name',
      value: userStore.name,
    },
    {
      label: 'userSetting.label.accountId',
      value: userStore.accountId,
    },
    {
      label: 'userSetting.label.phone',
      value: userStore.phone,
    },
    {
      label: 'userSetting.label.registrationDate',
      value: userStore.registrationDate,
    },
  ] as DescData[]);
  
  const fileList = ref<FileItem[]>([file.value]);
  
  // 加载用户信息（包括头像）
  const loadUserInfo = async () => {
    if (!userStore.accountId) return;
    
    try {
      const userId = parseInt(userStore.accountId);
      const response = await getUserInfo(userId);
      const userData = response?.data || response;
      
      // 更新头像
      if (userData.avatar) {
        userStore.setInfo({ avatar: userData.avatar });
        // 更新文件列表
        fileList.value = [{
          uid: '-2',
          name: 'avatar.png',
          url: avatarUrl.value,
        }];
      }
    } catch (err) {
      console.error('加载用户信息失败:', err);
    }
  };
  const uploadChange = (fileItemList: FileItem[], fileItem: FileItem) => {
    fileList.value = [fileItem];
  };
  
  const customRequest = (options: RequestOption) => {
    (async function requestWrap() {
      const {
        onProgress,
        onError,
        onSuccess,
        fileItem,
        name = 'file',
      } = options;
      
      try {
        // 验证用户ID
        const userId = userStore.accountId ? parseInt(userStore.accountId) : undefined;
        if (!userId) {
          throw new Error('用户ID不存在，请先登录');
        }

        onProgress(10);
        
        // 构建 FormData
        const formData = new FormData();
        formData.append(name as string, fileItem.file as Blob);
        formData.append('user_id', userId.toString());
        
        onProgress(20);
        
        // 调用上传API（不使用 onUploadProgress 以避免错误）
        const res = await userUploadApi(formData);
        
        onProgress(80);
        
        // 更新store中的头像
        const avatarUrl = res?.data?.data?.url || res?.data?.url;
        if (avatarUrl) {
          // 构建完整URL
          const fullAvatarUrl = avatarUrl.startsWith('/uploads') 
            ? `http://127.0.0.1:8000${avatarUrl}` 
            : avatarUrl;
          
          userStore.setInfo({ avatar: avatarUrl }); // 保存相对路径到store
          
          // 更新文件列表中的URL（使用完整URL显示）
          fileList.value = [{
            uid: '-2',
            name: 'avatar.png',
            url: fullAvatarUrl,
          }];
        }
        
        onProgress(100);
        onSuccess(res);
      } catch (error: any) {
        console.error('头像上传失败:', error);
        onError(error);
      }
    })();
    
    return {
      abort() {
        // 简化的 abort 实现
      },
    };
  };
  
  // 页面加载时获取用户信息
  onMounted(() => {
    loadUserInfo();
  });
</script>

<style scoped lang="less">
  .arco-card {
    padding: 14px 0 4px 4px;
    border-radius: 4px;
  }
  :deep(.arco-avatar-trigger-icon-button) {
    width: 32px;
    height: 32px;
    line-height: 32px;
    background-color: #e8f3ff;
    .arco-icon-camera {
      margin-top: 8px;
      color: rgb(var(--arcoblue-6));
      font-size: 14px;
    }
  }
</style>
