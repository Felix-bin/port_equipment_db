<template>
  <div class="navbar">
    <div class="left-side">
      <a-space>
        <img alt="logo" :src="logoUrl" style="width: 32px; height: 32px" />
        <a-typography-title
          class="system-title"
          :style="{ margin: 0 }"
          :heading="5"
        >
          装备租赁管理系统
        </a-typography-title>
        <icon-menu-fold
          v-if="!topMenu && appStore.device === 'mobile'"
          style="font-size: 22px; cursor: pointer"
          @click="toggleDrawerMenu"
        />
      </a-space>
    </div>
    <div class="center-side">
      <Menu v-if="topMenu" />
    </div>
    <ul class="right-side">
      <!-- 语言切换 -->
      <li>
        <a-tooltip :content="$t('settings.language')">
          <a-button
            class="nav-btn"
            type="outline"
            :shape="'circle'"
            @click="setDropDownVisible"
          >
            <template #icon>
              <icon-language />
            </template>
          </a-button>
        </a-tooltip>
        <a-dropdown trigger="click" @select="changeLocale as any">
          <div ref="triggerBtn" class="trigger-btn"></div>
          <template #content>
            <a-doption
              v-for="item in locales"
              :key="item.value"
              :value="item.value"
            >
              <template #icon>
                <icon-check v-show="item.value === currentLocale" />
              </template>
              {{ item.label }}
            </a-doption>
          </template>
        </a-dropdown>
      </li>
      
      <!-- 主题切换 -->
      <li>
        <a-tooltip
          :content="
            theme === 'light'
              ? $t('settings.navbar.theme.toDark')
              : $t('settings.navbar.theme.toLight')
          "
        >
          <a-button
            class="nav-btn"
            type="outline"
            :shape="'circle'"
            @click="handleToggleTheme"
          >
            <template #icon>
              <icon-moon-fill v-if="theme === 'dark'" />
              <icon-sun-fill v-else />
            </template>
          </a-button>
        </a-tooltip>
      </li>
      
      <!-- 全屏 -->
      <li>
        <a-tooltip
          :content="
            isFullscreen
              ? $t('settings.navbar.screen.toExit')
              : $t('settings.navbar.screen.toFull')
          "
        >
          <a-button
            class="nav-btn"
            type="outline"
            :shape="'circle'"
            @click="toggleFullScreen"
          >
            <template #icon>
              <icon-fullscreen-exit v-if="isFullscreen" />
              <icon-fullscreen v-else />
            </template>
          </a-button>
        </a-tooltip>
      </li>

      <!-- 用户信息 -->
      <li class="user-info">
        <span class="user-name">{{ userName }}</span>
        <span class="user-role-tag">{{ userRoleLabel }}</span>
      </li>
      
      <!-- 用户头像 -->
      <li>
        <a-dropdown trigger="click">
          <a-avatar
            :size="36"
            :style="{ cursor: 'pointer' }"
            class="user-avatar"
          >
            <img v-if="avatarUrl" alt="avatar" :src="avatarUrl" />
            <icon-user v-else />
          </a-avatar>
          <template #content>
            <a-doption @click="$router.push({ name: 'Setting' })">
              <a-space>
                <icon-settings />
                <span>{{ $t('messageBox.userSettings') }}</span>
              </a-space>
            </a-doption>
            <a-doption @click="handleLogout">
              <a-space>
                <icon-export />
                <span>{{ $t('messageBox.logout') }}</span>
              </a-space>
            </a-doption>
          </template>
        </a-dropdown>
      </li>
    </ul>
  </div>
</template>

