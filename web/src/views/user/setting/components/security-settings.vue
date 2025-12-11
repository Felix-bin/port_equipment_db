<template>
  <div class="security-settings">
    <a-card :bordered="false" class="security-card">
      <template #title>
        <div class="card-title">
          <icon-lock />
          <span>{{ $t('userSetting.SecuritySettings.form.label.password') }}</span>
        </div>
      </template>
      
      <a-form
        v-if="showPasswordForm"
        ref="passwordFormRef"
        :model="passwordForm"
        :label-col-props="{ span: 6 }"
        :wrapper-col-props="{ span: 18 }"
        class="password-form"
      >
        <a-form-item
          field="oldPassword"
          :label="$t('userSetting.SecuritySettings.form.label.oldPassword')"
          :rules="[
            {
              required: true,
              message: $t('userSetting.form.error.oldPassword.required'),
            },
          ]"
        >
          <a-input-password
            v-model="passwordForm.oldPassword"
            :placeholder="$t('userSetting.SecuritySettings.placeholder.oldPassword')"
            allow-clear
          />
        </a-form-item>

        <a-form-item
          field="newPassword"
          :label="$t('userSetting.SecuritySettings.form.label.newPassword')"
          :rules="[
            {
              required: true,
              message: $t('userSetting.form.error.newPassword.required'),
            },
            {
              minLength: 6,
              message: $t('userSetting.form.error.newPassword.minLength'),
            },
          ]"
        >
          <a-input-password
            v-model="passwordForm.newPassword"
            :placeholder="$t('userSetting.SecuritySettings.placeholder.newPassword')"
            allow-clear
          />
        </a-form-item>

        <a-form-item
          field="confirmPassword"
          :label="$t('userSetting.SecuritySettings.form.label.confirmPassword')"
          :rules="[
            {
              required: true,
              message: $t('userSetting.form.error.confirmPassword.required'),
            },
            {
              validator: (value, cb) => {
                if (value !== passwordForm.newPassword) {
                  cb($t('userSetting.form.error.confirmPassword.notMatch'));
                } else {
                  cb();
                }
              },
            },
          ]"
        >
          <a-input-password
            v-model="passwordForm.confirmPassword"
            :placeholder="$t('userSetting.SecuritySettings.placeholder.confirmPassword')"
            allow-clear
          />
        </a-form-item>

        <a-form-item>
          <a-space>
            <a-button type="primary" @click="handleUpdatePassword" :loading="loading">
              {{ $t('userSetting.save') }}
            </a-button>
            <a-button @click="showPasswordForm = false">
              {{ $t('userSetting.cancel') }}
            </a-button>
          </a-space>
        </a-form-item>
      </a-form>

      <div v-else class="security-item-content">
        <div class="item-description">
          <icon-check-circle-fill class="status-icon success" />
          <span>{{ $t('userSetting.SecuritySettings.placeholder.password') }}</span>
        </div>
        <a-button type="text" @click="showPasswordForm = true">
          {{ $t('userSetting.SecuritySettings.button.update') }}
        </a-button>
      </div>
    </a-card>

    <a-card :bordered="false" class="security-card">
      <template #title>
        <div class="card-title">
          <icon-phone />
          <span>{{ $t('userSetting.SecuritySettings.form.label.phone') }}</span>
        </div>
      </template>
      
      <div class="security-item-content">
        <div class="item-description">
          <icon-check-circle-fill v-if="userInfo.phone" class="status-icon success" />
          <icon-exclamation-circle-fill v-else class="status-icon warning" />
          <span v-if="userInfo.phone">
            {{ $t('userSetting.SecuritySettings.label.bound') }}：{{ maskPhone(userInfo.phone) }}
          </span>
          <span v-else class="tip">
            {{ $t('userSetting.SecuritySettings.placeholder.phoneNotSet') }}
          </span>
        </div>
        <a-button type="text" disabled>
          {{ $t('userSetting.SecuritySettings.button.update') }}
        </a-button>
      </div>
    </a-card>

    <a-card :bordered="false" class="security-card">
      <template #title>
        <div class="card-title">
          <icon-email />
          <span>{{ $t('userSetting.SecuritySettings.form.label.email') }}</span>
        </div>
      </template>
      
      <div class="security-item-content">
        <div class="item-description">
          <icon-check-circle-fill v-if="userInfo.email" class="status-icon success" />
          <icon-exclamation-circle-fill v-else class="status-icon warning" />
          <span v-if="userInfo.email">
            {{ $t('userSetting.SecuritySettings.label.bound') }}：{{ maskEmail(userInfo.email) }}
          </span>
          <span v-else class="tip">
            {{ $t('userSetting.SecuritySettings.placeholder.email') }}
          </span>
        </div>
        <a-button type="text" disabled>
          {{ $t('userSetting.SecuritySettings.button.update') }}
        </a-button>
      </div>
    </a-card>
  </div>
