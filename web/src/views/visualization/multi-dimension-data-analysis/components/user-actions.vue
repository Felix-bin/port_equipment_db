<template>
  <a-card
    class="general-card"
    :title="$t('multiDAnalysis.card.title.userActions')"
  >
    <Chart height="122px" :option="chartOption" />
  </a-card>
</template>

<script lang="ts" setup>
  import { ref, onMounted } from 'vue';
  import useChartOption from '@/hooks/chart-option';
  import { queryMultiDimensionAnalysis } from '@/api/visualization';

  const userActionsData = ref([0, 0, 0]);

  const fetchData = async () => {
    try {
      const response = await queryMultiDimensionAnalysis();
      const data = (response && typeof response === 'object' && 'user_actions' in response) ? response : (response?.data || null);
      
      if (data && data.user_actions && data.user_actions.data) {
        userActionsData.value = data.user_actions.data;
      }
    } catch (err) {
      console.error('获取用户行为数据失败:', err);
    }
  };

  onMounted(() => {
    fetchData();
  });

  const { chartOption } = useChartOption((isDark) => {
    return {
      grid: {
        left: 44,
        right: 20,
        top: 0,
        bottom: 20,
      },
      xAxis: {
        type: 'value',
        axisLabel: {
          show: true,
          formatter(value: number, idx: number) {
            if (idx === 0) return String(value);
            return `${Number(value) / 1000}k`;
          },
        },
        splitLine: {
          lineStyle: {
            color: isDark ? '#484849' : '#E5E8EF',
          },
        },
      },
      yAxis: {
        type: 'category',
        data: ['点赞量', '评论量', '分享量'],
        axisLabel: {
          show: true,
          color: '#4E5969',
        },
        axisTick: {
          show: true,
          length: 2,
          lineStyle: {
            color: '#A9AEB8',
          },
          alignWithLabel: true,
        },
        axisLine: {
          lineStyle: {
            color: isDark ? '#484849' : '#A9AEB8',
          },
        },
      },
      tooltip: {
        show: true,
        trigger: 'axis',
      },
      series: [
        {
          data: userActionsData.value,
          type: 'bar',
          barWidth: 7,
          itemStyle: {
            color: '#4086FF',
            borderRadius: 4,
          },
        },
      ],
    };
  });
</script>

<style scoped lang="less"></style>
