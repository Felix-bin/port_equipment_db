<template>
  <div class="container">
    <Breadcrumb :items="['menu.equipment', 'menu.equipment.inbound']" />
    <a-card class="general-card" :title="$t('equipment.inbound.title')">
      <a-row>
        <a-col :flex="1">
          <a-form
            :model="formModel"
            :label-col-props="{ span: 6 }"
            :wrapper-col-props="{ span: 18 }"
            label-align="left"
          >
            <a-row :gutter="24">
              <a-col :span="8">
                <a-form-item
                  field="equipmentCode"
                  :label="$t('equipment.inbound.form.equipmentCode')"
                >
                  <a-input
                    v-model="formModel.equipmentCode"
                    :placeholder="
                      $t('equipment.inbound.form.equipmentCode.placeholder')
                    "
                  />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item
                  field="equipmentName"
                  :label="$t('equipment.inbound.form.equipmentName')"
                >
                  <a-input
                    v-model="formModel.equipmentName"
                    :placeholder="
                      $t('equipment.inbound.form.equipmentName.placeholder')
                    "
                  />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item
                  field="equipmentType"
                  :label="$t('equipment.inbound.form.equipmentType')"
                >
                  <a-select
                    v-model="formModel.equipmentType"
                    :options="equipmentTypeOptions"
                    :placeholder="$t('equipment.inbound.form.selectDefault')"
                  />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item
                  field="supplier"
                  :label="$t('equipment.inbound.form.supplier')"
                >
                  <a-input
                    v-model="formModel.supplier"
                    :placeholder="
                      $t('equipment.inbound.form.supplier.placeholder')
                    "
                  />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item
                  field="inboundTime"
                  :label="$t('equipment.inbound.form.inboundTime')"
                >
                  <a-range-picker
                    v-model="formModel.inboundTime"
                    style="width: 100%"
                  />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item
                  field="status"
                  :label="$t('equipment.inbound.form.status')"
                >
                  <a-select
                    v-model="formModel.status"
                    :options="statusOptions"
                    :placeholder="$t('equipment.inbound.form.selectDefault')"
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
              {{ $t('equipment.inbound.form.search') }}
            </a-button>
            <a-button @click="reset">
              <template #icon>
                <icon-refresh />
              </template>
              {{ $t('equipment.inbound.form.reset') }}
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
              {{ $t('equipment.inbound.operation.create') }}
            </a-button>
            <a-upload action="/">
              <template #upload-button>
                <a-button>
                  {{ $t('equipment.inbound.operation.import') }}
                </a-button>
              </template>
            </a-upload>
          </a-space>
        </a-col>
        <a-col
          :span="12"
          style="display: flex; align-items: center; justify-content: end"
        >
          <a-tooltip :content="$t('equipment.inbound.actions.refresh')">
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
            {{ $t('equipment.inbound.form.status.pending') }}
          </a-tag>
          <a-tag v-else-if="record.status === 'completed'" color="green">
            {{ $t('equipment.inbound.form.status.completed') }}
          </a-tag>
          <a-tag v-else color="red">
            {{ $t('equipment.inbound.form.status.rejected') }}
          </a-tag>
        </template>
        <template #operations="{ record }">
          <a-button type="text" size="small" @click="handleView(record)">
            {{ $t('equipment.inbound.columns.operations.view') }}
          </a-button>
          <a-button
            v-if="record.status === 'pending'"
            type="text"
            size="small"
            @click="handleEdit(record)"
          >
            {{ $t('equipment.inbound.columns.operations.edit') }}
          </a-button>
        </template>
      </a-table>
    </a-card>

    <!-- 查看模态框 -->
    <a-modal
      v-model:visible="viewModalVisible"
      :title="'查看入库详情'"
      width="750px"
      :footer="false"
    >
      <a-descriptions
        v-if="viewRecord"
        :column="2"
        bordered
        :label-style="{ width: '120px' }"
      >
        <a-descriptions-item label="装备编号" :span="2">
          <span style="font-weight: 600; color: rgb(var(--arcoblue-6))">
            {{ viewRecord.equipmentCode }}
          </span>
        </a-descriptions-item>
        <a-descriptions-item label="装备名称">
          {{ viewRecord.equipmentName }}
        </a-descriptions-item>
        <a-descriptions-item label="装备类型">
          <a-tag color="blue">{{ viewRecord.equipmentType }}</a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="规格型号">
          {{ viewRecord.specification || '-' }}
        </a-descriptions-item>
        <a-descriptions-item label="数量">
          <span style="font-weight: 600">{{ viewRecord.quantity }}</span>
        </a-descriptions-item>
        <a-descriptions-item label="供应商">
          {{ viewRecord.supplier || '-' }}
        </a-descriptions-item>
        <a-descriptions-item label="仓库">
          {{ viewRecord.warehouse || '-' }}
        </a-descriptions-item>
        <a-descriptions-item label="存放位置">
          {{ viewRecord.location || '-' }}
        </a-descriptions-item>
        <a-descriptions-item label="入库时间">
          {{ viewRecord.inboundTime || '-' }}
        </a-descriptions-item>
        <a-descriptions-item label="状态">
          <a-tag v-if="viewRecord.status === 'pending'" color="orange">
            {{ $t('equipment.inbound.form.status.pending') }}
          </a-tag>
          <a-tag v-else-if="viewRecord.status === 'completed'" color="green">
            {{ $t('equipment.inbound.form.status.completed') }}
          </a-tag>
          <a-tag v-else color="red">
            {{ $t('equipment.inbound.form.status.rejected') }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="备注" :span="2">
          <div style="white-space: pre-wrap; word-break: break-word">
            {{ viewRecord.remark || '-' }}
          </div>
        </a-descriptions-item>
      </a-descriptions>
    </a-modal>

    <!-- 编辑/创建模态框 -->
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
            <a-form-item label="装备编号">
              <a-input value="系统自动生成" disabled />
              <template #extra>
                <span style="color: var(--color-text-3); font-size: 12px">
                  装备编号将由系统自动生成。如数量大于1，系统会自动为每个设备生成唯一编码（如：EQ000001,
                  EQ000002...）
                </span>
              </template>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item
              field="equipmentName"
              label="装备名称"
              :rules="[{ required: true, message: '请输入装备名称' }]"
            >
              <a-input
                v-model="form.equipmentName"
                placeholder="请输入装备名称"
              />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item
              field="equipmentType"
              label="装备类型"
              :rules="[{ required: true, message: '请选择装备类型' }]"
            >
              <a-select
                v-model="form.equipmentType"
                :options="equipmentTypeOptions"
                placeholder="请选择装备类型"
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
            <a-form-item field="specification" label="规格型号">
              <a-input
                v-model="form.specification"
                placeholder="请输入规格说明"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item field="supplier" label="供应商">
              <a-input v-model="form.supplier" placeholder="请输入供应商" />
            </a-form-item>
          </a-col>
        </a-row>

        <!-- 存储信息 -->
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
            >存储信息</span
          >
        </a-divider>
        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item field="warehouse" label="仓库">
              <a-input v-model="form.warehouse" placeholder="请输入仓库名称" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item field="location" label="存放位置">
              <a-input
                v-model="form.location"
                placeholder="请输入具体存放位置"
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
  </div>
</template>

<script lang="ts" setup>
  import { computed, ref, reactive } from 'vue';
  import { useI18n } from 'vue-i18n';
  import { Message } from '@arco-design/web-vue';
  import type { FormInstance } from '@arco-design/web-vue';
  import useLoading from '@/hooks/loading';
  import {
    queryEquipmentInboundList,
    createEquipmentInbound,
  } from '@/api/equipment';
  import { Pagination } from '@/types/global';
  import type { SelectOptionData } from '@arco-design/web-vue/es/select/interface';
  import type { TableColumnData } from '@arco-design/web-vue/es/table/interface';

  const generateFormModel = () => {
    return {
      equipmentCode: '',
      equipmentName: '',
      equipmentType: '',
      supplier: '',
      inboundTime: [],
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

  const equipmentTypeOptions = computed<SelectOptionData[]>(() => [
    { label: '起重机', value: '起重机' },
    { label: '叉车', value: '叉车' },
    { label: '集装箱', value: '集装箱' },
    { label: '装卸机', value: '装卸机' },
    { label: '牵引车', value: '牵引车' },
    { label: '堆高机', value: '堆高机' },
  ]);

  const statusOptions = computed<SelectOptionData[]>(() => [
    { label: t('equipment.inbound.form.status.pending'), value: 'pending' },
    { label: t('equipment.inbound.form.status.completed'), value: 'completed' },
    { label: t('equipment.inbound.form.status.rejected'), value: 'rejected' },
  ]);

  const columns = computed<TableColumnData[]>(() => [
    {
      title: t('equipment.inbound.columns.index'),
      dataIndex: 'index',
      slotName: 'index',
    },
    {
      title: t('equipment.inbound.columns.equipmentCode'),
      dataIndex: 'equipmentCode',
    },
    {
      title: t('equipment.inbound.columns.equipmentName'),
      dataIndex: 'equipmentName',
    },
    {
      title: t('equipment.inbound.columns.equipmentType'),
      dataIndex: 'equipmentType',
    },
    {
      title: t('equipment.inbound.columns.quantity'),
      dataIndex: 'quantity',
    },
    {
      title: t('equipment.inbound.columns.supplier'),
      dataIndex: 'supplier',
    },
    {
      title: t('equipment.inbound.columns.warehouse'),
      dataIndex: 'warehouse',
    },
    {
      title: t('equipment.inbound.columns.inboundTime'),
      dataIndex: 'inboundTime',
    },
    {
      title: t('equipment.inbound.columns.status'),
      dataIndex: 'status',
      slotName: 'status',
    },
    {
      title: t('equipment.inbound.columns.operations'),
      dataIndex: 'operations',
      slotName: 'operations',
    },
  ]);

  const fetchData = async (params: any = { current: 1, pageSize: 20 }) => {
    setLoading(true);
    try {
      console.log('请求入库列表，参数:', params);
      const response = await queryEquipmentInboundList(params);
      console.log('入库列表响应:', response);

      // 处理不同的响应格式
      const responseData = response.data || response;
      console.log('处理后的响应数据:', responseData);

      // 后端返回格式: { code: 200, message: "success", list: [...], total: ... }
      if (responseData && responseData.list) {
        renderData.value = responseData.list;
        pagination.current = params.current || 1;
        pagination.total = responseData.total || 0;
        console.log('入库列表数据已更新，共', responseData.list.length, '条');
      } else {
        console.warn('响应数据格式不正确:', responseData);
        renderData.value = [];
        pagination.total = 0;
      }
    } catch (err: any) {
      console.error('获取入库列表失败:', err);
      Message.error(
        err?.response?.data?.detail || err?.message || '获取入库列表失败'
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
    if (formModel.value.equipmentCode) {
      searchParams.equipmentCode = formModel.value.equipmentCode;
    }
    if (formModel.value.equipmentName) {
      searchParams.equipmentName = formModel.value.equipmentName;
    }
    if (formModel.value.equipmentType) {
      searchParams.equipmentType = formModel.value.equipmentType;
    }
    if (formModel.value.supplier) {
      searchParams.supplier = formModel.value.supplier;
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
    modalTitle.value = t('equipment.inbound.operation.create');
    form.value = {
      equipmentName: '',
      equipmentType: '',
      specification: '',
      quantity: 1,
      supplier: '',
      warehouse: '',
      location: '',
      remark: '',
    };
    // 重置表单验证状态
    formRef.value?.resetFields();
    modalVisible.value = true;
  };

  const handleEdit = (record: any) => {
    modalTitle.value = t('equipment.inbound.operation.edit');
    form.value = { ...record };
    modalVisible.value = true;
  };

  const handleView = (record: any) => {
    viewRecord.value = { ...record };
    viewModalVisible.value = true;
  };

  const handleSubmit = async () => {
    if (!formRef.value) {
      return false;
    }

    try {
      // 表单验证
      await formRef.value.validate();

      // 准备提交数据，不包含equipmentCode（由后端自动生成）
      const submitData = { ...form.value };
      // 确保不传递equipmentCode字段
      delete submitData.equipmentCode;

      console.log('提交入库数据:', submitData);
      const response = await createEquipmentInbound(submitData);
      console.log('入库响应:', response);

      Message.success('设备入库成功');
      modalVisible.value = false;
      formRef.value?.resetFields();

      // 刷新列表
      fetchData();
      return true;
    } catch (err: any) {
      console.error('入库失败:', err);
      // 如果是表单验证错误，Arco Design 会自动显示错误信息
      if (err?.errors) {
        console.log('表单验证错误:', err.errors);
        return false;
      }
      // API 错误
      const errorMessage =
        err?.response?.data?.detail || err?.message || '设备入库失败';
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
    name: 'EquipmentInbound',
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
