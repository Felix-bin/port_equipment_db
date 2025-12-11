<template>
  <div class="container">
    <Breadcrumb :items="['menu.equipment', 'menu.equipment.inventory']" />
    <a-card class="general-card">
      <template #title>
        <a-space>
          <icon-storage />
          <span>{{ $t('equipment.inventory.title') }}</span>
        </a-space>
      </template>
      <a-row style="margin-bottom: 16px">
        <a-col :span="12">
          <a-space>
            <a-input-search
              :placeholder="$t('equipment.inventory.search.placeholder')"
              style="width: 300px"
              @search="handleSearch"
            />
            <a-select
              v-model="categoryFilter"
              :placeholder="$t('equipment.inventory.filter.category')"
              style="width: 150px"
              @change="handleFilter"
            >
              <a-option value="all">全部类型</a-option>
              <a-option value="起重机">起重机</a-option>
              <a-option value="叉车">叉车</a-option>
              <a-option value="集装箱">集装箱</a-option>
              <a-option value="装卸机">装卸机</a-option>
              <a-option value="牵引车">牵引车</a-option>
              <a-option value="堆高机">堆高机</a-option>
            </a-select>
          </a-space>
        </a-col>
        <a-col :span="12" style="text-align: right">
          <a-space>
            <a-button type="primary" @click="handleAdd">
              <template #icon>
                <icon-plus />
              </template>
              {{ $t('equipment.inventory.add') }}
            </a-button>
          </a-space>
        </a-col>
      </a-row>

      <a-spin :loading="loading" style="width: 100%; min-height: 400px">
        <a-row class="list-row" :gutter="16">
          <a-col
            v-for="item in equipmentList"
            :key="item.id"
            :xs="24"
            :sm="12"
            :md="12"
            :lg="8"
            :xl="6"
            :xxl="6"
            class="list-col"
          >
            <a-card class="equipment-card" hoverable>
              <a-card-meta>
                <template #title>
                  <div
                    style="
                      display: flex;
                      justify-content: space-between;
                      align-items: center;
                    "
                  >
                    <span>{{ item.name }}</span>
                    <a-tag
                      :color="
                        item.status === 'available'
                          ? 'green'
                          : item.status === 'rented'
                          ? 'orange'
                          : 'red'
                      "
                      class="status-tag"
                    >
                      {{ getStatusText(item.status) }}
                    </a-tag>
                  </div>
                </template>
                <template #description>
                  <a-space direction="vertical" :size="8" fill>
                    <div class="info-item">
                      <icon-user />
                      <span
                        >{{ $t('equipment.inventory.code') }}:
                        {{ item.code }}</span
                      >
                    </div>
                    <div class="info-item">
                      <icon-location />
                      <span
                        >{{ $t('equipment.inventory.location') }}:
                        {{ item.location }}</span
                      >
                    </div>
                    <div class="info-item">
                      <icon-calendar />
                      <span
                        >{{ $t('equipment.inventory.inboundDate') }}:
                        {{ item.inboundDate }}</span
                      >
                    </div>
                    <a-divider :margin="8" />
                    <div class="price-info">
                      <span class="price">¥{{ item.dailyRate }}</span>
                      <span class="unit">/天</span>
                    </div>
                  </a-space>
                </template>
              </a-card-meta>
              <template #actions>
                <span class="action-btn" @click="handleView(item)">
                  <icon-eye />
                  查看
                </span>
                <span class="action-btn" @click="handleEdit(item)">
                  <icon-edit />
                  编辑
                </span>
                <span
                  class="action-btn action-btn-danger"
                  @click="handleDelete(item)"
                >
                  <icon-close-circle />
                  删除
                </span>
              </template>
            </a-card>
          </a-col>
        </a-row>
      </a-spin>

      <a-row style="margin-top: 20px">
        <a-col :span="24" style="display: flex; justify-content: flex-end">
          <a-pagination
            :total="total"
            :page-size="pageSize"
            :current="currentPage"
            show-total
            show-jumper
            show-page-size
            @change="handlePageChange"
            @page-size-change="handlePageSizeChange"
          />
        </a-col>
      </a-row>
    </a-card>

    <!-- 查看模态框 -->
    <a-modal
      v-model:visible="viewModalVisible"
      :title="'查看设备详情'"
      width="600px"
      :footer="false"
    >
      <a-descriptions v-if="currentEquipment" :column="2" bordered>
        <a-descriptions-item label="设备名称">
          {{ currentEquipment.name }}
        </a-descriptions-item>
        <a-descriptions-item label="设备编码">
          {{ currentEquipment.code }}
        </a-descriptions-item>
        <a-descriptions-item label="设备类型">
          {{ currentEquipment.category }}
        </a-descriptions-item>
        <a-descriptions-item label="状态">
          <a-tag
            :color="
              currentEquipment.status === 'available'
                ? 'green'
                : currentEquipment.status === 'rented'
                ? 'orange'
                : 'red'
            "
          >
            {{ getStatusText(currentEquipment.status) }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="存储位置">
          {{ currentEquipment.location }}
        </a-descriptions-item>
        <a-descriptions-item label="入库日期">
          {{ currentEquipment.inboundDate }}
        </a-descriptions-item>
        <a-descriptions-item label="日租金" :span="2">
          <span class="price">¥{{ currentEquipment.dailyRate }}</span>
          <span class="unit">/天</span>
        </a-descriptions-item>
      </a-descriptions>
    </a-modal>

    <!-- 编辑模态框 -->
    <a-modal
      v-model:visible="editModalVisible"
      :title="'编辑设备信息'"
      width="600px"
      @before-ok="handleSubmitEdit"
      @cancel="handleCancelEdit"
    >
      <a-form
        ref="editFormRef"
        :model="editForm"
        :label-col-props="{ span: 6 }"
        :wrapper-col-props="{ span: 18 }"
      >
        <a-form-item
          field="name"
          label="设备名称"
          :rules="[{ required: true, message: '请输入设备名称' }]"
        >
          <a-input v-model="editForm.name" placeholder="请输入设备名称" />
        </a-form-item>
        <a-form-item field="code" label="设备编码">
          <a-input
            v-model="editForm.code"
            placeholder="请输入设备编码"
            disabled
          />
        </a-form-item>
        <a-form-item
          field="category"
          label="设备类型"
          :rules="[{ required: true, message: '请选择设备类型' }]"
        >
          <a-select v-model="editForm.category" placeholder="请选择设备类型">
            <a-option value="起重机">起重机</a-option>
            <a-option value="叉车">叉车</a-option>
            <a-option value="集装箱">集装箱</a-option>
            <a-option value="装卸机">装卸机</a-option>
            <a-option value="牵引车">牵引车</a-option>
            <a-option value="堆高机">堆高机</a-option>
          </a-select>
        </a-form-item>
        <a-form-item
          field="status"
          label="状态"
          :rules="[{ required: true, message: '请选择状态' }]"
        >
          <a-select v-model="editForm.status" placeholder="请选择状态">
            <a-option value="available">可租赁</a-option>
            <a-option value="rented">租赁中</a-option>
            <a-option value="maintenance">维护中</a-option>
          </a-select>
        </a-form-item>
        <a-form-item
          field="location"
          label="存储位置"
          :rules="[{ required: true, message: '请输入存储位置' }]"
        >
          <a-input v-model="editForm.location" placeholder="请输入存储位置" />
        </a-form-item>
        <a-form-item field="inboundDate" label="入库日期">
          <a-input v-model="editForm.inboundDate" disabled />
        </a-form-item>
        <a-form-item
          field="dailyRate"
          label="日租金"
          :rules="[
            { required: true, message: '请输入日租金' },
            { type: 'number', min: 0, message: '日租金必须大于等于0' },
          ]"
        >
          <a-input-number
            v-model="editForm.dailyRate"
            :min="0"
            :precision="2"
            placeholder="请输入日租金"
            style="width: 100%"
          >
            <template #prefix>¥</template>
          </a-input-number>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 添加设备模态框 -->
    <a-modal
      v-model:visible="addModalVisible"
      :title="'添加设备'"
      width="600px"
      @before-ok="handleSubmitAdd"
      @cancel="handleCancelAdd"
    >
      <a-form
        ref="addFormRef"
        :model="addForm"
        :label-col-props="{ span: 6 }"
        :wrapper-col-props="{ span: 18 }"
      >
        <a-form-item label="设备编码">
          <a-input value="系统自动生成" disabled />
          <template #extra>
            <span style="color: var(--color-text-3); font-size: 12px"
              >设备编码将由系统自动生成</span
            >
          </template>
        </a-form-item>
        <a-form-item
          field="equipment_name"
          label="设备名称"
          :rules="[{ required: true, message: '请输入设备名称' }]"
        >
          <a-input
            v-model="addForm.equipment_name"
            placeholder="请输入设备名称"
          />
        </a-form-item>
        <a-form-item
          field="category"
          label="设备类型"
          :rules="[{ required: true, message: '请选择设备类型' }]"
        >
          <a-select v-model="addForm.category" placeholder="请选择设备类型">
            <a-option value="起重机">起重机</a-option>
            <a-option value="叉车">叉车</a-option>
            <a-option value="集装箱">集装箱</a-option>
            <a-option value="装卸机">装卸机</a-option>
            <a-option value="牵引车">牵引车</a-option>
            <a-option value="堆高机">堆高机</a-option>
          </a-select>
        </a-form-item>
        <a-form-item
          field="storage_location"
          label="存储位置"
          :rules="[{ required: true, message: '请输入存储位置' }]"
        >
          <a-input
            v-model="addForm.storage_location"
            placeholder="请输入存储位置"
          />
        </a-form-item>
        <a-form-item
          field="daily_rental_rate"
          label="日租金"
          :rules="[
            { required: true, message: '请输入日租金' },
            { type: 'number', min: 0, message: '日租金必须大于等于0' },
          ]"
        >
          <a-input-number
            v-model="addForm.daily_rental_rate"
            :min="0"
            :precision="2"
            placeholder="请输入日租金"
            style="width: 100%"
          >
            <template #prefix>¥</template>
          </a-input-number>
        </a-form-item>
        <a-form-item
          field="purchase_price"
          label="采购价格"
          :rules="[
            { type: 'number', min: 0, message: '采购价格必须大于等于0' },
          ]"
        >
          <a-input-number
            v-model="addForm.purchase_price"
            :min="0"
            :precision="2"
            placeholder="请输入采购价格"
            style="width: 100%"
          >
            <template #prefix>¥</template>
          </a-input-number>
        </a-form-item>
        <a-form-item field="specifications" label="规格说明">
          <a-textarea
            v-model="addForm.specifications"
            placeholder="请输入规格说明"
            :rows="3"
          />
        </a-form-item>
        <a-form-item field="remarks" label="备注">
          <a-textarea
            v-model="addForm.remarks"
            placeholder="请输入备注信息"
            :rows="3"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
  import { ref, onMounted, watch } from 'vue';
  import { Message, Modal } from '@arco-design/web-vue';
  import {
    queryEquipmentInventoryList,
    updateEquipment,
    deleteEquipment,
    createEquipment,
    type EquipmentInventoryRecord,
  } from '@/api/equipment';
  import type { FormInstance } from '@arco-design/web-vue';

  interface Equipment {
    id: string;
    name: string;
    code: string;
    category: string;
    status: 'available' | 'rented' | 'maintenance';
    location: string;
    inboundDate: string;
    dailyRate: number;
  }

  const categoryFilter = ref('all');
  const currentPage = ref(1);
  const pageSize = ref(12);
  const total = ref(0);
  const loading = ref(false);
  const searchKeyword = ref('');

  const equipmentList = ref<Equipment[]>([]);

  // 查看模态框相关
  const viewModalVisible = ref(false);
  const currentEquipment = ref<Equipment | null>(null);

  // 编辑模态框相关
  const editModalVisible = ref(false);
  const editFormRef = ref<FormInstance>();
  const editForm = ref<Partial<Equipment>>({
    id: '',
    name: '',
    code: '',
    category: '',
    status: 'available',
    location: '',
    inboundDate: '',
    dailyRate: 0,
  });

  // 添加模态框相关
  const addModalVisible = ref(false);
  const addFormRef = ref<FormInstance>();
  const addForm = ref({
    equipment_name: '',
    category: '',
    storage_location: '',
    daily_rental_rate: 0,
    purchase_price: 0,
    specifications: '',
    remarks: '',
  });

  const fetchEquipmentList = async () => {
    loading.value = true;
    try {
      console.log('正在请求设备列表...', {
        current: currentPage.value,
        pageSize: pageSize.value,
        equipmentType:
          categoryFilter.value === 'all' ? undefined : categoryFilter.value,
        keyword: searchKeyword.value || undefined,
      });

      const response = await queryEquipmentInventoryList({
        current: currentPage.value,
        pageSize: pageSize.value,
        equipmentType:
          categoryFilter.value === 'all' ? undefined : categoryFilter.value,
        keyword: searchKeyword.value || undefined,
      });

      console.log('API 响应:', response);

      // 处理响应数据 - 兼容不同的响应格式
      const responseData = response.data || response;
      console.log('响应数据:', responseData);

      if (responseData && responseData.list) {
        equipmentList.value = responseData.list.map(
          (
            item: EquipmentInventoryRecord & {
              dailyRate?: number;
              inboundDate?: string;
            }
          ) => {
            console.log(
              '设备数据:',
              item.equipmentCode,
              '状态:',
              item.status,
              '日租金:',
              item.dailyRate
            );
            return {
              id: item.id,
              name: item.equipmentName,
              code: item.equipmentCode,
              category: item.equipmentType,
              status: item.status,
              location: item.location || item.warehouse,
              inboundDate:
                item.inboundDate || new Date().toISOString().split('T')[0],
              dailyRate: item.dailyRate || 0,
            };
          }
        );
        total.value = responseData.total || 0;
        console.log('设备列表已更新:', equipmentList.value.length, '条');
      } else {
        console.warn('没有找到 list 数据:', responseData);
      }
    } catch (error: any) {
      Message.error('获取设备列表失败');
      console.error('Failed to fetch equipment list:', error);
    } finally {
      loading.value = false;
    }
  };

  const getStatusText = (status: string) => {
    const statusMap: Record<string, string> = {
      available: '可租赁',
      rented: '租赁中',
      maintenance: '维护中',
    };
    return statusMap[status] || status;
  };

  const handleSearch = (value: string) => {
    searchKeyword.value = value;
    currentPage.value = 1;
    fetchEquipmentList();
  };

  const handleFilter = () => {
    currentPage.value = 1;
    fetchEquipmentList();
  };

  const handleAdd = () => {
    addForm.value = {
      equipment_name: '',
      category: '',
      storage_location: '',
      daily_rental_rate: 0,
      purchase_price: 0,
      specifications: '',
      remarks: '',
    };
    addModalVisible.value = true;
  };

  const handleSubmitAdd = async () => {
    if (!addFormRef.value) {
      Message.error('表单引用不存在');
      return false;
    }

    try {
      // Arco Design 的 validate 方法在验证失败时会抛出错误
      await addFormRef.value.validate();
      console.log('表单验证通过，准备提交设备数据:', addForm.value);

      const response = await createEquipment(addForm.value);
      console.log('设备创建响应:', response);

      Message.success('设备添加成功');
      addModalVisible.value = false;

      // 刷新列表
      await fetchEquipmentList();
      return true;
    } catch (error: any) {
      console.error('添加设备失败:', error);
      // 如果是表单验证错误，Arco Design 会自动显示错误信息
      if (error?.errors) {
        // 这是表单验证错误，Arco Design 已经显示了错误信息
        console.log('表单验证错误:', error.errors);
        return false;
      }
      // 这是 API 错误
      const errorMessage =
        error?.response?.data?.detail || error?.message || '添加设备失败';
      Message.error(errorMessage);
      return false;
    }
  };

  const handleCancelAdd = () => {
    addFormRef.value?.resetFields();
    addModalVisible.value = false;
  };

  const handleView = (item: Equipment) => {
    currentEquipment.value = item;
    viewModalVisible.value = true;
  };

  const handleEdit = (item: Equipment) => {
    currentEquipment.value = item;
    editForm.value = {
      id: item.id,
      name: item.name,
      code: item.code,
      category: item.category,
      status: item.status,
      location: item.location,
      inboundDate: item.inboundDate,
      dailyRate: item.dailyRate,
    };
    editModalVisible.value = true;
  };

  const handleSubmitEdit = async () => {
    console.log('开始编辑设备提交...');
    if (!editFormRef.value) {
      console.error('editFormRef 不存在');
      Message.error('表单引用不存在');
      return false;
    }

    try {
      console.log('验证表单...', editForm.value);
      // Arco Design 的 validate 方法在验证失败时会抛出错误
      await editFormRef.value.validate();
      console.log('表单验证通过');

      if (!editForm.value.id) {
        Message.error('设备ID不存在');
        return false;
      }

      // 转换前端状态到后端状态
      let backendStatus: string;
      if (editForm.value.status === 'available') {
        backendStatus = '在库';
      } else if (editForm.value.status === 'rented') {
        backendStatus = '已出库';
      } else {
        backendStatus = '维修中';
      }

      // 准备更新数据
      const updateData: any = {
        equipment_name: editForm.value.name,
        category: editForm.value.category,
        status: backendStatus,
        storage_location: editForm.value.location,
        daily_rental_rate: editForm.value.dailyRate,
      };

      console.log('准备提交更新数据:', updateData);
      const response = await updateEquipment(editForm.value.id, updateData);
      console.log('设备更新响应:', response);

      Message.success('设备信息更新成功');
      editModalVisible.value = false;

      // 刷新列表
      await fetchEquipmentList();
      return true;
    } catch (error: any) {
      console.error('更新设备失败:', error);
      // 如果是表单验证错误，Arco Design 会自动显示错误信息
      if (error?.errors) {
        // 这是表单验证错误，Arco Design 已经显示了错误信息
        console.log('表单验证错误:', error.errors);
        return false;
      }
      // 这是 API 错误
      const errorMessage =
        error?.response?.data?.detail || error?.message || '更新设备信息失败';
      Message.error(errorMessage);
      return false;
    }
  };

  const handleCancelEdit = () => {
    editFormRef.value?.resetFields();
    editModalVisible.value = false;
  };

  const handleDelete = (item: Equipment) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除设备"${item.name}"吗？此操作不可恢复。`,
      okText: '确认删除',
      cancelText: '取消',
      okButtonProps: {
        status: 'danger',
      },
      onOk: async () => {
        try {
          await deleteEquipment(item.id);
          Message.success('设备删除成功');
          // 刷新列表
          await fetchEquipmentList();
        } catch (error: any) {
          console.error('删除设备失败:', error);
          Message.error(error?.response?.data?.detail || '删除设备失败');
        }
      },
    });
  };

  const handlePageChange = (page: number) => {
    currentPage.value = page;
    fetchEquipmentList();
  };

  const handlePageSizeChange = (size: number) => {
    pageSize.value = size;
    currentPage.value = 1;
    fetchEquipmentList();
  };

  onMounted(() => {
    fetchEquipmentList();
  });
</script>

<script lang="ts">
  export default {
    name: 'EquipmentInventory',
  };
</script>

<style scoped lang="less">
  .container {
    padding: 0 20px 20px 20px;
  }

  .list-row {
    .list-col {
      margin-bottom: 16px;
    }
  }

  .equipment-card {
    height: 100%;
    transition: all 0.3s;

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    :deep(.arco-card-meta-title) {
      font-size: 16px;
      font-weight: 600;
      margin-bottom: 12px;
    }

    .info-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
      color: var(--color-text-2);

      .arco-icon {
        font-size: 14px;
        color: var(--color-text-3);
      }
    }

    .price-info {
      display: flex;
      align-items: baseline;
      gap: 4px;

      .price {
        font-size: 20px;
        font-weight: 600;
        color: rgb(var(--danger-6));
      }

      .unit {
        font-size: 13px;
        color: var(--color-text-3);
      }
    }

    .action-btn {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      cursor: pointer;
      color: rgb(var(--arcoblue-6));
      transition: all 0.3s;

      &:hover {
        color: rgb(var(--arcoblue-5));
      }

      &.action-btn-danger {
        color: rgb(var(--red-6));

        &:hover {
          color: rgb(var(--red-5));
        }
      }
    }
  }
</style>
