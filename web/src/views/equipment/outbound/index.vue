<template>
  <div class="container">
    <Breadcrumb :items="['menu.equipment', 'menu.equipment.outbound']" />
    <a-card class="general-card" :title="$t('equipment.outbound.title')">
      <a-row>
        <a-col :flex="1">
          <a-form
            :model="formModel"
            :label-col-props="{ span: 6 }"
            :wrapper-col-props="{ span: 18 }"
            label-align="left"
          >
            <a-row :gutter="16">
              <a-col :span="8">
                <a-form-item
                  field="outboundCode"
                  :label="$t('equipment.outbound.form.outboundCode')"
                >
                  <a-input
                    v-model="formModel.outboundCode"
                    :placeholder="
                      $t('equipment.outbound.form.outboundCode.placeholder')
                    "
                  />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item
                  field="equipmentCode"
                  :label="$t('equipment.outbound.form.equipmentCode')"
                >
                  <a-input
                    v-model="formModel.equipmentCode"
                    :placeholder="
                      $t('equipment.outbound.form.equipmentCode.placeholder')
                    "
                  />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item
                  field="rentalOrder"
                  :label="$t('equipment.outbound.form.rentalOrder')"
                >
                  <a-input
                    v-model="formModel.rentalOrder"
                    :placeholder="
                      $t('equipment.outbound.form.rentalOrder.placeholder')
                    "
                  />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item
                  field="outboundTime"
                  :label="$t('equipment.outbound.form.outboundTime')"
                >
                  <a-range-picker
                    v-model="formModel.outboundTime"
                    style="width: 100%"
                  />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item
                  field="status"
                  :label="$t('equipment.outbound.form.status')"
                >
                  <a-select
                    v-model="formModel.status"
                    :options="statusOptions"
                    :placeholder="$t('equipment.outbound.form.selectDefault')"
                  />
                </a-form-item>
              </a-col>
            </a-row>
          </a-form>
        </a-col>
        <a-divider style="height: 84px" direction="vertical" />
        <a-col :flex="'86px'" style="text-align: right">
          <a-space direction="vertical" :size="18">
            <a-button type="primary" @click="search">
              <template #icon>
                <icon-search />
              </template>
              {{ $t('equipment.outbound.form.search') }}
            </a-button>
            <a-button @click="reset">
              <template #icon>
                <icon-refresh />
              </template>
              {{ $t('equipment.outbound.form.reset') }}
            </a-button>
          </a-space>
        </a-col>
      </a-row>
      <a-divider style="margin-top: 0" />
      <a-row style="margin-bottom: 16px">
        <a-col :span="12">
          <a-space>
            <a-button type="primary" @click="handleCreate">
              <template #icon>
                <icon-plus />
              </template>
              {{ $t('equipment.outbound.operation.create') }}
            </a-button>
          </a-space>
        </a-col>
        <a-col
          :span="12"
          style="display: flex; align-items: center; justify-content: end"
        >
          <a-button @click="handleExport">
            <template #icon>
              <icon-download />
            </template>
            {{ $t('equipment.outbound.operation.download') }}
          </a-button>
          <a-tooltip :content="$t('equipment.outbound.actions.refresh')">
            <div class="action-icon" @click="search">
              <icon-refresh size="18" />
            </div>
          </a-tooltip>
        </a-col>
      </a-row>
      <a-table
        row-key="id"
        :loading="loading"
        :pagination="pagination"
        :columns="columns"
        :data="renderData"
        :bordered="false"
        @page-change="onPageChange"
      >
        <template #index="{ rowIndex }">
          {{ rowIndex + 1 + (pagination.current - 1) * pagination.pageSize }}
        </template>
        <template #status="{ record }">
          <a-tag v-if="record.status === 'pending'" color="orange">
            {{ $t('equipment.outbound.form.status.pending') }}
          </a-tag>
          <a-tag v-else-if="record.status === 'completed'" color="green">
            {{ $t('equipment.outbound.form.status.completed') }}
          </a-tag>
          <a-tag v-else color="red">
            {{ $t('equipment.outbound.form.status.cancelled') }}
          </a-tag>
        </template>
        <template #operations="{ record }">
          <a-button type="text" size="small" @click="handleView(record)">
            {{ $t('equipment.outbound.columns.operations.view') }}
          </a-button>
          <a-button
            v-if="record.status === 'pending'"
            type="text"
            size="small"
            @click="handleConfirm(record)"
          >
            {{ $t('equipment.outbound.columns.operations.confirm') }}
          </a-button>
          <a-popconfirm
            content="确定要删除这条出库记录吗？"
            type="warning"
            @ok="handleDelete(record)"
          >
            <a-button type="text" size="small" status="danger"> 删除 </a-button>
          </a-popconfirm>
        </template>
      </a-table>
    </a-card>
    <!-- 创建/编辑模态框 -->
    <a-modal
      v-model:visible="modalVisible"
      :title="modalTitle"
      width="900px"
      @before-ok="handleSubmit"
    >
      <a-form
        ref="formRef"
        :model="form"
        :label-col-props="{ span: 6 }"
        :wrapper-col-props="{ span: 18 }"
      >
        <!-- 基本信息 -->
        <a-divider
          orientation="left"
          style="margin-top: 0; margin-bottom: 16px"
        >
          <span
            style="
              font-size: 14px;
              font-weight: 600;
              color: rgb(var(--arcoblue-6));
            "
            >基本信息</span
          >
        </a-divider>
        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item
              field="equipmentCode"
              label="装备编号"
              :rules="[{ required: true, message: '请输入装备编号' }]"
            >
              <a-input
                v-model="form.equipmentCode"
                placeholder="请输入装备编号"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item
              field="quantity"
              label="数量"
              :rules="[
                { required: true, message: '请输入数量' },
                { type: 'number', min: 1, message: '数量必须大于0' },
              ]"
            >
              <a-input-number
                v-model="form.quantity"
                :min="1"
                placeholder="请输入数量"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item field="rentalOrder" label="关联订单">
              <a-input
                v-model="form.rentalOrder"
                placeholder="请输入订单号（可选）"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item field="outboundTime" label="出库时间">
              <a-date-picker
                v-model="form.outboundTime"
                style="width: 100%"
                placeholder="请选择出库时间"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <!-- 操作信息 -->
        <a-divider
          orientation="left"
          style="margin-top: 8px; margin-bottom: 16px"
        >
          <span
            style="
              font-size: 14px;
              font-weight: 600;
              color: rgb(var(--arcoblue-6));
            "
            >操作信息</span
          >
        </a-divider>
        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item field="operator" label="操作员">
              <a-input
                v-model="form.operator"
                placeholder="请输入操作员（可选）"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item
              field="status"
              label="状态"
              :rules="[{ required: true, message: '请选择状态' }]"
            >
              <a-select
                v-model="form.status"
                :options="statusOptions"
                placeholder="请选择出库状态"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <!-- 其他信息 -->
        <a-divider
          orientation="left"
          style="margin-top: 8px; margin-bottom: 16px"
        >
          <span
            style="
              font-size: 14px;
              font-weight: 600;
              color: rgb(var(--arcoblue-6));
            "
            >其他信息</span
          >
        </a-divider>
        <a-row :gutter="24">
          <a-col :span="24">
            <a-form-item
              field="remark"
              label="备注"
              :label-col-props="{ span: 3 }"
              :wrapper-col-props="{ span: 21 }"
            >
              <a-textarea
                v-model="form.remark"
                :rows="3"
                placeholder="请输入备注信息（可选）"
                :max-length="500"
                show-word-limit
              />
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>
    </a-modal>

    <!-- 查看模态框 -->
    <a-modal
      v-model:visible="viewModalVisible"
      title="查看出库详情"
      width="800px"
      :footer="false"
    >
      <a-descriptions
        v-if="viewRecord"
        :column="2"
        bordered
        :label-style="{ width: '120px' }"
      >
        <a-descriptions-item label="出库单号" :span="2">
          <span style="font-weight: 600; color: rgb(var(--arcoblue-6))">
            {{ viewRecord.outboundCode }}
          </span>
        </a-descriptions-item>
        <a-descriptions-item label="订单号">
          {{ viewRecord.rentalOrder || '-' }}
        </a-descriptions-item>
        <a-descriptions-item label="装备编号">
          {{ viewRecord.equipmentCode }}
        </a-descriptions-item>
        <a-descriptions-item label="装备名称">
          {{ viewRecord.equipmentName || '-' }}
        </a-descriptions-item>
        <a-descriptions-item label="数量">
          <span style="font-weight: 600">{{ viewRecord.quantity }}</span>
        </a-descriptions-item>
        <a-descriptions-item label="出库时间">
          {{ viewRecord.outboundTime || '-' }}
        </a-descriptions-item>
        <a-descriptions-item label="操作员">
          {{ viewRecord.operator || '-' }}
        </a-descriptions-item>
        <a-descriptions-item label="状态">
          <a-tag v-if="viewRecord.status === 'pending'" color="orange">
            {{ $t('equipment.outbound.form.status.pending') }}
          </a-tag>
          <a-tag v-else-if="viewRecord.status === 'completed'" color="green">
            {{ $t('equipment.outbound.form.status.completed') }}
          </a-tag>
          <a-tag v-else color="red">
            {{ $t('equipment.outbound.form.status.cancelled') }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="备注" :span="2">
          <div style="white-space: pre-wrap; word-break: break-word">
            {{ viewRecord.remark || '-' }}
          </div>
        </a-descriptions-item>
      </a-descriptions>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
  import { computed, ref, reactive } from 'vue';
  import { useI18n } from 'vue-i18n';
  import { Message } from '@arco-design/web-vue';
  import type { FormInstance } from '@arco-design/web-vue';
  import useLoading from '@/hooks/loading';
  import {
    queryEquipmentOutboundList,
    createEquipmentOutbound,
    deleteEquipmentOutbound,
  } from '@/api/equipment';
  import { Pagination } from '@/types/global';
  import type { SelectOptionData } from '@arco-design/web-vue/es/select/interface';
  import type { TableColumnData } from '@arco-design/web-vue/es/table/interface';

  const generateFormModel = () => {
    return {
      outboundCode: '',
      equipmentCode: '',
      rentalOrder: '',
      outboundTime: [],
      status: '',
    };
  };

  const { loading, setLoading } = useLoading(true);
  const { t } = useI18n();
  const renderData = ref<any[]>([]);
  const formModel = ref(generateFormModel());
  const modalVisible = ref(false);
  const modalTitle = ref('');
  const form = ref<any>({});
  const formRef = ref<FormInstance>();
  const viewModalVisible = ref(false);
  const viewRecord = ref<any>(null);

  const basePagination: Pagination = {
    current: 1,
    pageSize: 20,
  };
  const pagination = reactive({
    ...basePagination,
    total: 0,
  });

  const statusOptions = computed<SelectOptionData[]>(() => [
    { label: t('equipment.outbound.form.status.pending'), value: 'pending' },
    {
      label: t('equipment.outbound.form.status.completed'),
      value: 'completed',
    },
    {
      label: t('equipment.outbound.form.status.cancelled'),
      value: 'cancelled',
    },
  ]);

  const columns = computed<TableColumnData[]>(() => [
    {
      title: t('equipment.outbound.columns.index'),
      dataIndex: 'index',
      slotName: 'index',
    },
    {
      title: t('equipment.outbound.columns.outboundCode'),
      dataIndex: 'outboundCode',
    },
    {
      title: t('equipment.outbound.columns.rentalOrder'),
      dataIndex: 'rentalOrder',
    },
    {
      title: t('equipment.outbound.columns.equipmentCode'),
      dataIndex: 'equipmentCode',
    },
    {
      title: t('equipment.outbound.columns.equipmentName'),
      dataIndex: 'equipmentName',
    },
    {
      title: t('equipment.outbound.columns.quantity'),
      dataIndex: 'quantity',
    },
    {
      title: t('equipment.outbound.columns.outboundTime'),
      dataIndex: 'outboundTime',
    },
    {
      title: t('equipment.outbound.columns.operator'),
      dataIndex: 'operator',
    },
    {
      title: t('equipment.outbound.columns.status'),
      dataIndex: 'status',
      slotName: 'status',
    },
    {
      title: t('equipment.outbound.columns.operations'),
      dataIndex: 'operations',
      slotName: 'operations',
    },
  ]);

  const fetchData = async (params: any = { current: 1, pageSize: 20 }) => {
    setLoading(true);
    try {
      console.log('请求出库列表，参数:', params);
      const response = await queryEquipmentOutboundList(params);
      console.log('出库列表响应:', response);

      // 处理不同的响应格式
      const responseData = response.data || response;
      console.log('处理后的响应数据:', responseData);

      // 后端返回格式: { code: 200, message: "success", list: [...], total: ... }
      if (responseData && responseData.list) {
        renderData.value = responseData.list;
        pagination.current = params.current || 1;
        pagination.total = responseData.total || 0;
        console.log('出库列表数据已更新，共', responseData.list.length, '条');
      } else {
        console.warn('响应数据格式不正确:', responseData);
        renderData.value = [];
        pagination.total = 0;
      }
    } catch (err: any) {
      console.error('获取出库列表失败:', err);
      Message.error(
        err?.response?.data?.detail || err?.message || '获取出库列表失败'
      );
      renderData.value = [];
      pagination.total = 0;
    } finally {
      setLoading(false);
    }
  };

  const search = () => {
    const searchParams: any = {
      current: basePagination.current,
      pageSize: basePagination.pageSize,
    };

    // 只添加有值的搜索条件
    if (formModel.value.outboundCode) {
      searchParams.outboundCode = formModel.value.outboundCode;
    }
    if (formModel.value.equipmentCode) {
      searchParams.equipmentCode = formModel.value.equipmentCode;
    }
    if (formModel.value.rentalOrder) {
      searchParams.rentalOrder = formModel.value.rentalOrder;
    }
    if (formModel.value.status) {
      searchParams.status = formModel.value.status;
    }

    fetchData(searchParams);
  };

  const reset = () => {
    formModel.value = generateFormModel();
  };

  const onPageChange = (current: number) => {
    fetchData({ ...basePagination, current });
  };

  const handleCreate = () => {
    modalTitle.value = t('equipment.outbound.operation.create');
    form.value = {
      rentalOrder: '',
      equipmentCode: '',
      quantity: 1,
      outboundTime: new Date(),
      operator: '',
      status: 'completed', // 默认为已完成
      remark: '',
    };
    modalVisible.value = true;
  };

  const handleView = (record: any) => {
    viewRecord.value = { ...record };
    viewModalVisible.value = true;
  };

  const handleConfirm = async (record: any) => {
    try {
      // 确认出库操作（如果需要单独的状态更新接口）
      Message.success('出库确认成功');
      fetchData();
    } catch (err: any) {
      console.error('确认出库失败:', err);
      Message.error(
        err?.response?.data?.detail || err?.message || '确认出库失败'
      );
    }
  };

  const handleDelete = async (record: any) => {
    try {
      await deleteEquipmentOutbound(record.id);
      Message.success('删除成功');
      fetchData();
    } catch (err: any) {
      console.error('删除出库记录失败:', err);
      Message.error(err?.response?.data?.detail || err?.message || '删除失败');
    }
  };

  const handleSubmit = async () => {
    if (!formRef.value) {
      return false;
    }

    try {
      // 表单验证
      await formRef.value.validate();

      // 准备提交数据
      const submitData: any = {
        equipmentCode: form.value.equipmentCode?.trim(),
        quantity: form.value.quantity || 1,
        operator: form.value.operator?.trim() || '系统',
        status: form.value.status || 'completed',
        remark: form.value.remark?.trim() || '',
      };

      // 如果有订单号，添加订单号
      if (form.value.rentalOrder) {
        submitData.rentalOrder = form.value.rentalOrder.trim();
      }

      // 处理出库时间
      if (form.value.outboundTime) {
        if (form.value.outboundTime instanceof Date) {
          submitData.outboundTime = form.value.outboundTime
            .toISOString()
            .split('T')[0];
        } else if (typeof form.value.outboundTime === 'string') {
          submitData.outboundTime = form.value.outboundTime.split('T')[0];
        }
      }

      console.log('提交出库数据:', submitData);
      const response = await createEquipmentOutbound(submitData);
      console.log('出库响应:', response);

      Message.success('出库记录创建成功');

      // 显示触发器自动执行的效果
      setTimeout(() => {
        Message.info({
          content: '🔔 [库存触发器] 装备库存数量已自动更新',
          duration: 3000,
        });
      }, 500);

      setTimeout(() => {
        Message.info({
          content: '📝 [日志触发器] 已自动记录装备状态变更',
          duration: 3000,
        });
      }, 1000);

      modalVisible.value = false;
      formRef.value?.resetFields();
      // 重置搜索条件并刷新到第一页
      formModel.value = generateFormModel();
      fetchData({ current: 1, pageSize: basePagination.pageSize });
      return true;
    } catch (err: any) {
      console.error('出库失败:', err);
      // 如果是表单验证错误，Arco Design 会自动显示错误信息
      if (err?.errors) {
        console.log('表单验证错误:', err.errors);
        return false;
      }
      // API 错误
      const errorMessage =
        err?.response?.data?.detail || err?.message || '出库失败';
      Message.error(errorMessage);
      return false;
    }
  };

  const handleExport = () => {
    // Export logic
  };

  fetchData();
</script>

<script lang="ts">
  export default {
    name: 'EquipmentOutbound',
  };
</script>

<style scoped lang="less">
  .container {
    padding: 0 20px 20px 20px;
  }
  .action-icon {
    margin-left: 12px;
    cursor: pointer;
  }
</style>
