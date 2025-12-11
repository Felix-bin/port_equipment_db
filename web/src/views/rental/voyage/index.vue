<template>
  <div class="container">
    <Breadcrumb :items="['menu.rental', 'menu.rental.voyage']" />
    <a-card class="general-card" :title="$t('rental.voyage.title')">
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
                  field="voyageNumber"
                  :label="$t('rental.voyage.form.voyageNumber')"
                >
                  <a-input
                    v-model="formModel.voyageNumber"
                    :placeholder="
                      $t('rental.voyage.form.voyageNumber.placeholder')
                    "
                  />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item
                  field="vesselName"
                  :label="$t('rental.voyage.form.vesselName')"
                >
                  <a-input
                    v-model="formModel.vesselName"
                    :placeholder="
                      $t('rental.voyage.form.vesselName.placeholder')
                    "
                  />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item
                  field="rentalOrder"
                  :label="$t('rental.voyage.form.rentalOrder')"
                >
                  <a-input
                    v-model="formModel.rentalOrder"
                    :placeholder="
                      $t('rental.voyage.form.rentalOrder.placeholder')
                    "
                  />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item
                  field="voyageDate"
                  :label="$t('rental.voyage.form.voyageDate')"
                >
                  <a-range-picker
                    v-model="formModel.voyageDate"
                    style="width: 100%"
                  />
                </a-form-item>
              </a-col>
              <a-col :span="8">
                <a-form-item
                  field="status"
                  :label="$t('rental.voyage.form.status')"
                >
                  <a-select
                    v-model="formModel.status"
                    :options="statusOptions"
                    :placeholder="$t('rental.voyage.form.selectDefault')"
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
              {{ $t('rental.voyage.form.search') }}
            </a-button>
            <a-button @click="reset">
              <template #icon>
                <icon-refresh />
              </template>
              {{ $t('rental.voyage.form.reset') }}
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
              {{ $t('rental.voyage.operation.create') }}
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
            {{ $t('rental.voyage.operation.download') }}
          </a-button>
          <a-tooltip :content="$t('rental.voyage.actions.refresh')">
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
          <a-tag v-if="record.status === 'in-progress'" color="blue">
            {{ $t('rental.voyage.form.status.inProgress') }}
          </a-tag>
          <a-tag v-else-if="record.status === 'completed'" color="green">
            {{ $t('rental.voyage.form.status.completed') }}
          </a-tag>
          <a-tag v-else color="gray">
            {{ $t('rental.voyage.form.status.cancelled') }}
          </a-tag>
        </template>
        <template #operations="{ record }">
          <a-button type="text" size="small" @click="handleView(record)">
            {{ $t('rental.voyage.columns.operations.view') }}
          </a-button>
          <a-button
            v-if="record.status === 'in-progress'"
            type="text"
            size="small"
            @click="handleComplete(record)"
          >
            {{ $t('rental.voyage.columns.operations.complete') }}
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
              field="rentalOrder"
              :label="$t('rental.voyage.form.rentalOrder')"
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
              field="voyageNumber"
              :label="$t('rental.voyage.form.voyageNumber')"
              :rules="[{ required: true, message: '请输入航次号' }]"
            >
              <a-input v-model="form.voyageNumber" placeholder="请输入航次号" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item
              field="vesselName"
              :label="$t('rental.voyage.form.vesselName')"
            >
              <a-input
                v-model="form.vesselName"
                placeholder="请输入船舶名称（可选）"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item
              field="voyageDate"
              :label="$t('rental.voyage.form.voyageDate')"
            >
              <a-date-picker
                v-model="form.voyageDate"
                style="width: 100%"
                placeholder="请选择航次日期"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <!-- 使用信息 -->
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
            >使用信息</span
          >
        </a-divider>
        <a-row :gutter="24">
          <a-col :span="12">
            <a-form-item
              field="usageHours"
              :label="$t('rental.voyage.form.usageHours')"
            >
              <a-input-number
                v-model="form.usageHours"
                :min="0"
                placeholder="请输入使用小时数"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="24">
          <a-col :span="24">
            <a-form-item
              field="equipmentList"
              :label="$t('rental.voyage.form.equipmentList')"
              :label-col-props="{ span: 3 }"
              :wrapper-col-props="{ span: 21 }"
            >
              <a-textarea
                v-model="form.equipmentList"
                :rows="3"
                placeholder="请输入装备列表（可选）"
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
    queryRentalVoyageList,
    createRentalVoyage,
    completeRentalVoyage,
  } from '@/api/rental';
  import { Pagination } from '@/types/global';
  import type { SelectOptionData } from '@arco-design/web-vue/es/select/interface';
  import type { TableColumnData } from '@arco-design/web-vue/es/table/interface';

  const generateFormModel = () => {
    return {
      voyageNumber: '',
      vesselName: '',
      rentalOrder: '',
      voyageDate: [],
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

  const statusOptions = computed<SelectOptionData[]>(() => [
    { label: t('rental.voyage.form.status.inProgress'), value: 'in-progress' },
    { label: t('rental.voyage.form.status.completed'), value: 'completed' },
    { label: t('rental.voyage.form.status.cancelled'), value: 'cancelled' },
  ]);

  const columns = computed<TableColumnData[]>(() => [
    {
      title: t('rental.voyage.columns.index'),
      dataIndex: 'index',
      slotName: 'index',
    },
    {
      title: t('rental.voyage.columns.voyageNumber'),
      dataIndex: 'voyageNumber',
    },
    {
      title: t('rental.voyage.columns.rentalOrder'),
      dataIndex: 'rentalOrder',
    },
    {
      title: t('rental.voyage.columns.vesselName'),
      dataIndex: 'vesselName',
    },
    {
      title: t('rental.voyage.columns.equipmentList'),
      dataIndex: 'equipmentList',
    },
    {
      title: t('rental.voyage.columns.usageHours'),
      dataIndex: 'usageHours',
    },
    {
      title: t('rental.voyage.columns.voyageDate'),
      dataIndex: 'voyageDate',
    },
    {
      title: t('rental.voyage.columns.status'),
      dataIndex: 'status',
      slotName: 'status',
    },
    {
      title: t('rental.voyage.columns.operations'),
      dataIndex: 'operations',
      slotName: 'operations',
    },
  ]);

  const fetchData = async (params: any = { current: 1, pageSize: 20 }) => {
    setLoading(true);
    try {
      console.log('请求航次列表，参数:', params);
      const response = await queryRentalVoyageList(params);
      console.log('航次列表响应:', response);

      // 处理不同的响应格式
      const responseData = response.data || response;
      console.log('处理后的响应数据:', responseData);

      // 后端返回格式: { code: 200, message: "success", list: [...], total: ... }
      if (responseData && responseData.list) {
        renderData.value = responseData.list;
        pagination.current = params.current || 1;
        pagination.total = responseData.total || 0;
        console.log('航次列表数据已更新，共', responseData.list.length, '条');
      } else {
        console.warn('响应数据格式不正确:', responseData);
        renderData.value = [];
        pagination.total = 0;
      }
    } catch (err: any) {
      console.error('获取航次列表失败:', err);
      Message.error(
        err?.response?.data?.detail || err?.message || '获取航次列表失败'
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
    if (formModel.value.voyageNumber) {
      searchParams.voyageNumber = formModel.value.voyageNumber;
    }
    if (formModel.value.vesselName) {
      searchParams.vesselName = formModel.value.vesselName;
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
    modalTitle.value = t('rental.voyage.operation.create');
    form.value = {
      rentalOrder: '',
      voyageNumber: '',
      vesselName: '',
      voyageDate: new Date(),
      equipmentList: '',
      usageHours: 0,
      remark: '',
    };
    modalVisible.value = true;
  };

  const handleView = (record: any) => {
    modalTitle.value = t('rental.voyage.operation.view');
    form.value = { ...record };
    modalVisible.value = true;
  };

  const handleComplete = async (record: any) => {
    try {
      await completeRentalVoyage(record.id);
      Message.success('航次已完成');
      fetchData();
    } catch (err: any) {
      console.error('完成航次失败:', err);
      Message.error(
        err?.response?.data?.detail || err?.message || '完成航次失败'
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
        rentalOrder: form.value.rentalOrder?.trim(),
        voyageNumber: form.value.voyageNumber?.trim(),
        vesselName: form.value.vesselName?.trim() || '',
        equipmentList: form.value.equipmentList?.trim() || '',
        usageHours: form.value.usageHours || 0,
        remark: form.value.remark?.trim() || '',
      };

      // 处理航次日期
      if (form.value.voyageDate) {
        if (form.value.voyageDate instanceof Date) {
          const [datePart] = form.value.voyageDate
            .toISOString()
            .split('T');
          submitData.voyageDate = datePart;
        } else if (typeof form.value.voyageDate === 'string') {
          const [datePart] = form.value.voyageDate.split('T');
          submitData.voyageDate = datePart;
        }
      }

      // 验证必填字段
      if (!submitData.rentalOrder) {
        Message.error('请输入租赁订单号');
        return false;
      }
      if (!submitData.voyageNumber) {
        Message.error('请输入航次号');
        return false;
      }

      console.log('提交航次数据:', submitData);
      const response = await createRentalVoyage(submitData);
      console.log('航次响应:', response);

      Message.success('航次创建成功');
      modalVisible.value = false;
      formRef.value?.resetFields();
      // 重置搜索条件并刷新到第一页
      formModel.value = generateFormModel();
      fetchData({ current: 1, pageSize: basePagination.pageSize });
      return true;
    } catch (err: any) {
      console.error('提交航次失败:', err);
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
    name: 'RentalVoyage',
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
