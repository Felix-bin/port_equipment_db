<template>
  <a-spin :loading="loading" style="width: 100%">
    <a-card class="general-card" :header-style="{ paddingBottom: '16px' }">
      <template #title>
        {{ $t('dataAnalysis.contentPeriodAnalysis') }}
      </template>
      <Chart style="width: 100%; height: 370px" :option="chartOption" />
    </a-card>
  </a-spin>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import useLoading from '@/hooks/loading';
  import { queryContentPeriodAnalysis } from '@/api/visualization';
  import { queryRentalAnalysis } from '@/api/rental';
  import { ToolTipFormatterParams } from '@/types/echarts';
  import useChartOption from '@/hooks/chart-option';

  const tooltipItemsHtmlString = (items: ToolTipFormatterParams[]) => {
    return items
      .map(
        (el) => `<div class="content-panel">
        <p>
          <span style="background-color: ${el.color}" class="tooltip-item-icon"></span>
          <span>${el.seriesName}</span>
        </p>
        <span class="tooltip-value">
        ${el.value}%
        </span>
      </div>`
      )
      .join('');
  };

  const { loading, setLoading } = useLoading(true);
  const xAxis = ref<string[]>([]);
  const textChartsData = ref<number[]>([]);
  const imgChartsData = ref<number[]>([]);
  const videoChartsData = ref<number[]>([]);
  const { chartOption } = useChartOption((isDark) => {
    return {
      grid: {
        left: '40',
        right: 0,
        top: '20',
        bottom: '100',
      },
      legend: {
        bottom: 0,
        icon: 'circle',
        textStyle: {
          color: '#4E5969',
        },
      },
      xAxis: {
        type: 'category',
        data: xAxis.value,
        boundaryGap: false,
        axisLine: {
          lineStyle: {
            color: isDark ? '#3f3f3f' : '#A9AEB8',
          },
        },
        axisTick: {
          show: true,
          alignWithLabel: true,
          lineStyle: {
            color: '#86909C',
          },
          interval(idx: number) {
            if (idx === 0) return false;
            if (idx === xAxis.value.length - 1) return false;
            return true;
          },
        },
        axisLabel: {
          color: '#86909C',
          formatter(value: number, idx: number) {
            if (idx === 0) return '';
            if (idx === xAxis.value.length - 1) return '';
            return `${value}`;
          },
        },
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          color: '#86909C',
          formatter: '{value}',
        },
        splitLine: {
          lineStyle: {
            color: isDark ? '#3F3F3F' : '#E5E6EB',
          },
        },
      },
      tooltip: {
        show: true,
        trigger: 'axis',
        formatter(params) {
          const [firstElement] = params as ToolTipFormatterParams[];
          return `<div>
            <p class="tooltip-title">${firstElement.axisValueLabel}</p>
            ${tooltipItemsHtmlString(params as ToolTipFormatterParams[])}
          </div>`;
        },
        className: 'echarts-tooltip-diy',
      },
      series: [
        {
          name: '租赁订单',
          data: textChartsData.value,
          type: 'line',
          smooth: true,
          showSymbol: false,
          color: isDark ? '#3D72F6' : '#246EFF',
          symbol: 'circle',
          symbolSize: 10,
          emphasis: {
            focus: 'series',
            itemStyle: {
              borderWidth: 2,
              borderColor: '#E0E3FF',
            },
          },
        },
        {
          name: '图文类',
          data: imgChartsData.value,
          type: 'line',
          smooth: true,
          showSymbol: false,
          color: isDark ? '#A079DC' : '#00B2FF',
          symbol: 'circle',
          symbolSize: 10,
          emphasis: {
            focus: 'series',
            itemStyle: {
              borderWidth: 2,
              borderColor: '#E2F2FF',
            },
          },
        },
        {
          name: '视频类',
          data: videoChartsData.value,
          type: 'line',
          smooth: true,
          showSymbol: false,
          color: isDark ? '#6CAAF5' : '#81E2FF',
          symbol: 'circle',
          symbolSize: 10,
          emphasis: {
            focus: 'series',
            itemStyle: {
              borderWidth: 2,
              borderColor: '#D9F6FF',
            },
          },
        },
      ],
      dataZoom: [
        {
          bottom: 40,
          type: 'slider',
          left: 40,
          right: 14,
          height: 14,
          borderColor: 'transparent',
          handleIcon:
            'image://http://p3-armor.byteimg.com/tos-cn-i-49unhts6dw/1ee5a8c6142b2bcf47d2a9f084096447.svg~tplv-49unhts6dw-image.image',
          handleSize: '20',
          handleStyle: {
            shadowColor: 'rgba(0, 0, 0, 0.2)',
            shadowBlur: 4,
          },
          brushSelect: false,
          backgroundColor: isDark ? '#313132' : '#F2F3F5',
        },
        {
          type: 'inside',
          start: 0,
          end: 100,
          zoomOnMouseWheel: false,
        },
      ],
    };
  });
  const fetchData = async () => {
    setLoading(true);
    try {
      // 使用租赁分析 API
      const response = await queryRentalAnalysis();
      
      // 响应拦截器可能已经解构了数据
      const data = (response && typeof response === 'object' && 'period_analysis' in response) ? response : (response?.data || null);
      
      if (data && data.period_analysis) {
        const periodAnalysis = data.period_analysis;
        
        // 设置 xAxis
        if (periodAnalysis.xAxis && Array.isArray(periodAnalysis.xAxis) && periodAnalysis.xAxis.length > 0) {
          xAxis.value = periodAnalysis.xAxis;
        } else {
          // 如果没有 xAxis，生成默认的月份列表（最近12个月）
          const months = [];
          const now = new Date();
          for (let i = 11; i >= 0; i--) {
            const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
            months.push(`${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`);
          }
          xAxis.value = months;
        }
        
        // 处理数据
        if (periodAnalysis.data && Array.isArray(periodAnalysis.data) && periodAnalysis.data.length > 0) {
          // 查找"租赁订单"数据
          const rentalOrderData = periodAnalysis.data.find((el: any) => el.name === '租赁订单');
          if (rentalOrderData && Array.isArray(rentalOrderData.value)) {
            textChartsData.value = rentalOrderData.value;
          } else {
            // 如果没有数据，填充零值
            textChartsData.value = new Array(xAxis.value.length).fill(0);
          }
          
          // 处理其他数据系列（如果有）
          periodAnalysis.data.forEach((el: any) => {
            if (el.name === '图文类' && Array.isArray(el.value)) {
              imgChartsData.value = el.value;
            } else if (el.name !== '租赁订单' && Array.isArray(el.value)) {
              videoChartsData.value = el.value;
            }
          });
          
          // 确保数据长度与 xAxis 一致
          if (textChartsData.value.length !== xAxis.value.length) {
            const newData = new Array(xAxis.value.length).fill(0);
            textChartsData.value.forEach((val: number, idx: number) => {
              if (idx < newData.length) {
                newData[idx] = val;
              }
            });
            textChartsData.value = newData;
          }
        } else {
          // 如果没有数据，填充零值
          textChartsData.value = new Array(xAxis.value.length).fill(0);
          imgChartsData.value = [];
          videoChartsData.value = [];
        }
      } else {
        // 如果没有数据，使用原来的 API
        const { data: chartData } = await queryContentPeriodAnalysis();
        xAxis.value = chartData.xAxis;
        chartData.data.forEach((el) => {
          if (el.name === '纯文本') {
            textChartsData.value = el.value;
          } else if (el.name === '图文类') {
            imgChartsData.value = el.value;
          }
          videoChartsData.value = el.value;
        });
      }
    } catch (err) {
      console.error('获取数据失败:', err);
      // 出错时使用原来的 API
      try {
        const { data: chartData } = await queryContentPeriodAnalysis();
        xAxis.value = chartData.xAxis;
        chartData.data.forEach((el) => {
          if (el.name === '纯文本') {
            textChartsData.value = el.value;
          } else if (el.name === '图文类') {
            imgChartsData.value = el.value;
          }
          videoChartsData.value = el.value;
        });
      } catch (fallbackErr) {
        console.error('备用 API 也失败:', fallbackErr);
        // 即使备用 API 也失败，也要显示一些默认数据
        const months = [];
        const now = new Date();
        for (let i = 11; i >= 0; i--) {
          const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
          months.push(`${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`);
        }
        xAxis.value = months;
        textChartsData.value = new Array(12).fill(0);
        imgChartsData.value = [];
        videoChartsData.value = [];
      }
    } finally {
      setLoading(false);
    }
  };
  fetchData();
</script>

<style scoped lang="less">
  .chart-box {
    width: 100%;
    height: 230px;
  }
</style>
