<template>
  <a-spin :loading="loading" style="width: 100%">
    <a-form
      ref="formRef"
      :model="formData"
      class="form"
      :label-col-props="{ span: 8 }"
      :wrapper-col-props="{ span: 16 }"
    >
    <a-form-item
      field="email"
      :label="$t('userSetting.basicInfo.form.label.email')"
      :rules="[
        {
          required: true,
          message: $t('userSetting.form.error.email.required'),
        },
      ]"
    >
      <a-input
        v-model="formData.email"
        :placeholder="$t('userSetting.basicInfo.placeholder.email')"
      />
    </a-form-item>
    <a-form-item
      field="nickname"
      :label="$t('userSetting.basicInfo.form.label.nickname')"
      :rules="[
        {
          required: true,
          message: $t('userSetting.form.error.nickname.required'),
        },
      ]"
    >
      <a-input
        v-model="formData.nickname"
        :placeholder="$t('userSetting.basicInfo.placeholder.nickname')"
      />
    </a-form-item>
    <a-form-item
      field="countryRegion"
      :label="$t('userSetting.basicInfo.form.label.countryRegion')"
      :rules="[
        {
          required: true,
          message: $t('userSetting.form.error.countryRegion.required'),
        },
      ]"
    >
      <a-select
        v-model="formData.countryRegion"
        :placeholder="$t('userSetting.basicInfo.placeholder.area')"
      >
        <a-option value="China">中国</a-option>
      </a-select>
    </a-form-item>
    <a-form-item
      field="area"
      :label="$t('userSetting.basicInfo.form.label.area')"
      :rules="[
        {
          required: true,
          message: $t('userSetting.form.error.area.required'),
        },
      ]"
    >
      <a-cascader
        v-model="formData.area"
        :placeholder="$t('userSetting.basicInfo.placeholder.area')"
        :options="[
          {
            label: '北京',
            value: 'beijing',
            children: [
              {
                label: '北京',
                value: 'beijing',
                children: [
                  {
                    label: '朝阳',
                    value: 'chaoyang',
                  },
                ],
              },
            ],
          },
        ]"
        allow-clear
      />
    </a-form-item>
    <a-form-item
      field="address"
      :label="$t('userSetting.basicInfo.form.label.address')"
    >
      <a-input
        v-model="formData.address"
        :placeholder="$t('userSetting.basicInfo.placeholder.address')"
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
      row-class="keep-margin"
    >
      <a-textarea
        v-model="formData.profile"
        :placeholder="$t('userSetting.basicInfo.placeholder.profile')"
      />
    </a-form-item>
    <a-form-item>
      <a-space>
        <a-button type="primary" @click="validate">
          {{ $t('userSetting.save') }}
        </a-button>
        <a-button type="secondary" @click="reset">
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
  import { BasicInfoModel, getUserInfo, saveUserInfo } from '@/api/user-center';
  import { useUserStore } from '@/store';

  const userStore = useUserStore();
  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const formData = ref<BasicInfoModel>({
    email: '',
    nickname: '',
    countryRegion: '',
    area: '',
    address: '',
    profile: '',
  });

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
      
      // 映射后端数据到表单
      formData.value = {
        email: userData.email || '',
        nickname: userData.real_name || userData.nickname || '',
        countryRegion: userData.country_region || userData.countryRegion || '',
        area: userData.area || '',
        address: userData.address || '',
        profile: userData.profile || '',
      };
    } catch (err) {
      console.error('获取用户信息失败:', err);
      Message.error('获取用户信息失败');
    } finally {
      loading.value = false;
    }
  };

  const validate = async () => {
    const res = await formRef.value?.validate();
    if (!res) {
      if (!userStore.accountId) {
        Message.warning('请先登录');
        return;
      }

      loading.value = true;
      try {
        const userId = parseInt(userStore.accountId);
        // 映射表单数据到后端格式
        const updateData = {
          email: formData.value.email,
          real_name: formData.value.nickname,
          nickname: formData.value.nickname,
          country_region: formData.value.countryRegion,
          area: formData.value.area,
          address: formData.value.address,
          profile: formData.value.profile,
        };
        
        await saveUserInfo(userId, updateData as any);
        Message.success('保存成功');
        
        // 更新store中的用户信息
        userStore.setInfo({
          email: formData.value.email,
          name: formData.value.nickname,
        });
      } catch (err) {
        console.error('保存用户信息失败:', err);
        Message.error('保存失败');
      } finally {
        loading.value = false;
      }
    }
  };

  const reset = async () => {
    await formRef.value?.resetFields();
    await loadUserInfo();
  };

  onMounted(() => {
    loadUserInfo();
  });
</script>

<style scoped lang="less">
  .form {
    width: 540px;
    margin: 0 auto;
  }
</style>
