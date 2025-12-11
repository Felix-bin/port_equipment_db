<template>
  <a-spin :loading="loading" style="width: 100%">
    <a-form
      ref="formRef"
      :model="formData"
      class="form"
      :label-col-props="{ span: 6 }"
      :wrapper-col-props="{ span: 18 }"
    >
      <a-form-item
        field="real_name"
        :label="$t('userSetting.basicInfo.form.label.realName')"
      >
        <a-input
          v-model="formData.real_name"
          :placeholder="$t('userSetting.basicInfo.placeholder.realName')"
          allow-clear
        />
      </a-form-item>
      
      <a-form-item
        field="nickname"
        :label="$t('userSetting.basicInfo.form.label.nickname')"
      >
        <a-input
          v-model="formData.nickname"
          :placeholder="$t('userSetting.basicInfo.placeholder.nickname')"
          allow-clear
        />
      </a-form-item>

      <a-form-item
        field="phone"
        :label="$t('userSetting.basicInfo.form.label.phone')"
        :rules="[
          {
            match: /^1[3-9]\d{9}$/,
            message: $t('userSetting.form.error.phone.format'),
          },
        ]"
      >
        <a-input
          v-model="formData.phone"
          :placeholder="$t('userSetting.basicInfo.placeholder.phone')"
          allow-clear
        />
      </a-form-item>

      <a-form-item
        field="email"
        :label="$t('userSetting.basicInfo.form.label.email')"
        :rules="[
          {
            type: 'email',
            message: $t('userSetting.form.error.email.format'),
          },
        ]"
      >
        <a-input
          v-model="formData.email"
          :placeholder="$t('userSetting.basicInfo.placeholder.email')"
          allow-clear
        />
      </a-form-item>

      <a-form-item
        field="country_region"
        :label="$t('userSetting.basicInfo.form.label.countryRegion')"
      >
        <a-select
          v-model="formData.country_region"
          :placeholder="$t('userSetting.basicInfo.placeholder.countryRegion')"
          allow-clear
        >
          <a-option value="中国">中国</a-option>
          <a-option value="美国">美国</a-option>
          <a-option value="日本">日本</a-option>
          <a-option value="韩国">韩国</a-option>
          <a-option value="新加坡">新加坡</a-option>
          <a-option value="其他">其他</a-option>
        </a-select>
      </a-form-item>

      <a-form-item
        field="area"
        :label="$t('userSetting.basicInfo.form.label.area')"
      >
        <a-input
          v-model="formData.area"
          :placeholder="$t('userSetting.basicInfo.placeholder.area')"
          allow-clear
        />
      </a-form-item>

      <a-form-item
        field="address"
        :label="$t('userSetting.basicInfo.form.label.address')"
      >
        <a-textarea
          v-model="formData.address"
          :placeholder="$t('userSetting.basicInfo.placeholder.address')"
          :auto-size="{ minRows: 2, maxRows: 4 }"
          allow-clear
        />
      </a-form-item>

      <a-form-item
        field="profile"
        :label="$t('userSetting.basicInfo.form.label.profile')"
        :rules="[
          {
            maxLength: 200,
            message: $t('userSetting.form.error.profile.maxLength'),
          },
        ]"
      >
        <a-textarea
          v-model="formData.profile"
          :placeholder="$t('userSetting.basicInfo.placeholder.profile')"
          :auto-size="{ minRows: 3, maxRows: 6 }"
          :max-length="200"
          show-word-limit
          allow-clear
        />
      </a-form-item>

      <a-form-item>
        <a-space>
          <a-button type="primary" @click="handleSave">
            {{ $t('userSetting.save') }}
          </a-button>
          <a-button type="secondary" @click="handleReset">
            {{ $t('userSetting.reset') }}
          </a-button>
        </a-space>
      </a-form-item>
    </a-form>
  </a-spin>
</template>

<script lang="ts" setup>
  import { ref, onMounted } from 'vue';
  import { FormInstance } from '@arco-design/web-vue/es/form';
  import { Message } from '@arco-design/web-vue';
  import { getUserInfo, saveUserInfo } from '@/api/user-center';
  import { useUserStore } from '@/store';

  const userStore = useUserStore();
  const formRef = ref<FormInstance>();
  const loading = ref(false);
  
  const formData = ref({
    real_name: '',
    nickname: '',
    phone: '',
    email: '',
    country_region: '',
    area: '',
    address: '',
    profile: '',
  });

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
      
      formData.value = {
        real_name: userData.real_name || '',
        nickname: userData.nickname || '',
        phone: userData.phone || '',
        email: userData.email || '',
        country_region: userData.country_region || '',
        area: userData.area || '',
        address: userData.address || '',
        profile: userData.profile || '',
      };
    } catch (err) {
      console.error('获取用户信息失败:', err);
      Message.error('获取用户信息失败: ' + (err.response?.data?.detail || err.message));
    } finally {
      loading.value = false;
    }
  };

  // 保存用户信息
  const handleSave = async () => {
    const res = await formRef.value?.validate();
    if (res) return;

    if (!userStore.accountId) {
      Message.warning('请先登录');
      return;
    }

    loading.value = true;
    try {
      const userId = parseInt(userStore.accountId);
      await saveUserInfo(userId, formData.value as any);
      Message.success('保存成功');
      
      // 更新store中的用户信息
      userStore.setInfo({
        name: formData.value.real_name || formData.value.nickname,
        email: formData.value.email,
        phone: formData.value.phone,
      });
    } catch (err) {
      console.error('保存用户信息失败:', err);
      Message.error('保存失败');
    } finally {
      loading.value = false;
    }
  };

  // 重置表单
  const handleReset = async () => {
    await formRef.value?.resetFields();
    await loadUserInfo();
  };

  onMounted(() => {
    loadUserInfo();
  });
</script>

<style scoped lang="less">
  .form {
    max-width: 700px;
    margin: 0 auto;
    padding: 0 24px;
    
    :deep(.arco-form-item-label) {
      font-weight: 500;
      color: rgb(var(--gray-8));
    }
    
    @media (max-width: 768px) {
      padding: 0 16px;
      max-width: 100%;
    }
  }
</style>
