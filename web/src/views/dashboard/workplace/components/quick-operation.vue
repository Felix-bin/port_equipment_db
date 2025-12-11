<template>
  <a-card
    class="general-card"
    :title="$t('workplace.quick.operation')"
    :header-style="{ paddingBottom: '0' }"
    :body-style="{ padding: '24px 20px 0 20px' }"
  >
    <template #extra>
      <a-link>{{ $t('workplace.quickOperation.setup') }}</a-link>
    </template>
    <a-row :gutter="8">
      <a-col
        v-for="link in links"
        :key="link.text"
        :span="8"
        class="wrapper"
        @click="handleClick(link.route)"
      >
        <div class="icon">
          <component :is="link.icon" />
        </div>
        <a-typography-paragraph class="text">
          {{ $t(link.text) }}
        </a-typography-paragraph>
      </a-col>
    </a-row>
    <a-divider class="split-line" style="margin: 0" />
  </a-card>
</template>

<script lang="ts" setup>
  import { useRouter } from 'vue-router';

  const router = useRouter();

  const links = [
    {
      text: 'workplace.equipmentInbound',
      icon: 'icon-archive',
      route: '/equipment/inbound',
    },
    {
      text: 'workplace.inventoryQuery',
      icon: 'icon-storage',
      route: '/equipment/inventory',
    },
    {
      text: 'workplace.rentalApplication',
      icon: 'icon-file',
      route: '/rental/application',
    },
    {
      text: 'workplace.feeSettlement',
      icon: 'icon-bookmark',
      route: '/settlement/fee',
    },
    {
      text: 'workplace.equipmentOutbound',
      icon: 'icon-export',
      route: '/equipment/outbound',
    },
  ];

  const handleClick = (route: string) => {
    if (route) {
      router.push(route);
    }
  };
</script>

<style scoped lang="less">
  .wrapper {
    cursor: pointer;
    transition: all 0.3s ease;

    &:hover {
      transform: translateY(-2px);

      .icon {
        color: rgb(var(--arcoblue-6));
        background-color: #e8f3ff;
      }

      .text {
        color: rgb(var(--arcoblue-6));
      }
    }
  }
</style>
