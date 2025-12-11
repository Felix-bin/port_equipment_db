<template>
  <div class="container">
    <Breadcrumb :items="['menu.system', 'menu.system.log']" />
    <a-card class="general-card">
      <template #title>
        <a-space>
          <icon-file />
          <span>{{ $t('system.log.title') }}</span>
        </a-space>
      </template>

      <a-row style="margin-bottom: 16px">
        <a-col :span="20">
          <a-space>
            <a-select
              v-model="filterType"
              :placeholder="$t('system.log.filter.type')"
              style="width: 150px"
              @change="handleFilter"
            >
              <a-option value="all">全部类型</a-option>
              <a-option value="库存触发器">库存触发器</a-option>
              <a-option value="费用触发器">费用触发器</a-option>
              <a-option value="日志触发器">日志触发器</a-option>
              <a-option value="提醒触发器">提醒触发器</a-option>
              <a-option value="审核触发器">审核触发器</a-option>
            </a-select>

            <a-select
              v-model="filterLogType"
              :placeholder="$t('system.log.filter.logType')"
              style="width: 120px"
              @change="handleFilter"
            >
              <a-option value="all">全部状态</a-option>
              <a-option value="success">成功</a-option>
              <a-option value="info">信息</a-option>
              <a-option value="warning">警告</a-option>
            </a-select>

            <a-range-picker
              v-model="dateRange"
              style="width: 280px"
              @change="handleFilter"
            />
          </a-space>
        </a-col>
        <a-col :span="4" style="text-align: right">
          <a-space>
            <a-button @click="handleExport">
              <template #icon>
                <icon-download />
              </template>
              导出日志
            </a-button>
            <a-tooltip content="刷新">
              <div class="action-icon" @click="fetchData">
                <icon-refresh size="18" />
              </div>
            </a-tooltip>
          </a-space>
        </a-col>
      </a-row>

      <a-table
        :columns="columns"
        :data="logData"
        :pagination="pagination"
        :loading="loading"
        @page-change="onPageChange"
      >
        <template #logType="{ record }">
          <a-tag v-if="record.logType === 'success'" color="green">
            <template #icon>
              <icon-check-circle />
            </template>
            成功
          </a-tag>
          <a-tag v-else-if="record.logType === 'info'" color="blue">
            <template #icon>
              <icon-info-circle />
            </template>
            信息
          </a-tag>
          <a-tag v-else-if="record.logType === 'warning'" color="orange">
            <template #icon>
              <icon-exclamation-circle />
            </template>
            警告
          </a-tag>
          <a-tag v-else color="red">
            <template #icon>
              <icon-close-circle />
            </template>
            错误
          </a-tag>
        </template>

        <template #triggerName="{ record }">
          <a-tag :color="getTriggerColor(record.triggerName)">
            {{ record.triggerName }}
          </a-tag>
        </template>

        <template #description="{ record }">
          <a-typography-paragraph
            :ellipsis="{
              rows: 2,
              showTooltip: true,
            }"
            style="margin-bottom: 0"
          >
            {{ record.description }}
          </a-typography-paragraph>
        </template>

        <template #operations="{ record }">
          <a-button type="text" size="small" @click="handleView(record)">
            查看详情
          </a-button>
        </template>
      </a-table>
    </a-card>

    <!-- 日志详情弹窗 -->
    <a-modal
      v-model:visible="detailVisible"
      title="日志详情"
      width="600px"
      :footer="false"
    >
      <a-descriptions :data="detailData" :column="1" bordered>
        <a-descriptions-item label="日志ID">
          {{ selectedLog?.id }}
        </a-descriptions-item>
        <a-descriptions-item label="日志类型">
          <a-tag v-if="selectedLog?.logType === 'success'" color="green">
            成功
          </a-tag>
          <a-tag v-else-if="selectedLog?.logType === 'info'" color="blue">
            信息
          </a-tag>
          <a-tag v-else-if="selectedLog?.logType === 'warning'" color="orange">
            警告
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="触发器">
          <a-tag :color="getTriggerColor(selectedLog?.triggerName)">
            {{ selectedLog?.triggerName }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="操作类型">
          {{ selectedLog?.operation }}
        </a-descriptions-item>
        <a-descriptions-item label="影响表">
          {{ selectedLog?.tableName }}
        </a-descriptions-item>
        <a-descriptions-item label="记录ID">
          {{ selectedLog?.recordId }}
        </a-descriptions-item>
        <a-descriptions-item label="描述">
          {{ selectedLog?.description }}
        </a-descriptions-item>
        <a-descriptions-item label="创建时间">
          {{ selectedLog?.createdAt }}
        </a-descriptions-item>
      </a-descriptions>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
  import { ref, reactive, onMounted } from 'vue';
  import { Message } from '@arco-design/web-vue';
  import { queryTriggerLogs, getTriggerLogById, type TriggerLog } from '@/api/system';

  interface LogRecord {
    id: number;
    logType: 'success' | 'info' | 'warning' | 'error';
    triggerName: string;
    operation: string;
    tableName: string;
    recordId: number | null;
    description: string;
    createdAt: string;
  }

  const loading = ref(false);
  const filterType = ref('all');
  const filterLogType = ref('all');
  const dateRange = ref([]);
  const detailVisible = ref(false);
  const selectedLog = ref<LogRecord | null>(null);

  const pagination = reactive({
    current: 1,
    pageSize: 20,
    total: 0,
    showTotal: true,
    showJumper: true,
    showPageSize: true,
  });

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      width: 80,
    },
    {
      title: '日志类型',
      dataIndex: 'logType',
      slotName: 'logType',
      width: 100,
    },
    {
      title: '触发器',
      dataIndex: 'triggerName',
      slotName: 'triggerName',
      width: 120,
    },
    {
      title: '操作',
      dataIndex: 'operation',
      width: 120,
    },
    {
      title: '影响表',
      dataIndex: 'tableName',
      width: 150,
    },
    {
      title: '描述',
      dataIndex: 'description',
      slotName: 'description',
    },
    {
      title: '时间',
      dataIndex: 'createdAt',
      width: 180,
    },
    {
      title: '操作',
      slotName: 'operations',
      width: 100,
      fixed: 'right',
    },
  ];

  const logData = ref<LogRecord[]>([]);

  const detailData = ref([]);

  const getTriggerColor = (trigger: string) => {
    const colorMap: Record<string, string> = {
      库存触发器: 'blue',
      费用触发器: 'green',
      日志触发器: 'purple',
      提醒触发器: 'orange',
      审核触发器: 'cyan',
      结算触发器: 'arcoblue',
      维护触发器: 'magenta',
    };
    return colorMap[trigger] || 'gray';
  };

  const fetchData = async () => {
    loading.value = true;
    try {
      const params: any = {
        page: pagination.current,
        page_size: pagination.pageSize,
      };

      if (filterLogType.value && filterLogType.value !== 'all') {
        params.log_type = filterLogType.value;
      }

      if (filterType.value && filterType.value !== 'all') {
        params.trigger_name = filterType.value;
      }

      if (dateRange.value && dateRange.value.length === 2) {
        // 格式化日期为 YYYY-MM-DD 格式
        const formatDate = (date: any) => {
          if (!date) return '';
          const d = new Date(date);
          const year = d.getFullYear();
          const month = String(d.getMonth() + 1).padStart(2, '0');
          const day = String(d.getDate()).padStart(2, '0');
          return `${year}-${month}-${day}`;
        };
        params.start_date = formatDate(dateRange.value[0]);
        params.end_date = formatDate(dateRange.value[1]);
      }

      const response = await queryTriggerLogs(params);
      const data = response?.data || response;

      if (data && data.items) {
        logData.value = data.items.map((item: any) => {
          // 格式化日期：将 ISO 格式转换为 YYYY-MM-DD HH:mm:ss
          let formattedDate = '';
          if (item.created_at) {
            const date = new Date(item.created_at);
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            const hours = String(date.getHours()).padStart(2, '0');
            const minutes = String(date.getMinutes()).padStart(2, '0');
            const seconds = String(date.getSeconds()).padStart(2, '0');
            formattedDate = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
          }
          
          return {
            id: item.id,
            logType: item.log_type || item.logType, // 后端返回 log_type
            triggerName: item.trigger_name || item.triggerName, // 后端返回 trigger_name
            operation: item.operation,
            tableName: item.table_name || item.tableName || '', // 后端返回 table_name
            recordId: item.record_id !== null && item.record_id !== undefined ? item.record_id : (item.recordId || null), // 后端返回 record_id
            description: item.description || '',
            createdAt: formattedDate || item.created_at || item.createdAt, // 后端返回 created_at
          };
        });
        pagination.total = data.total || 0;
      }
    } catch (err) {
      console.error('获取触发器日志失败:', err);
      Message.error('获取日志数据失败');
    } finally {
      loading.value = false;
    }
  };

  const handleFilter = () => {
    pagination.current = 1;
    fetchData();
  };

  const handleExport = () => {
    Message.success('导出日志成功');
  };

  const onPageChange = (page: number) => {
    pagination.current = page;
    fetchData();
  };

  const handleView = async (record: LogRecord) => {
    try {
      const response = await getTriggerLogById(record.id);
      const data = response?.data || response;
      
      // 格式化日期
      let formattedDate = '';
      if (data.created_at || data.createdAt) {
        const date = new Date(data.created_at || data.createdAt);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const seconds = String(date.getSeconds()).padStart(2, '0');
        formattedDate = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
      }
      
      selectedLog.value = {
        id: data.id,
        logType: data.log_type || data.logType,
        triggerName: data.trigger_name || data.triggerName,
        operation: data.operation,
        tableName: data.table_name || data.tableName || '',
        recordId: data.record_id !== null && data.record_id !== undefined ? data.record_id : (data.recordId || null),
        description: data.description || '',
        createdAt: formattedDate || data.created_at || data.createdAt,
      };
      detailVisible.value = true;
    } catch (err) {
      console.error('获取日志详情失败:', err);
      Message.error('获取日志详情失败');
    }
  };

  // 页面加载时获取数据
  onMounted(() => {
    fetchData();
  });
</script>

<script lang="ts">
  export default {
    name: 'SystemLog',
  };
</script>

<style scoped lang="less">
  .container {
    padding: 0 20px 20px 20px;
  }

  .action-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s;

    &:hover {
      background-color: var(--color-fill-3);
    }
  }
</style>
