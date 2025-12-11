<template>
  <div class="container">
    <Breadcrumb :items="['menu.rental', 'menu.rental.return']" />
    <a-card class="general-card" :title="$t('rental.return.title')">
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
                  field="returnCode"
                  :label="$t('rental.return.form.returnCode')"
                >
                  <a-input
                    v-model="formModel.returnCode"
                    :placeholder="
                      $t('rental.return.form.returnCode.placeholder')
                    "
                  />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item
                  field="rentalOrder"
                  :label="$t('rental.return.form.rentalOrder')"
                >
                  <a-input
                    v-model="formModel.rentalOrder"
                    :placeholder="
                      $t('rental.return.form.rentalOrder.placeholder')
                    "
                  />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item
                  field="equipmentCode"
                  :label="$t('rental.return.form.equipmentCode')"
                >
                  <a-input
                    v-model="formModel.equipmentCode"
                    :placeholder="
                      $t('rental.return.form.equipmentCode.placeholder')
                    "
                  />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item
                  field="returnTime"
                  :label="$t('rental.return.form.returnTime')"
                >
                  <a-range-picker
                    v-model="formModel.returnTime"
                    style="width: 100%"
                  />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item
                  field="inspectionStatus"
                  :label="$t('rental.return.form.inspectionStatus')"
                >
                  <a-select
                    v-model="formModel.inspectionStatus"
                    :options="inspectionStatusOptions"
                    :placeholder="$t('rental.return.form.selectDefault')"
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
              {{ $t('rental.return.form.search') }}
            </a-button>
            <a-button @click="reset">
              <template #icon>
                <icon-refresh />
              </template>
              {{ $t('rental.return.form.reset') }}
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
              {{ $t('rental.return.operation.create') }}
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
            {{ $t('rental.return.operation.download') }}
          </a-button>
          <a-tooltip :content="$t('rental.return.actions.refresh')">
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
        <template #inspectionStatus="{ record }">
          <a-tag v-if="record.inspectionStatus === 'pending'" color="orange">
            {{ $t('rental.return.form.inspectionStatus.pending') }}
          </a-tag>
          <a-tag v-else-if="record.inspectionStatus === 'passed'" color="green">
            {{ $t('rental.return.form.inspectionStatus.passed') }}
          </a-tag>
          <a-tag v-else color="red">
            {{ $t('rental.return.form.inspectionStatus.failed') }}
          </a-tag>
        </template>
        <template #operations="{ record }">
          <a-button type="text" size="small" @click="handleView(record)">
            {{ $t('rental.return.columns.operations.view') }}
          </a-button>
          <a-button
            v-if="record.inspectionStatus === 'pending'"
            type="text"
            size="small"
            @click="handleInspect(record)"
          >
            {{ $t('rental.return.columns.operations.inspect') }}
          </a-button>
        </template>
      </a-table>
    </a-card>
    <!-- 创建归还记录模态框 -->
    <a-modal
      v-if="
        modalTitle !== t('rental.return.operation.view') &&
        modalTitle !== t('rental.return.operation.inspect')
      "
      v-model:visible="modalVisible"
      :title="modalTitle"
      width="900px"
      "
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
              :label="$t('rental.return.form.rentalOrder')"
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
              field="equipmentCode"
              :label="$t('rental.return.form.equipmentCode')"
              :rules="[{ required: true, message: '请输入装备编号' }]"
            >
              <a-input
                v-model="form.equipmentCode"
                placeholder="请输入装备编号"
              />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item
              field="quantity"
              :label="$t('rental.return.form.quantity')"
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
          <a-col :span="12">
            <a-form-item
              field="returnTime"
              :label="$t('rental.return.form.returnTime')"
            >
              <a-date-picker
                v-model="form.returnTime"
                style="width: 100%"
                placeholder="请选择归还时间"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <!-- 设备状态 -->
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
            >设备状态</span
          >
        </a-divider>
        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item
              field="equipmentCondition"
              :label="$t('rental.return.form.equipmentCondition')"
            >
              <a-select
                v-model="form.equipmentCondition"
                :options="conditionOptions"
                placeholder="请选择设备状态"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item
              field="inspector"
              :label="$t('rental.return.form.inspector')"
            >
              <a-input
                v-model="form.inspector"
                placeholder="请输入归还人（可选）"
              />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="24">
          <a-col :span="24">
            <a-form-item
              field="damageDescription"
              :label="$t('rental.return.form.damageDescription')"
              :label-col-props="{ span: 3 }"
              :wrapper-col-props="{ span: 21 }"
            >
              <a-textarea
                v-model="form.damageDescription"
                :rows="3"
                placeholder="请输入损坏描述（可选）"
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

    <!-- 质检模态框 -->
    <a-modal
      v-model:visible="inspectModalVisible"
      :title="t('rental.return.operation.inspect')"
      width="900px"
      @before-ok="handleSubmit"
    >
      <a-form
        ref="inspectFormRef"
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
              :label="$t('rental.return.form.equipmentCode')"
            >
              <a-input v-model="form.equipmentCode" disabled />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item
              field="equipmentCondition"
              :label="$t('rental.return.form.equipmentCondition')"
            >
              <a-select
                v-model="form.equipmentCondition"
                :options="conditionOptions"
                placeholder="请选择设备状态"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <!-- 质检信息 -->
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
            >质检信息</span
          >
        </a-divider>
        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item
              field="inspector"
              :label="$t('rental.return.form.inspector')"
              :rules="[{ required: true, message: '请输入质检员' }]"
            >
              <a-input v-model="form.inspector" placeholder="请输入质检员" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item
              field="inspectionStatus"
              label="质检结果"
              :rules="[{ required: true, message: '请选择质检结果' }]"
            >
              <a-select
                v-model="form.inspectionStatus"
                :options="inspectionStatusOptions"
                placeholder="请选择质检结果"
              />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="24">
          <a-col :span="24">
            <a-form-item
              field="inspectionResult"
              :label="$t('rental.return.form.inspectionResult')"
              :label-col-props="{ span: 3 }"
              :wrapper-col-props="{ span: 21 }"
            >
              <a-textarea
                v-model="form.inspectionResult"
                :rows="3"
                placeholder="请输入质检结果说明"
              />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="24">
          <a-col :span="24">
            <a-form-item
              field="damageDescription"
              :label="$t('rental.return.form.damageDescription')"
              :label-col-props="{ span: 3 }"
              :wrapper-col-props="{ span: 21 }"
            >
              <a-textarea
                v-model="form.damageDescription"
                :rows="3"
                placeholder="请输入损坏描述（如有）"
              />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item field="repairCost" label="维修费用">
              <a-input-number
                v-model="form.repairCost"
                :min="0"
                placeholder="请输入维修费用"
                style="width: 100%"
              >
                <template #prefix>¥</template>
              </a-input-number>
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
      title="查看归还详情"
      width="900px"
      :footer="false"
    >
      <a-descriptions
        v-if="viewRecord"
        :column="2"
        bordered
        :label-style="{ width: '120px' }"
      >
        <a-descriptions-item label="归还单号" :span="2">
          <span style="font-weight: 600; color: rgb(var(--arcoblue-6))">
            {{ viewRecord.returnCode }}
          </span>
        </a-descriptions-item>
        <a-descriptions-item label="租赁订单">
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
        <a-descriptions-item label="归还时间">
          {{ viewRecord.returnTime || '-' }}
        </a-descriptions-item>
        <a-descriptions-item label="设备状态">
          <a-tag v-if="viewRecord.equipmentCondition === 'good'" color="green"
            >完好</a-tag
          >
          <a-tag
            v-else-if="viewRecord.equipmentCondition === 'normal'"
            color="blue"
            >正常</a-tag
          >
          <a-tag v-else color="red">损坏</a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="质检状态">
          <a-tag
            v-if="viewRecord.inspectionStatus === 'pending'"
            color="orange"
          >
            {{ $t('rental.return.form.inspectionStatus.pending') }}
          </a-tag>
          <a-tag
            v-else-if="viewRecord.inspectionStatus === 'passed'"
            color="green"
          >
            {{ $t('rental.return.form.inspectionStatus.passed') }}
          </a-tag>
          <a-tag v-else color="red">
            {{ $t('rental.return.form.inspectionStatus.failed') }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="质检员">
          {{ viewRecord.inspector || '-' }}
        </a-descriptions-item>
        <a-descriptions-item label="损坏描述" :span="2">
          <div style="white-space: pre-wrap; word-break: break-word">
            {{ viewRecord.damageDescription || '-' }}
          </div>
        </a-descriptions-item>
        <a-descriptions-item label="质检结果" :span="2">
          <div style="white-space: pre-wrap; word-break: break-word">
            {{ viewRecord.inspectionResult || '-' }}
          </div>
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
    queryRentalReturnList,
    createRentalReturn,
    inspectRentalReturn,
  } from '@/api/rental';
  import { Pagination } from '@/types/global';
  import type { SelectOptionData } from '@arco-design/web-vue/es/select/interface';
  import type { TableColumnData } from '@arco-design/web-vue/es/table/interface';

  const generateFormModel = () => {
    return {
      returnCode: '',
      rentalOrder: '',
      equipmentCode: '',
      returnTime: [],
      inspectionStatus: '',
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
  const inspectModalVisible = ref(false);
  const inspectFormRef = ref<FormInstance>();
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

  const inspectionStatusOptions = computed<SelectOptionData[]>(() => [
    {
      label: t('rental.return.form.inspectionStatus.pending'),
      value: 'pending',
    },
    { label: t('rental.return.form.inspectionStatus.passed'), value: 'passed' },
    { label: t('rental.return.form.inspectionStatus.failed'), value: 'failed' },
  ]);

  const conditionOptions = computed<SelectOptionData[]>(() => [
    { label: t('rental.return.form.equipmentCondition.good'), value: 'good' },
    {
      label: t('rental.return.form.equipmentCondition.normal'),
      value: 'normal',
    },
    {
      label: t('rental.return.form.equipmentCondition.damaged'),
      value: 'damaged',
    },
  ]);

  const columns = computed<TableColumnData[]>(() => [
    {
      title: t('rental.return.columns.index'),
      dataIndex: 'index',
      slotName: 'index',
    },
    {
      title: t('rental.return.columns.returnCode'),
      dataIndex: 'returnCode',
    },
    {
      title: t('rental.return.columns.rentalOrder'),
      dataIndex: 'rentalOrder',
    },
    {
      title: t('rental.return.columns.equipmentCode'),
      dataIndex: 'equipmentCode',
    },
    {
      title: t('rental.return.columns.equipmentName'),
      dataIndex: 'equipmentName',
    },
    {
      title: t('rental.return.columns.quantity'),
      dataIndex: 'quantity',
    },
    {
      title: t('rental.return.columns.returnTime'),
      dataIndex: 'returnTime',
    },
    {
      title: t('rental.return.columns.equipmentCondition'),
      dataIndex: 'equipmentCondition',
    },
    {
      title: t('rental.return.columns.inspectionStatus'),
      dataIndex: 'inspectionStatus',
      slotName: 'inspectionStatus',
    },
    {
      title: t('rental.return.columns.inspector'),
      dataIndex: 'inspector',
    },
    {
      title: t('rental.return.columns.operations'),
      dataIndex: 'operations',
      slotName: 'operations',
    },
  ]);

  const fetchData = async (params: any = { current: 1, pageSize: 20 }) => {
    setLoading(true);
    try {
      const response = await queryRentalReturnList(params);

      // 处理不同的响应格式
      const responseData = response.data || response;

      // 后端返回格式: { code: 200, message: "success", list: [...], total: ... }
      if (responseData && responseData.list) {
        renderData.value = responseData.list;
        pagination.current = params.current || 1;
        pagination.total = responseData.total || 0;
      } else {
        renderData.value = [];
        pagination.total = 0;
      }
    } catch (err: any) {
      Message.error(
        err?.response?.data?.detail || err?.message || '获取归还列表失败'
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
    if (formModel.value.returnCode) {
      searchParams.returnCode = formModel.value.returnCode;
    }
    if (formModel.value.rentalOrder) {
      searchParams.rentalOrder = formModel.value.rentalOrder;
    }
    if (formModel.value.equipmentCode) {
      searchParams.equipmentCode = formModel.value.equipmentCode;
    }
    if (formModel.value.inspectionStatus) {
      searchParams.inspectionStatus = formModel.value.inspectionStatus;
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
    modalTitle.value = t('rental.return.operation.create');
    form.value = {
      rentalOrder: '',
      equipmentCode: '',
      quantity: 1,
      returnTime: new Date(),
      equipmentCondition: 'good',
      damageDescription: '',
      inspector: '',
      remark: '',
    };
    modalVisible.value = true;
  };

  const handleView = (record: any) => {
    viewRecord.value = { ...record };
    viewModalVisible.value = true;
  };

  const handleInspect = (record: any) => {
    form.value = {
      ...record,
      id: record.id,
      equipmentCode: record.equipmentCode,
      inspectionStatus: 'pending',
      repairCost: 0,
      inspector: '',
      inspectionResult: '',
    };
    inspectModalVisible.value = true;
  };

  const handleSubmit = async () => {
    // 判断是质检模态框还是创建模态框
    if (inspectModalVisible.value) {
      // 质检操作
      if (!inspectFormRef.value) {
        return false;
      }

      try {
        await inspectFormRef.value.validate();

        const inspectData: any = {
          equipmentCode: form.value.equipmentCode?.trim(),
          inspector: form.value.inspector?.trim(),
          equipmentCondition: form.value.equipmentCondition || 'good',
          inspectionResult: form.value.inspectionResult?.trim() || '通过',
          damageDescription: form.value.damageDescription?.trim() || '',
          repairCost: form.value.repairCost || 0,
          inspectionStatus: form.value.inspectionStatus || 'passed',
          remark: form.value.remark?.trim() || '',
        };

        await inspectRentalReturn(form.value.id, inspectData);
        Message.success('质检完成');

        inspectModalVisible.value = false;
        inspectFormRef.value?.resetFields();
        fetchData({ current: 1, pageSize: basePagination.pageSize });
        return true;
      } catch (err: any) {
        if (err?.errors) {
          return false;
        }
        const errorMessage =
          err?.response?.data?.detail || err?.message || '质检失败';
        Message.error(errorMessage);
        return false;
      }
    } else {
      // 创建归还记录
      if (!formRef.value) {
        return false;
      }

      try {
        await formRef.value.validate();

        const submitData: any = {
          rentalOrder: form.value.rentalOrder?.trim(),
          equipmentCode: form.value.equipmentCode?.trim(),
          quantity: form.value.quantity || 1,
          equipmentCondition: form.value.equipmentCondition || 'good',
          damageDescription: form.value.damageDescription?.trim() || '',
          inspector: form.value.inspector?.trim() || '系统',
          remark: form.value.remark?.trim() || '',
        };

        // 处理归还时间
        if (form.value.returnTime) {
          if (form.value.returnTime instanceof Date) {
            const [datePart] = form.value.returnTime
              .toISOString()
              .split('T');
            submitData.returnTime = datePart;
          } else if (typeof form.value.returnTime === 'string') {
            const [datePart] = form.value.returnTime.split('T');
            submitData.returnTime = datePart;
          }
        }

        const response = await createRentalReturn(submitData);

        Message.success('归还记录创建成功');

        modalVisible.value = false;
        formRef.value?.resetFields();
        // 重置搜索条件并刷新到第一页
        formModel.value = generateFormModel();
        fetchData({ current: 1, pageSize: basePagination.pageSize });
        return true;
      } catch (err: any) {
        if (err?.errors) {
          return false;
        }
        const errorMessage =
          err?.response?.data?.detail || err?.message || '提交失败';
        Message.error(errorMessage);
        return false;
      }
    }
  };

  const handleExport = () => {
    // Export logic
  };

  fetchData();
</script>

<script lang="ts">
  export default {
    name: 'RentalReturn',
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
