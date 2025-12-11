<template>
  <a-card class="general-card" :title="$t('workplace.operationLog')">
    <template #extra>
      <a-link @click="viewAll">{{ $t('workplace.viewMore') }}</a-link>
    </template>
    <a-timeline>
      <a-timeline-item v-for="log in logs" :key="log.id" :label="log.time">
        <template #dot>
          <icon-check-circle-fill
            v-if="log.type === 'success'"
            :style="{ fontSize: '12px', color: '#00b42a' }"
          />
          <icon-info-circle-fill
            v-else-if="log.type === 'info'"
            :style="{ fontSize: '12px', color: '#165dff' }"
          />
          <icon-exclamation-circle-fill
            v-else
            :style="{ fontSize: '12px', color: '#ff7d00' }"
          />
        </template>
        <div class="log-content">
          <div class="log-title">
            <a-tag :color="getTagColor(log.trigger)">{{ log.trigger }}</a-tag>
            <span>{{ log.title }}</span>
          </div>
          <div class="log-desc">{{ log.description }}</div>
        </div>
      </a-timeline-item>
    </a-timeline>
  </a-card>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { useRouter } from 'vue-router';

  interface OperationLog {
    id: number;
    time: string;
    type: 'success' | 'info' | 'warning';
    trigger: string;
    title: string;
    description: string;
  }

  const router = useRouter();

  const logs = ref<OperationLog[]>([
    {
      id: 1,
      time: '10:32',
      type: 'success',
      trigger: '库存触发器',
      title: '自动更新库存状态',
      description:
        '装备"门式起重机 QZ-50T"出库后，库存数量自动减1，状态更新为"租赁中"',
    },
    {
      id: 2,
      time: '09:45',
      type: 'success',
      trigger: '费用触发器',
      title: '自动计算租赁费用',
      description:
        '订单 LD202401001 归还后，系统自动计算租金：30天 × ¥1,500/天 = ¥45,000',
    },
    {
      id: 3,
      time: '09:20',
      type: 'info',
      trigger: '日志触发器',
      title: '记录装备状态变更',
      description:
        '装备"电动叉车 CPCD-3T"状态从"可用"变更为"租赁中"，已记录到系统日志',
    },
    {
      id: 4,
      time: '08:55',
      type: 'warning',
      trigger: '提醒触发器',
      title: '租赁即将到期提醒',
      description: '订单 LD202312025 将于3天后到期，已自动发送提醒通知给租户',
    },
    {
      id: 5,
      time: '08:30',
      type: 'success',
      trigger: '库存触发器',
      title: '自动恢复库存',
      description:
        '装备"桥式起重机 QD-32T"归还后，可用数量自动+1，状态更新为"可用"',
    },
  ]);

  const getTagColor = (trigger: string) => {
    const colorMap: Record<string, string> = {
      库存触发器: 'blue',
      费用触发器: 'green',
      日志触发器: 'purple',
      提醒触发器: 'orange',
      审核触发器: 'cyan',
    };
    return colorMap[trigger] || 'gray';
  };

  const viewAll = () => {
    router.push({ name: 'SystemLog' });
  };
</script>

<style scoped lang="less">
  .log-content {
    .log-title {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 4px;
      font-weight: 500;
      color: var(--color-text-1);
    }

    .log-desc {
      font-size: 13px;
      color: var(--color-text-3);
      line-height: 1.5;
    }
  }

  :deep(.arco-timeline-item-label) {
    font-size: 12px;
    color: var(--color-text-3);
  }
</style>
