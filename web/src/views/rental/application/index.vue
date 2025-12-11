<template>
  <div class="container">
    <Breadcrumb :items="['menu.rental', 'menu.rental.application']" />
    <a-card class="general-card" :title="$t('rental.application.title')">
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
                  field="applicationCode"
                  :label="$t('rental.application.form.applicationCode')"
                >
                  <a-input
                    v-model="formModel.applicationCode"
                    :placeholder="
                      $t('rental.application.form.applicationCode.placeholder')
                    "
                  />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item
                  field="applicant"
                  :label="$t('rental.application.form.applicant')"
                >
                  <a-input
                    v-model="formModel.applicant"
                    :placeholder="
                      $t('rental.application.form.applicant.placeholder')
                    "
                  />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item
                  field="equipmentType"
                  :label="$t('rental.application.form.equipmentType')"
                >
                  <a-select
                    v-model="formModel.equipmentType"
                    :options="equipmentTypeOptions"
                    :placeholder="$t('rental.application.form.selectDefault')"
                  />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item
                  field="applicationTime"
                  :label="$t('rental.application.form.applicationTime')"
                >
                  <a-range-picker
                    v-model="formModel.applicationTime"
                    style="width: 100%"
                  />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item
                  field="status"
                  :label="$t('rental.application.form.status')"
                >
                  <a-select
                    v-model="formModel.status"
                    :options="statusOptions"
                    :placeholder="$t('rental.application.form.selectDefault')"
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
              {{ $t('rental.application.form.search') }}
            </a-button>
            <a-button @click="reset">
              <template #icon>
                <icon-refresh />
              </template>
              {{ $t('rental.application.form.reset') }}
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
              {{ $t('rental.application.operation.create') }}
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
            {{ $t('rental.application.operation.download') }}
          </a-button>
          <a-tooltip :content="$t('rental.application.actions.refresh')">
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
            {{ $t('rental.application.form.status.pending') }}
          </a-tag>
          <a-tag v-else-if="record.status === 'approved'" color="green">
            {{ $t('rental.application.form.status.approved') }}
          </a-tag>
          <a-tag v-else-if="record.status === 'rejected'" color="red">
            {{ $t('rental.application.form.status.rejected') }}
          </a-tag>
          <a-tag v-else color="blue">
            {{ $t('rental.application.form.status.completed') }}
          </a-tag>
        </template>
        <template #operations="{ record }">
          <a-button type="text" size="small" @click="handleView(record)">
            {{ $t('rental.application.columns.operations.view') }}
          </a-button>
          <a-button
            v-if="record.status === 'pending'"
            type="text"
            size="small"
            @click="handleApprove(record)"
          >
            {{ $t('rental.application.columns.operations.approve') }}
          </a-button>
          <a-button
            v-if="record.status === 'pending'"
            type="text"
            size="small"
            @click="handleReject(record)"
          >
            {{ $t('rental.application.columns.operations.reject') }}
          </a-button>
        </template>
      </a-table>
    </a-card>
    <!-- 创建/查看模态框 -->
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
              field="applicant"
              label="申请人"
              :rules="[{ required: true, message: '请输入申请人' }]"
            >
              <a-input
                v-model="form.applicant"
                placeholder="请输入申请人姓名"
              />
            </a-form-item>
          </a-col>
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
        </a-row>
        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item field="equipmentType" label="装备类型">
              <a-select
                v-model="form.equipmentType"
                :options="equipmentTypeOptions"
                placeholder="请选择装备类型（可选）"
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

        <!-- 租赁信息 -->
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
            >租赁信息</span
          >
        </a-divider>
        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item
              field="startDate"
              label="开始日期"
              :rules="[{ required: true, message: '请选择开始日期' }]"
            >
              <a-date-picker
                v-model="form.startDate"
                style="width: 100%"
                placeholder="请选择开始日期"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item
              field="endDate"
              label="结束日期"
              :rules="[{ required: true, message: '请选择结束日期' }]"
            >
              <a-date-picker
                v-model="form.endDate"
                style="width: 100%"
                placeholder="请选择结束日期"
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
              field="purpose"
              label="用途说明"
              :label-col-props="{ span: 3 }"
              :wrapper-col-props="{ span: 21 }"
            >
              <a-textarea
                v-model="form.purpose"
                :rows="3"
                placeholder="请输入用途说明（可选）"
              />
            </a-form-item>
          </a-col>
        </a-row>
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
    queryRentalApplicationList,
    createRentalApplication,
    approveRentalApplication,
    rejectRentalApplication,
  } from '@/api/rental';
  import { Pagination } from '@/types/global';
  import type { SelectOptionData } from '@arco-design/web-vue/es/select/interface';
  import type { TableColumnData } from '@arco-design/web-vue/es/table/interface';

  const generateFormModel = () => {
    return {
      applicationCode: '',
      applicant: '',
      equipmentType: '',
      applicationTime: [],
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

  const basePagination: Pagination = {
    current: 1,
    pageSize: 20,
  };
  const pagination = reactive({
    ...basePagination,
    total: 0,
  });

  const equipmentTypeOptions = computed<SelectOptionData[]>(() => [
    { label: t('rental.application.form.equipmentType.crane'), value: 'crane' },
    {
      label: t('rental.application.form.equipmentType.forklift'),
      value: 'forklift',
    },
    {
      label: t('rental.application.form.equipmentType.container'),
      value: 'container',
    },
    { label: t('rental.application.form.equipmentType.other'), value: 'other' },
  ]);

  const statusOptions = computed<SelectOptionData[]>(() => [
    { label: t('rental.application.form.status.pending'), value: 'pending' },
    { label: t('rental.application.form.status.approved'), value: 'approved' },
    { label: t('rental.application.form.status.rejected'), value: 'rejected' },
    {
      label: t('rental.application.form.status.completed'),
      value: 'completed',
    },
  ]);

  const columns = computed<TableColumnData[]>(() => [
    {
      title: t('rental.application.columns.index'),
      dataIndex: 'index',
      slotName: 'index',
    },
    {
      title: t('rental.application.columns.applicationCode'),
      dataIndex: 'applicationCode',
    },
    {
      title: t('rental.application.columns.applicant'),
      dataIndex: 'applicant',
    },
    {
      title: t('rental.application.columns.equipmentType'),
      dataIndex: 'equipmentType',
    },
    {
      title: t('rental.application.columns.equipmentCode'),
      dataIndex: 'equipmentCode',
    },
    {
      title: t('rental.application.columns.quantity'),
      dataIndex: 'quantity',
    },
    {
      title: t('rental.application.columns.startDate'),
      dataIndex: 'startDate',
    },
    {
      title: t('rental.application.columns.endDate'),
      dataIndex: 'endDate',
    },
    {
      title: t('rental.application.columns.applicationTime'),
      dataIndex: 'applicationTime',
    },
    {
      title: t('rental.application.columns.status'),
      dataIndex: 'status',
      slotName: 'status',
    },
    {
      title: t('rental.application.columns.operations'),
      dataIndex: 'operations',
      slotName: 'operations',
    },
  ]);

  const fetchData = async (params: any = { current: 1, pageSize: 20 }) => {
    setLoading(true);
    try {
      console.log('请求租赁申请列表，参数:', params);
      const response = await queryRentalApplicationList(params);
      console.log('租赁申请列表响应:', response);

      // 处理不同的响应格式
      const responseData = response.data || response;
      console.log('处理后的响应数据:', responseData);

      // 后端返回格式: { code: 200, message: "success", list: [...], total: ... }
      if (responseData && responseData.list) {
        renderData.value = responseData.list;
        pagination.current = params.current || 1;
        pagination.total = responseData.total || 0;
        console.log(
          '租赁申请列表数据已更新，共',
          responseData.list.length,
          '条'
        );
      } else {
        console.warn('响应数据格式不正确:', responseData);
        renderData.value = [];
        pagination.total = 0;
      }
    } catch (err: any) {
      console.error('获取租赁申请列表失败:', err);
      Message.error(
        err?.response?.data?.detail || err?.message || '获取租赁申请列表失败'
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
    if (formModel.value.applicationCode) {
      searchParams.applicationCode = formModel.value.applicationCode;
    }
    if (formModel.value.applicant) {
      searchParams.applicant = formModel.value.applicant;
    }
    if (formModel.value.equipmentType) {
      searchParams.equipmentType = formModel.value.equipmentType;
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
    modalTitle.value = t('rental.application.operation.create');
    form.value = {
      applicant: '',
      equipmentType: '',
      equipmentCode: '',
      quantity: 1,
      startDate: new Date(),
      endDate: null,
      purpose: '',
      remark: '',
    };
    modalVisible.value = true;
  };

  const handleView = (record: any) => {
    modalTitle.value = t('rental.application.operation.view');
    form.value = { ...record };
    modalVisible.value = true;
  };

  const handleApprove = async (record: any) => {
    try {
      await approveRentalApplication(record.id);
      Message.success('审批成功');
      fetchData();
    } catch (err: any) {
      console.error('审批失败:', err);
      Message.error(err?.response?.data?.detail || err?.message || '审批失败');
    }
  };

  const handleReject = async (record: any) => {
    try {
      await rejectRentalApplication(record.id);
      Message.success('已拒绝申请');
      fetchData();
    } catch (err: any) {
      console.error('拒绝申请失败:', err);
      Message.error(
        err?.response?.data?.detail || err?.message || '拒绝申请失败'
      );
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
        applicant: form.value.applicant?.trim(),
        equipmentCode: form.value.equipmentCode?.trim(),
        quantity: form.value.quantity || 1,
        purpose: form.value.purpose?.trim() || '',
        remark: form.value.remark?.trim() || '',
      };

      // 添加装备类型（如果有）
      if (form.value.equipmentType) {
        submitData.equipmentType = form.value.equipmentType;
      }

      // 处理日期
      if (form.value.startDate) {
        if (form.value.startDate instanceof Date) {
          const [datePart] = form.value.startDate
            .toISOString()
            .split('T');
          submitData.startDate = datePart;
        } else if (typeof form.value.startDate === 'string') {
          const [datePart] = form.value.startDate.split('T');
          submitData.startDate = datePart;
        }
      }

      if (form.value.endDate) {
        if (form.value.endDate instanceof Date) {
          const [datePart] = form.value.endDate.toISOString().split('T');
          submitData.endDate = datePart;
        } else if (typeof form.value.endDate === 'string') {
          const [datePart] = form.value.endDate.split('T');
          submitData.endDate = datePart;
        }
      }

      console.log('提交租赁申请数据:', submitData);
      const response = await createRentalApplication(submitData);
      console.log('租赁申请响应:', response);

      Message.success('租赁申请提交成功');

      modalVisible.value = false;
      formRef.value?.resetFields();
      // 重置搜索条件并刷新到第一页
      formModel.value = generateFormModel();
      fetchData({ current: 1, pageSize: basePagination.pageSize });
      return true;
    } catch (err: any) {
      console.error('提交租赁申请失败:', err);
      // 如果是表单验证错误，Arco Design 会自动显示错误信息
      if (err?.errors) {
        console.log('表单验证错误:', err.errors);
        return false;
      }
      // API 错误
      const errorMessage =
        err?.response?.data?.detail || err?.message || '提交失败';
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
    name: 'RentalApplication',
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
