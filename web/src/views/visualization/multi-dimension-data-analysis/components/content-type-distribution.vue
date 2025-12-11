<template>
  <a-card
    class="general-card"
    :title="$t('multiDAnalysis.card.title.contentTypeDistribution')"
    :header-style="{ paddingBottom: 0 }"
  >
    <Chart style="height: 222px" :option="chartOption" />
  </a-card>
</template>

<script lang="ts" setup>
  import { ref, onMounted } from 'vue';
  import useChartOption from '@/hooks/chart-option';
  import { queryMultiDimensionAnalysis } from '@/api/visualization';

  const indicator = ref([{ name: '国际', max: 6500 }]);
  const radarData = ref([{
    value: [4850],
    name: '装备租赁',
  }]);

  const fetchData = async () => {
    try {
      const response = await queryMultiDimensionAnalysis();
      const data = (response && typeof response === 'object' && 'content_type_distribution' in response) ? response : (response?.data || null);
      
      if (data && data.content_type_distribution) {
        const distData = data.content_type_distribution;
        if (distData.indicator && distData.indicator.length > 0) {
          indicator.value = distData.indicator;
        }
        if (distData.data && distData.data.length > 0) {
          radarData.value = distData.data;
        }
      }
    } catch (err) {
      console.error('获取内容类型分布数据失败:', err);
    }
  };

  onMounted(() => {
    fetchData();
  });

  const { chartOption } = useChartOption((isDark) => {
    return {
      grid: {
        left: 0,
        right: 0,
        top: 0,
        bottom: 20,
      },
      legend: {
        show: true,
        top: 'center',
        right: '0',
        orient: 'vertical',
        icon: 'circle',
        itemWidth: 10,
        itemHeight: 10,
        itemGap: 20,
        textStyle: {
          color: isDark ? '#ffffff' : '#4E5969',
        },
      },
      radar: {
        center: ['40%', '50%'],
        radius: 80,
        indicator: indicator.value.length > 0 ? indicator.value : [
          { name: '国际', max: 100 },
        ],
        // 禁用alignTicks以避免警告
        axisNameGap: 10,
        axisName: {
          color: isDark ? '#ffffff' : '#1D2129',
        },
        axisLine: {
          lineStyle: {
            color: isDark ? '#484849' : '#E5E6EB',
          },
        },
        splitLine: {
          lineStyle: {
            color: isDark ? '#484849' : '#E5E6EB',
          },
        },
        splitArea: {
          areaStyle: {
            color: [],
          },
        },
      },
      series: [
        {
          type: 'radar',
          areaStyle: {
            opacity: 0.2,
          },
          data: radarData.value.length > 0 ? radarData.value.map((item: any, idx: number) => ({
            value: item.value,
            name: item.name,
            symbol: 'none',
            itemStyle: {
              color: idx === 0 ? (isDark ? '#6CAAF5' : '#249EFF') : 
                     idx === 1 ? (isDark ? '#A079DC' : '#313CA9') : 
                     (isDark ? '#3D72F6' : '#21CCFF'),
            },
          })) : [
            {
              value: [4850, 19000, 19000, 29500, 35200, 20000],
              name: '装备租赁',
              symbol: 'none',
              itemStyle: {
                color: isDark ? '#6CAAF5' : '#249EFF',
              },
            },
          ],
        },
      ],
    };
  });
</script>

<style scoped lang="less"></style>
