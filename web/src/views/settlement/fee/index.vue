<template>
  <div class="container">
    <Breadcrumb :items="['menu.settlement', 'menu.settlement.fee']" />
    <a-card class="general-card">
      <template #title>
        <a-space>
          <icon-bookmark />
          <span>{{ $t('settlement.fee.title') }}</span>
        </a-space>
      </template>
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
                  field="settlementCode"
                  :label="$t('settlement.fee.form.settlementCode')"
                >
                  <a-input
                    v-model="formModel.settlementCode"
                    :placeholder="
                      $t('settlement.fee.form.settlementCode.placeholder')
                    "
                  />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item
                  field="rentalOrder"
                  :label="$t('settlement.fee.form.rentalOrder')"
                >
                  <a-input
                    v-model="formModel.rentalOrder"
                    :placeholder="
                      $t('settlement.fee.form.rentalOrder.placeholder')
                    "
                  />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item
                  field="applicant"
                  :label="$t('settlement.fee.form.applicant')"
                >
                  <a-input
                    v-model="formModel.applicant"
                    :placeholder="
                      $t('settlement.fee.form.applicant.placeholder')
                    "
                  />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item
                  field="settlementTime"
                  :label="$t('settlement.fee.form.settlementTime')"
                >
                  <a-range-picker
                    v-model="formModel.settlementTime"
                    style="width: 100%"
                  />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item
                  field="status"
                  :label="$t('settlement.fee.form.status')"
                >
                  <a-select
                    v-model="formModel.status"
                    :options="statusOptions"
                    :placeholder="$t('settlement.fee.form.selectDefault')"
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
              {{ $t('settlement.fee.form.search') }}
            </a-button>
            <a-button @click="reset">
              <template #icon>
                <icon-refresh />
              </template>
              {{ $t('settlement.fee.form.reset') }}
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
              {{ $t('settlement.fee.operation.create') }}
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
            {{ $t('settlement.fee.operation.download') }}
          </a-button>
          <a-tooltip :content="$t('settlement.fee.actions.refresh')">
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
            {{ $t('settlement.fee.form.status.pending') }}
          </a-tag>
          <a-tag v-else-if="record.status === 'paid'" color="green">
            {{ $t('settlement.fee.form.status.paid') }}
          </a-tag>
          <a-tag v-else color="red">
            {{ $t('settlement.fee.form.status.overdue') }}
          </a-tag>
        </template>
        <template #totalAmount="{ record }">
          <span style="color: #f53f3f; font-weight: bold">
            ¥{{ record.totalAmount?.toLocaleString() }}
          </span>
        </template>
        <template #operations="{ record }">
          <a-button type="text" size="small" @click="handleView(record)">
            {{ $t('settlement.fee.columns.operations.view') }}
          </a-button>
          <a-button
            v-if="record.status === 'pending'"
            type="text"
            size="small"
            @click="handlePay(record)"
          >
            {{ $t('settlement.fee.columns.operations.pay') }}
          </a-button>
          <a-button type="text" size="small" @click="handlePrint(record)">
            {{ $t('settlement.fee.columns.operations.print') }}
          </a-button>
        </template>
      </a-table>
    </a-card>
    <!-- 查看模态框 -->
    <a-modal
      v-model:visible="viewModalVisible"
      title="查看费用结算详情"
      width="900px"
      :footer="false"
    >
      <a-descriptions
        v-if="viewRecord"
        :column="2"
        bordered
        :label-style="{ width: '140px', fontWeight: '600' }"
      >
        <a-descriptions-item label="结算单号" :span="2">
          <span style="font-weight: 600; color: rgb(var(--arcoblue-6))">
            {{ viewRecord.settlementCode || '-' }}
          </span>
        </a-descriptions-item>
        <a-descriptions-item label="租赁订单号">
          {{ viewRecord.rentalOrder || '-' }}
        </a-descriptions-item>
        <a-descriptions-item label="申请人">
          {{ viewRecord.applicant || '-' }}
        </a-descriptions-item>
        <a-descriptions-item label="租赁天数">
          {{ viewRecord.rentalDays || 0 }} 天
        </a-descriptions-item>
        <a-descriptions-item label="日租金">
          ¥{{ (viewRecord.dailyRate || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
        </a-descriptions-item>
        <a-descriptions-item label="结算时间">
          {{ viewRecord.settlementTime || '-' }}
        </a-descriptions-item>
        <a-descriptions-item label="支付方式">
          {{
            paymentMethodOptions.find(
              (opt) => opt.value === viewRecord.paymentMethod
            )?.label || viewRecord.paymentMethod || '-'
          }}
        </a-descriptions-item>
        <a-descriptions-item label="状态" :span="2">
          <a-tag v-if="viewRecord.status === 'pending'" color="orange">
            {{ $t('settlement.fee.form.status.pending') }}
          </a-tag>
          <a-tag v-else-if="viewRecord.status === 'paid'" color="green">
            {{ $t('settlement.fee.form.status.paid') }}
          </a-tag>
          <a-tag v-else color="red">
            {{ $t('settlement.fee.form.status.overdue') }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="装备费用" :span="1">
          <span style="color: #165dff">
            ¥{{ (viewRecord.equipmentFee || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
          </span>
        </a-descriptions-item>
        <a-descriptions-item label="使用费用" :span="1">
          <span style="color: #165dff">
            ¥{{ (viewRecord.usageFee || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
          </span>
        </a-descriptions-item>
        <a-descriptions-item label="损坏费用" :span="1">
          <span style="color: #f53f3f">
            ¥{{ (viewRecord.damageFee || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
          </span>
        </a-descriptions-item>
        <a-descriptions-item label="折扣" :span="1">
          {{ viewRecord.discount || 0 }}%
        </a-descriptions-item>
        <a-descriptions-item label="总金额" :span="2">
          <span
            style="
              font-size: 18px;
              font-weight: 700;
              color: #f53f3f;
            "
          >
            ¥{{ (viewRecord.totalAmount || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
          </span>
        </a-descriptions-item>
        <a-descriptions-item label="备注" :span="2">
          <div style="white-space: pre-wrap; word-break: break-word">
            {{ viewRecord.remark || '-' }}
          </div>
        </a-descriptions-item>
      </a-descriptions>
    </a-modal>

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
              field="rentalOrder"
              :label="$t('settlement.fee.form.rentalOrder')"
              :rules="[{ required: true, message: '请输入租赁订单号' }]"
            >
              <a-input
                v-model="form.rentalOrder"
                placeholder="请输入租赁订单号"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item
              field="applicant"
              :label="$t('settlement.fee.form.applicant')"
            >
              <a-input
                v-model="form.applicant"
                placeholder="请输入申请人"
              />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item
              field="rentalDays"
              :label="$t('settlement.fee.form.rentalDays')"
            >
              <a-input-number
                v-model="form.rentalDays"
                :min="1"
                placeholder="请输入租赁天数"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item
              field="dailyRate"
              :label="$t('settlement.fee.form.dailyRate')"
            >
              <a-input-number
                v-model="form.dailyRate"
                :min="0"
                :precision="2"
                placeholder="请输入日租金"
                style="width: 100%"
              >
                <template #prefix>¥</template>
              </a-input-number>
            </a-form-item>
          </a-col>
        </a-row>

        <!-- 费用信息 -->
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
            >费用信息</span
          >
        </a-divider>
        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item
              field="equipmentFee"
              :label="$t('settlement.fee.form.equipmentFee')"
            >
              <a-input-number
                v-model="form.equipmentFee"
                :min="0"
                :precision="2"
                placeholder="请输入装备费用"
                style="width: 100%"
              >
                <template #prefix>¥</template>
              </a-input-number>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item
              field="usageFee"
              :label="$t('settlement.fee.form.usageFee')"
            >
              <a-input-number
                v-model="form.usageFee"
                :min="0"
                :precision="2"
                placeholder="请输入使用费用"
                style="width: 100%"
              >
                <template #prefix>¥</template>
              </a-input-number>
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item
              field="damageFee"
              :label="$t('settlement.fee.form.damageFee')"
            >
              <a-input-number
                v-model="form.damageFee"
                :min="0"
                :precision="2"
                placeholder="请输入损坏费用"
                style="width: 100%"
              >
                <template #prefix>¥</template>
              </a-input-number>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item
              field="discount"
              :label="$t('settlement.fee.form.discount')"
            >
              <a-input-number
                v-model="form.discount"
                :min="0"
                :max="100"
                placeholder="请输入折扣"
                style="width: 100%"
              >
                <template #suffix>%</template>
              </a-input-number>
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item
              field="totalAmount"
              :label="$t('settlement.fee.form.totalAmount')"
            >
              <a-input-number
                v-model="form.totalAmount"
                :min="0"
                :precision="2"
                disabled
                style="width: 100%"
              >
                <template #prefix>
                  <span style="font-weight: 600; color: #f53f3f">¥</span>
                </template>
              </a-input-number>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item
              field="paymentMethod"
              :label="$t('settlement.fee.form.paymentMethod')"
            >
              <a-select
                v-model="form.paymentMethod"
                :options="paymentMethodOptions"
                placeholder="请选择支付方式"
                style="width: 100%"
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
              :label="$t('settlement.fee.form.remark')"
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
  </div>
</template>

<script lang="ts" setup>
  import { computed, ref, reactive, watch } from 'vue';
  import { useI18n } from 'vue-i18n';
  import { Message } from '@arco-design/web-vue';
  import type { FormInstance } from '@arco-design/web-vue';
  import useLoading from '@/hooks/loading';
  import {
    querySettlementFeeList,
    createSettlementFee,
    paySettlementFee,
  } from '@/api/settlement';
  import { Pagination } from '@/types/global';
  import type { SelectOptionData } from '@arco-design/web-vue/es/select/interface';
  import type { TableColumnData } from '@arco-design/web-vue/es/table/interface';

  const generateFormModel = () => {
    return {
      settlementCode: '',
      rentalOrder: '',
      applicant: '',
      settlementTime: [],
      status: '',
    };
  };

  const { loading, setLoading } = useLoading(true);
  const { t } = useI18n();
  const renderData = ref<any[]>([]);
  const formModel = ref(generateFormModel());
  const modalVisible = ref(false);
  const viewModalVisible = ref(false);
  const modalTitle = ref('');
  const form = ref<any>({});
  const viewRecord = ref<any>(null);
  const formRef = ref<FormInstance>();

  const basePagination: Pagination = {
    current: 1,
    pageSize: 20,
  };
  const pagination = reactive({
    ...basePagination,
    total: 0,
  });

  const statusOptions = computed<SelectOptionData[]>(() => [
    { label: t('settlement.fee.form.status.pending'), value: 'pending' },
    { label: t('settlement.fee.form.status.paid'), value: 'paid' },
    { label: t('settlement.fee.form.status.overdue'), value: 'overdue' },
  ]);

  const paymentMethodOptions = computed<SelectOptionData[]>(() => [
    { label: t('settlement.fee.form.paymentMethod.cash'), value: 'cash' },
    {
      label: t('settlement.fee.form.paymentMethod.transfer'),
      value: 'transfer',
    },
    { label: t('settlement.fee.form.paymentMethod.check'), value: 'check' },
    { label: t('settlement.fee.form.paymentMethod.other'), value: 'other' },
  ]);

  const columns = computed<TableColumnData[]>(() => [
    {
      title: t('settlement.fee.columns.index'),
      dataIndex: 'index',
      slotName: 'index',
    },
    {
      title: t('settlement.fee.columns.settlementCode'),
      dataIndex: 'settlementCode',
    },
    {
      title: t('settlement.fee.columns.rentalOrder'),
      dataIndex: 'rentalOrder',
    },
    {
      title: t('settlement.fee.columns.applicant'),
      dataIndex: 'applicant',
    },
    {
      title: t('settlement.fee.columns.rentalDays'),
      dataIndex: 'rentalDays',
    },
    {
      title: t('settlement.fee.columns.totalAmount'),
      dataIndex: 'totalAmount',
      slotName: 'totalAmount',
    },
    {
      title: t('settlement.fee.columns.paymentMethod'),
      dataIndex: 'paymentMethod',
    },
    {
      title: t('settlement.fee.columns.settlementTime'),
      dataIndex: 'settlementTime',
    },
    {
      title: t('settlement.fee.columns.status'),
      dataIndex: 'status',
      slotName: 'status',
    },
    {
      title: t('settlement.fee.columns.operations'),
      dataIndex: 'operations',
      slotName: 'operations',
    },
  ]);

  // Calculate total amount
  watch(
    () => [
      form.value.rentalDays,
      form.value.dailyRate,
      form.value.equipmentFee,
      form.value.usageFee,
      form.value.damageFee,
      form.value.discount,
    ],
    () => {
      const baseAmount =
        (form.value.rentalDays || 0) * (form.value.dailyRate || 0) +
        (form.value.equipmentFee || 0) +
        (form.value.usageFee || 0) +
        (form.value.damageFee || 0);
      const discountAmount = baseAmount * ((form.value.discount || 0) / 100);
      form.value.totalAmount = baseAmount - discountAmount;
    },
    { deep: true }
  );

  const fetchData = async (params: any = { current: 1, pageSize: 20 }) => {
    setLoading(true);
    try {
      console.log('请求费用结算列表，参数:', params);
      const response = await querySettlementFeeList(params);
      console.log('费用结算列表响应:', response);

      // 处理不同的响应格式
      const responseData = response.data || response;
      console.log('处理后的响应数据:', responseData);

      // 后端返回格式: { code: 200, message: "success", list: [...], total: ... }
      if (responseData && responseData.list) {
        renderData.value = responseData.list;
        pagination.current = params.current || 1;
        pagination.total = responseData.total || 0;
        console.log(
          '费用结算列表数据已更新，共',
          responseData.list.length,
          '条'
        );
      } else {
        console.warn('响应数据格式不正确:', responseData);
        renderData.value = [];
        pagination.total = 0;
      }
    } catch (err: any) {
      console.error('获取费用结算列表失败:', err);
      Message.error(
        err?.response?.data?.detail || err?.message || '获取费用结算列表失败'
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
    if (formModel.value.settlementCode) {
      searchParams.settlementCode = formModel.value.settlementCode;
    }
    if (formModel.value.rentalOrder) {
      searchParams.rentalOrder = formModel.value.rentalOrder;
    }
    if (formModel.value.applicant) {
      searchParams.applicant = formModel.value.applicant;
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
    const searchParams: any = {
      current,
      pageSize: basePagination.pageSize,
    };

    // 保留搜索条件
    if (formModel.value.settlementCode) {
      searchParams.settlementCode = formModel.value.settlementCode;
    }
    if (formModel.value.rentalOrder) {
      searchParams.rentalOrder = formModel.value.rentalOrder;
    }
    if (formModel.value.applicant) {
      searchParams.applicant = formModel.value.applicant;
    }
    if (formModel.value.status) {
      searchParams.status = formModel.value.status;
    }

    fetchData(searchParams);
  };

  const handleCreate = () => {
    modalTitle.value = t('settlement.fee.operation.create');
    form.value = {};
    modalVisible.value = true;
  };

  const handleView = (record: any) => {
    viewRecord.value = { ...record };
    viewModalVisible.value = true;
  };

  const handlePay = async (record: any) => {
    try {
      await paySettlementFee(record.id);
      Message.success('支付成功');
      // 刷新当前页数据
      const searchParams: any = {
        current: pagination.current,
        pageSize: pagination.pageSize,
      };
      if (formModel.value.settlementCode) {
        searchParams.settlementCode = formModel.value.settlementCode;
      }
      if (formModel.value.rentalOrder) {
        searchParams.rentalOrder = formModel.value.rentalOrder;
      }
      if (formModel.value.applicant) {
        searchParams.applicant = formModel.value.applicant;
      }
      if (formModel.value.status) {
        searchParams.status = formModel.value.status;
      }
      fetchData(searchParams);
    } catch (err: any) {
      console.error('支付失败:', err);
      Message.error(
        err?.response?.data?.detail || err?.message || '支付失败'
      );
    }
  };

  const handlePrint = (record: any) => {
    // Print logic
    window.print();
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
        rentalOrder: form.value.rentalOrder?.trim(),
        applicant: form.value.applicant?.trim() || '',
        rentalDays: form.value.rentalDays || 0,
        dailyRate: form.value.dailyRate || 0,
        equipmentFee: form.value.equipmentFee || 0,
        usageFee: form.value.usageFee || 0,
        damageFee: form.value.damageFee || 0,
        discount: form.value.discount || 0,
        totalAmount: form.value.totalAmount || 0,
        paymentMethod: form.value.paymentMethod || 'transfer',
        remark: form.value.remark?.trim() || '',
      };

      console.log('提交费用结算数据:', submitData);
      const response = await createSettlementFee(submitData);
      console.log('费用结算响应:', response);

      Message.success('费用结算创建成功');

      modalVisible.value = false;
      formRef.value?.resetFields();
      form.value = {};
      // 重置搜索条件并刷新到第一页
      formModel.value = generateFormModel();
      fetchData({ current: 1, pageSize: basePagination.pageSize });
      return true;
    } catch (err: any) {
      console.error('创建费用结算失败:', err);
      // 如果是表单验证错误，Arco Design 会自动显示错误信息
      if (err?.errors) {
        console.log('表单验证错误:', err.errors);
        return false;
      }
      // API 错误
      const errorMessage =
        err?.response?.data?.detail || err?.message || '创建失败';
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
    name: 'SettlementFee',
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
