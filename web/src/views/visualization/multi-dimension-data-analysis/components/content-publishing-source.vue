<template>
  <a-spin :loading="loading" style="width: 100%">
    <a-card
      class="general-card"
      :title="$t('multiDAnalysis.card.title.contentPublishingSource')"
    >
      <Chart style="width: 100%; height: 300px" :option="chartOption" />
    </a-card>
  </a-spin>
</template>

<script lang="ts" setup>
  import { ref, onMounted } from 'vue';
  import useLoading from '@/hooks/loading';
  import useChartOption from '@/hooks/chart-option';
  import { queryMultiDimensionAnalysis } from '@/api/visualization';

  const { loading, setLoading } = useLoading(true);
  const pieData1 = ref<Array<{name: string, value: number}>>([]);
  const pieData2 = ref<Array<{name: string, value: number}>>([]);
  const pieData3 = ref<Array<{name: string, value: number}>>([]);
  const legendData = ref<string[]>([]);

  const { chartOption } = useChartOption((isDark) => {
    const graphicElementStyle = {
      textAlign: 'center',
      fill: isDark ? 'rgba(255,255,255,0.7)' : '#4E5969',
      fontSize: 14,
      lineWidth: 10,
      fontWeight: 'bold',
    };
    
    // 动态生成图例数据（合并三个饼图的所有名称）
    const allNames = new Set<string>();
    pieData1.value.forEach(item => allNames.add(item.name));
    pieData2.value.forEach(item => allNames.add(item.name));
    pieData3.value.forEach(item => allNames.add(item.name));
    
    return {
      legend: {
        left: 'center',
        data: Array.from(allNames).length > 0 ? Array.from(allNames) : [],
        bottom: 0,
        icon: 'circle',
        itemWidth: 8,
        textStyle: {
          color: isDark ? 'rgba(255,255,255,0.7)' : '#4E5969',
        },
        itemStyle: {
          borderWidth: 0,
        },
      },
      tooltip: {
        show: true,
        trigger: 'item',
      },
      graphic: {
        elements: [
          {
            type: 'text',
            left: '9.6%',
            top: 'center',
            style: {
              text: '装备来源',
              ...graphicElementStyle,
            },
          },
          {
            type: 'text',
            left: 'center',
            top: 'center',
            style: {
              text: '租赁状态',
              ...graphicElementStyle,
            },
          },
          {
            type: 'text',
            left: '86.6%',
            top: 'center',
            style: {
              text: '归还状态',
              ...graphicElementStyle,
            },
          },
        ],
      },
      series: [
        {
          type: 'pie',
          radius: ['50%', '70%'],
          center: ['11%', '50%'],
          label: {
            formatter: '{d}% ',
            color: isDark ? 'rgba(255, 255, 255, 0.7)' : '#4E5969',
          },
          itemStyle: {
            borderColor: isDark ? '#000' : '#fff',
            borderWidth: 1,
          },
          data: pieData1.value,
        },
        {
          type: 'pie',
          radius: ['50%', '70%'],
          center: ['50%', '50%'],
          label: {
            formatter: '{d}% ',
            color: isDark ? 'rgba(255, 255, 255, 0.7)' : '#4E5969',
          },
          itemStyle: {
            borderColor: isDark ? '#000' : '#fff',
            borderWidth: 1,
          },
          data: pieData2.value,
        },
        {
          type: 'pie',
          radius: ['50%', '70%'],
          center: ['88%', '50%'],
          label: {
            formatter: '{d}% ',
            color: isDark ? 'rgba(255, 255, 255, 0.7)' : '#4E5969',
          },
          itemStyle: {
            borderColor: isDark ? '#000' : '#fff',
            borderWidth: 1,
          },
          data: pieData3.value,
        },
      ],
    };
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await queryMultiDimensionAnalysis();
      const data = (response && typeof response === 'object' && 'content_publishing_source' in response) ? response : (response?.data || null);
      
      if (data && data.content_publishing_source && data.content_publishing_source.data) {
        const sourceData = data.content_publishing_source.data;
        if (sourceData.length >= 1 && Array.isArray(sourceData[0])) {
          pieData1.value = sourceData[0];
        }
        if (sourceData.length >= 2 && Array.isArray(sourceData[1])) {
          pieData2.value = sourceData[1];
        }
        if (sourceData.length >= 3 && Array.isArray(sourceData[2])) {
          pieData3.value = sourceData[2];
        }
        
        // 更新图例数据
        const allNames = new Set<string>();
        pieData1.value.forEach(item => allNames.add(item.name));
        pieData2.value.forEach(item => allNames.add(item.name));
        pieData3.value.forEach(item => allNames.add(item.name));
        legendData.value = Array.from(allNames);
      }
    } catch (err) {
      console.error('获取内容发布来源数据失败:', err);
    } finally {
      setLoading(false);
    }
  };

  onMounted(() => {
    fetchData();
  });
</script>

<style scoped lang="less"></style>
