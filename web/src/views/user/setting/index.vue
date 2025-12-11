<template>
  <div class="container">
    <Breadcrumb :items="['menu.user', 'menu.user.setting']" />
    
    <!-- 调试信息组件 - 开发时显示 -->
    <DebugInfo v-if="isDevelopment" />
    
    <div class="content-wrapper">
      <div class="user-panel-wrapper">
        <UserPanel />
      </div>
      <div class="tabs-wrapper">
        <a-tabs default-active-key="1" type="rounded" class="setting-tabs">
          <a-tab-pane key="1" :title="$t('userSetting.tab.basicInformation')">
            <div class="tab-content">
              <BasicInformation />
            </div>
          </a-tab-pane>
          <a-tab-pane key="2" :title="$t('userSetting.tab.accountInfo')">
            <div class="tab-content">
              <AccountInfo />
            </div>
          </a-tab-pane>
          <a-tab-pane key="3" :title="$t('userSetting.tab.securitySettings')">
            <div class="tab-content">
              <SecuritySettings />
            </div>
          </a-tab-pane>
        </a-tabs>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import UserPanel from './components/user-panel.vue';
  import BasicInformation from './components/basic-information.vue';
  import AccountInfo from './components/account-info.vue';
  import SecuritySettings from './components/security-settings.vue';
  import DebugInfo from './components/debug-info.vue';

  // 根据环境变量判断是否显示调试信息（设为 false 以隐藏调试信息）
  const isDevelopment = ref(false);
</script>

<script lang="ts">
  export default {
    name: 'Setting',
  };
</script>

<style scoped lang="less">
  .container {
    padding: 0 24px 24px 24px;
    max-width: 1400px;
    margin: 0 auto;
  }

  .content-wrapper {
    display: flex;
    flex-direction: column;
    gap: 24px;
    margin-top: 16px;
  }

  .user-panel-wrapper {
    width: 100%;
  }

  .tabs-wrapper {
    background-color: var(--color-bg-2);
    border-radius: 8px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    min-height: 500px;
  }

  .setting-tabs {
    :deep(.arco-tabs-nav) {
      margin-bottom: 24px;
      padding: 0 4px;
    }

    :deep(.arco-tabs-content) {
      padding-top: 0;
    }
  }

  .tab-content {
    padding: 8px 0;
  }

  :deep(.section-title) {
    margin-top: 0;
    margin-bottom: 16px;
    font-size: 14px;
    font-weight: 600;
    color: rgb(var(--gray-10));
  }

  @media (max-width: 768px) {
    .container {
      padding: 0 16px 16px 16px;
    }

    .tabs-wrapper {
      padding: 16px;
    }
  }
</style>