</template>

<script lang="ts" setup>
  import { ref, onMounted } from 'vue';
  import { FormInstance } from '@arco-design/web-vue/es/form';
  import { Message } from '@arco-design/web-vue';
  import { getUserInfo } from '@/api/user-center';
  import { useUserStore } from '@/store';

  const userStore = useUserStore();
  const passwordFormRef = ref<FormInstance>();
  const loading = ref(false);
  const showPasswordForm = ref(false);
  
  const userInfo = ref({
    phone: '',
    email: '',
  });

  const passwordForm = ref({
    oldPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  // 手机号脱敏
  const maskPhone = (phone: string) => {
    if (!phone || phone.length < 11) return phone;
    return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2');
  };

  // 邮箱脱敏
  const maskEmail = (email: string) => {
    if (!email) return email;
    const [username, domain] = email.split('@');
    if (!username || !domain) return email;
    
    const visibleChars = Math.min(3, Math.floor(username.length / 2));
    const maskedUsername = username.substring(0, visibleChars) + '***';
    return `${maskedUsername}@${domain}`;
  };

  // 加载用户信息
  const loadUserInfo = async () => {
    if (!userStore.accountId) return;
    
    try {
      const userId = parseInt(userStore.accountId);
      const response = await getUserInfo(userId);
      const userData = response?.data || response;
      
      userInfo.value = {
        phone: userData.phone || '',
        email: userData.email || '',
      };
    } catch (err) {
      console.error('获取用户信息失败:', err);
    }
  };

  // 修改密码
  const handleUpdatePassword = async () => {
    const res = await passwordFormRef.value?.validate();
    if (res) return;

    if (!userStore.accountId) {
      Message.warning('请先登录');
      return;
    }

    loading.value = true;
    try {
      // TODO: 调用修改密码的API
      // await updatePassword(userStore.accountId, passwordForm.value);
      
      Message.success('密码修改成功，请重新登录');
      showPasswordForm.value = false;
      
      // 重置表单
      passwordFormRef.value?.resetFields();
      passwordForm.value = {
        oldPassword: '',
        newPassword: '',
        confirmPassword: '',
      };
      
      // TODO: 退出登录，跳转到登录页
    } catch (err) {
      console.error('修改密码失败:', err);
      Message.error('修改密码失败');
    } finally {
      loading.value = false;
    }
  };

  onMounted(() => {
    loadUserInfo();
  });
</script>

<style scoped lang="less">
  .security-settings {
    max-width: 800px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .security-card {
    border-radius: 8px;
    border: 1px solid var(--color-neutral-3);
    
    .card-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 600;
      font-size: 16px;
      color: rgb(var(--gray-10));
    }
  }

  .security-item-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    
    .item-description {
      flex: 1;
      display: flex;
      align-items: center;
      gap: 8px;
      
      .status-icon {
        font-size: 18px;
        
        &.success {
          color: rgb(var(--success-6));
        }
        
        &.warning {
          color: rgb(var(--warning-6));
        }
      }
      
      .tip {
        color: rgb(var(--gray-6));
      }
    }
  }

  .password-form {
    max-width: 600px;
    margin-top: 16px;
    
    :deep(.arco-form-item-label) {
      font-weight: 500;
    }
  }

  @media (max-width: 768px) {
    .security-settings {
      max-width: 100%;
    }
    
    .security-item-content {
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;
    }
  }
</style>