<script lang="ts" setup>
  import { computed, inject, onMounted, ref } from 'vue';
  import { useDark, useToggle, useFullscreen } from '@vueuse/core';
  import { useAppStore, useUserStore } from '@/store';
  import { LOCALE_OPTIONS } from '@/locale';
  import useLocale from '@/hooks/locale';
  import useUser from '@/hooks/user';
  import Menu from '@/components/menu/index.vue';
  import logoUrl from '@/assets/logo.svg?url';
  import { getAvatarUrl } from '@/utils/image';
  import { getUserInfo } from '@/api/user-center';

  const appStore = useAppStore();
  const userStore = useUserStore();
  const { logout } = useUser();
  const { changeLocale, currentLocale } = useLocale();
  const { isFullscreen, toggle: toggleFullScreen } = useFullscreen();
  const locales = [...LOCALE_OPTIONS];
  
  const topMenu = computed(() => appStore.topMenu && appStore.menu);
  const toggleDrawerMenu = inject('toggleDrawerMenu') as () => void;

  // 主题相关
  const theme = computed(() => appStore.theme);
  const isDark = useDark({
    selector: 'body',
    attribute: 'arco-theme',
    valueDark: 'dark',
    valueLight: 'light',
    storageKey: 'arco-theme',
    onChanged(dark: boolean) {
      appStore.toggleTheme(dark);
    },
  });
  const toggleTheme = useToggle(isDark);
  const handleToggleTheme = () => {
    toggleTheme();
  };

  // 语言切换触发
  const triggerBtn = ref();
  const setDropDownVisible = () => {
    const event = new MouseEvent('click', {
      view: window,
      bubbles: true,
      cancelable: true,
    });
    triggerBtn.value.dispatchEvent(event);
  };

  // 用户信息
  const userName = computed(() => userStore.name || '未登录');
  const avatarUrl = computed(() => getAvatarUrl(userStore.avatar));
  
  // 角色标签
  const userRoleLabel = computed(() => {
    const roleMap: Record<string, string> = {
      admin: '管理员',
      warehouse: '仓管员',
      finance: '财务',
      operator: '操作员',
    };
    return roleMap[userStore.role] || userStore.role || '';
  });

  // 处理退出登录
  const handleLogout = () => {
    logout();
  };

  // 加载用户完整信息（包括头像）
  const loadUserInfo = async () => {
    if (userStore.accountId) {
      try {
        const userId = parseInt(userStore.accountId);
        const response = await getUserInfo(userId);
        const userData = response?.data || response;
        
        // 更新store中的头像
        if (userData.avatar) {
          userStore.setInfo({ avatar: userData.avatar });
        }
      } catch (err) {
        console.error('获取用户头像失败:', err);
      }
    }
  };

  onMounted(() => {
    loadUserInfo();
  });
</script>

<style scoped lang="less">
  .navbar {
    display: flex;
    justify-content: space-between;
    height: 100%;
    background-color: var(--color-bg-2);
    border-bottom: 1px solid var(--color-border);
  }

  .left-side {
    display: flex;
    align-items: center;
    padding-left: 20px;
  }

  .system-title {
    font-size: 18px;
    font-weight: 600;
    letter-spacing: 0.8px;
    color: #165dff;
    background: linear-gradient(135deg, #165dff 0%, #0d3f66 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-left: 8px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC',
      'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial,
      sans-serif;
    transition: all 0.3s ease;

    // Fallback for browsers that don't support background-clip
    @supports not (-webkit-background-clip: text) {
      color: #165dff;
      background: none;
      -webkit-text-fill-color: #165dff;
    }
  }

  .center-side {
    flex: 1;
  }

  .right-side {
    display: flex;
    align-items: center;
    padding-right: 20px;
    list-style: none;
    
    li {
      display: flex;
      align-items: center;
      padding: 0 10px;
    }

    .nav-btn {
      border-color: rgb(var(--gray-2));
      color: rgb(var(--gray-8));
      font-size: 16px;
    }

    .trigger-btn {
      position: absolute;
      bottom: 14px;
      margin-left: 14px;
    }

    .user-info {
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      padding-right: 12px;
      padding-left: 12px;
      margin-left: 8px;
      border-left: 1px solid var(--color-border-2);
      
      .user-name {
        font-size: 14px;
        font-weight: 500;
        color: var(--color-text-1);
        margin-bottom: 2px;
      }
      
      .user-role-tag {
        font-size: 12px;
        color: var(--color-text-3);
        background: var(--color-fill-2);
        padding: 2px 8px;
        border-radius: 10px;
      }
    }

    .user-avatar {
      border: 2px solid var(--color-border-2);
      transition: all 0.3s ease;
      
      &:hover {
        border-color: rgb(var(--primary-6));
        box-shadow: 0 2px 8px rgba(22, 93, 255, 0.15);
      }
    }

    a {
      color: var(--color-text-1);
      text-decoration: none;
    }
  }
</style>

<style lang="less">
  .message-popover {
    .arco-popover-content {
      margin-top: 0;
    }
  }
</style>
