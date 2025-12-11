<template>
  <a-spin :loading="loading" style="width: 100%">
    <a-card class="general-card" :header-style="{ paddingBottom: '14px' }">
      <template #title>
        {{ $t('dataAnalysis.popularAuthor') }}
      </template>
      <template #extra>
        <a-link>{{ $t('workplace.viewMore') }}</a-link>
      </template>
      <a-table
        :data="tableData.list"
        :pagination="false"
        :bordered="false"
        style="margin-bottom: 20px"
        :scroll="{ x: '100%', y: '350px' }"
      >
        <template #columns>
          <a-table-column
            :title="$t('dataAnalysis.popularAuthor.column.ranking')"
            data-index="ranking"
          >
          </a-table-column>
          <a-table-column
            :title="$t('dataAnalysis.popularAuthor.column.author')"
            data-index="author"
          >
          </a-table-column>
          <a-table-column
            :title="$t('dataAnalysis.popularAuthor.column.content')"
            data-index="contentCount"
            :sortable="{
              sortDirections: ['ascend', 'descend'],
            }"
          >
          </a-table-column>
          <a-table-column
            :title="$t('dataAnalysis.popularAuthor.column.click')"
            data-index="clickCount"
            :sortable="{
              sortDirections: ['ascend', 'descend'],
            }"
          >
          </a-table-column>
        </template>
      </a-table>
    </a-card>
  </a-spin>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import useLoading from '@/hooks/loading';
  import { queryPopularAuthor, PopularAuthorRes } from '@/api/visualization';
  import { queryRentalAnalysis } from '@/api/rental';

  const { loading, setLoading } = useLoading();
  const tableData = ref<PopularAuthorRes>({ list: [] });
  const fetchData = async () => {
    try {
      setLoading(true);
      // 使用租赁分析 API
      const response = await queryRentalAnalysis();
      // 响应拦截器可能已经解构了数据
      const data = (response && typeof response === 'object' && 'popular_equipment' in response) ? response : (response?.data || null);
      
      if (data && data.popular_equipment && data.popular_equipment.length > 0) {
        const popularEquipment = data.popular_equipment;
        // 转换为表格数据格式
        tableData.value = {
          list: popularEquipment.map((item: any, index: number) => ({
            ranking: index + 1,
            author: item.equipment_name || '',
            contentCount: item.rental_count || 0,
            clickCount: item.rental_days || 0,
          })),
        };
      } else {
        // 如果没有数据，使用原来的 API
        const { data: originalData } = await queryPopularAuthor();
        tableData.value = originalData;
      }
    } catch (err) {
      console.error('获取数据失败:', err);
      // 出错时使用原来的 API
      try {
        const { data: originalData } = await queryPopularAuthor();
        tableData.value = originalData;
      } catch (fallbackErr) {
        console.error('备用 API 也失败:', fallbackErr);
        tableData.value = { list: [] };
      }
    } finally {
      setLoading(false);
    }
  };
  fetchData();
</script>

<style scoped lang="less">
  .general-card {
    max-height: 425px;
  }
</style>
