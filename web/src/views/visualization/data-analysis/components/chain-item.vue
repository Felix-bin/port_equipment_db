<template>
  <a-spin :loading="loading" style="width: 100%">
    <a-card :bordered="false" :style="cardStyle">
      <div class="content-wrap">
        <div class="content">
          <a-statistic
            :title="title"
            :value="renderData.count"
            :value-from="0"
            animation
            show-group-separator
          />
          <div class="desc">
            <a-typography-text type="secondary" class="label">
              {{ $t('dataAnalysis.card.yesterday') }}
            </a-typography-text>
            <a-typography-text type="danger">
              {{ renderData.growth }}
              <icon-arrow-rise />
            </a-typography-text>
          </div>
        </div>
        <div class="chart">
          <Chart v-if="!loading" :option="chartOption" />
        </div>
      </div>
    </a-card>
  </a-spin>
</template>

<script lang="ts" setup>
  import { ref, PropType, CSSProperties } from 'vue';
  import useLoading from '@/hooks/loading';
  import {
    queryPublicOpinionAnalysis,
    PublicOpinionAnalysis,
    PublicOpinionAnalysisRes,
  } from '@/api/visualization';
  import { queryRentalAnalysis, RentalAnalysisStats } from '@/api/rental';
  import useChartOption from '@/hooks/chart-option';

  const barChartOptionsFactory = () => {
    const data = ref<any>([]);
    const { chartOption } = useChartOption(() => {
      return {
        grid: {
          left: 0,
          right: 0,
          top: 10,
          bottom: 0,
        },
        xAxis: {
          type: 'category',
          show: false,
        },
        yAxis: {
          show: false,
        },
        tooltip: {
          show: true,
          trigger: 'axis',
        },
        series: {
          name: 'total',
          data,
          type: 'bar',
          barWidth: 7,
          itemStyle: {
            borderRadius: 2,
          },
        },
      };
    });
    return {
      data,
      chartOption,
    };
  };

  const lineChartOptionsFactory = () => {
    const data = ref<number[][]>([[], []]);
    const { chartOption } = useChartOption(() => {
      return {
        grid: {
          left: 0,
          right: 0,
          top: 10,
          bottom: 0,
        },
        xAxis: {
          type: 'category',
          show: false,
        },
        yAxis: {
          show: false,
        },
        tooltip: {
          show: true,
          trigger: 'axis',
        },
        series: [
          {
            name: '2001',
            data: data.value[0],
            type: 'line',
            showSymbol: false,
            smooth: true,
            lineStyle: {
              color: '#165DFF',
              width: 3,
            },
          },
          {
            name: '2002',
            data: data.value[1],
            type: 'line',
            showSymbol: false,
            smooth: true,
            lineStyle: {
              color: '#6AA1FF',
              width: 3,
              type: 'dashed',
            },
          },
        ],
      };
    });
    return {
      data,
      chartOption,
    };
  };

  const pieChartOptionsFactory = () => {
    const data = ref<any>([]);
    const { chartOption } = useChartOption(() => {
      return {
        grid: {
          left: 0,
          right: '35%', // 为图例留出空间
          top: 0,
          bottom: 0,
        },
        legend: {
          show: true,
          top: 'center',
          right: '5%', // 距离右边缘5%
          orient: 'vertical',
          icon: 'circle',
          itemWidth: 6,
          itemHeight: 6,
          itemGap: 4, // 图例项之间的间距
          textStyle: {
            color: '#4E5969',
            fontSize: 11, // 稍微减小字体大小
          },
          formatter: function(name: string) {
            // 限制图例文字长度，避免过长
            return name.length > 6 ? name.substring(0, 6) + '...' : name;
          },
        },
        tooltip: {
          show: true,
          formatter: '{b}: {c} ({d}%)',
        },
        series: [
          {
            name: '总计',
            type: 'pie',
            radius: ['45%', '65%'], // 稍微缩小饼图，为图例留出更多空间
            center: ['35%', '50%'], // 将饼图向左移动
            label: {
              show: false,
            },
            data,
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)',
              },
            },
          },
        ],
      };
    });
    return {
      data,
      chartOption,
    };
  };

  const props = defineProps({
    title: {
      type: String,
      default: '',
    },
    quota: {
      type: String,
      default: '',
    },
    chartType: {
      type: String,
      default: '',
    },
    cardStyle: {
      type: Object as PropType<CSSProperties>,
      default: () => {
        return {};
      },
    },
  });

  const { loading, setLoading } = useLoading(true);
  const { chartOption: lineChartOption, data: lineData } =
    lineChartOptionsFactory();
  const { chartOption: barChartOption, data: barData } =
    barChartOptionsFactory();
  const { chartOption: pieChartOption, data: pieData } =
    pieChartOptionsFactory();
  const renderData = ref<PublicOpinionAnalysisRes>({
    count: 0,
    growth: 0,
    chartData: [],
  });
  const chartOption = ref({});
  const fetchData = async (params: PublicOpinionAnalysis) => {
    try {
      // 如果是租赁相关的 quota，使用租赁分析 API
      const rentalQuotas = ['orders', 'outbound', 'renting', 'returned'];
      if (rentalQuotas.includes(props.quota)) {
        const response = await queryRentalAnalysis();
        // 响应拦截器可能已经解构了，但为了安全，检查两种情况
        // 如果 response 有 data 属性且 data 有 total_orders，说明是包装格式
        // 否则 response 本身就是数据
        let data: any;
        if (response && typeof response === 'object' && 'data' in response && response.data && typeof response.data === 'object' && 'total_orders' in response.data) {
          data = response.data;
        } else if (response && typeof response === 'object' && 'total_orders' in response) {
          data = response;
        } else {
          console.error('API 返回数据格式不正确:', response);
          throw new Error('API 返回数据格式不正确');
        }
        
        let count = 0;
        let growth = 0;
        let chartData: any[] = [];
        
        // 根据 quota 获取对应的数据
        switch (props.quota) {
          case 'orders':
            count = data.total_orders || 0;
            growth = data.orders_growth || 0;
            // 生成模拟图表数据（基于订单总数）
            chartData = Array.from({ length: 7 }, (_, i) => ({
              x: `Day${i + 1}`,
              y: Math.floor(count / 7) + Math.floor(Math.random() * 10),
              name: '订单数',
            }));
            break;
          case 'outbound':
            count = data.total_outbound || 0;
            growth = data.outbound_growth || 0;
            chartData = Array.from({ length: 7 }, (_, i) => ({
              x: `Day${i + 1}`,
              y: Math.floor(count / 7) + Math.floor(Math.random() * 5),
              name: '出库量',
            }));
            break;
          case 'renting':
            count = data.total_renting || 0;
            growth = data.renting_growth || 0;
            chartData = Array.from({ length: 7 }, (_, i) => ({
              x: `Day${i + 1}`,
              y: Math.floor(count / 7) + Math.floor(Math.random() * 5),
              name: '在租数',
            }));
            break;
          case 'returned':
            count = data.total_returned || 0;
            growth = data.returned_growth || 0;
            // 饼图数据
            chartData = (data.category_ratio || []).map((item: any) => ({
              name: item.name,
              value: item.value || 0,
            }));
            break;
        }
        
        renderData.value = {
          count,
          growth,
          chartData,
        };
      } else {
        // 使用原来的 API
        const { data } = await queryPublicOpinionAnalysis(params);
        renderData.value = data;
      }
      
      const { chartData } = renderData.value;
      if (props.chartType === 'bar') {
        chartData.forEach((el: any, idx: number) => {
          barData.value.push({
            value: el.y || el.value,
            itemStyle: {
              color: idx % 2 ? '#2CAB40' : '#86DF6C',
            },
          });
        });
        chartOption.value = barChartOption.value;
      } else if (props.chartType === 'line') {
        // 为折线图生成两条线
        const half = Math.ceil(chartData.length / 2);
        chartData.forEach((el: any, idx: number) => {
          if (idx < half) {
            lineData.value[0].push(el.y || el.value || 0);
          } else {
            lineData.value[1].push(el.y || el.value || 0);
          }
        });
        chartOption.value = lineChartOption.value;
      } else {
        chartData.forEach((el: any) => {
          pieData.value.push({
            name: el.name,
            value: el.value || el.y || 0,
          });
        });
        chartOption.value = pieChartOption.value;
      }
    } catch (err) {
      console.error('获取数据失败:', err);
    } finally {
      setLoading(false);
    }
  };
  fetchData({ quota: props.quota });
</script>

<style scoped lang="less">
  :deep(.arco-card) {
    border-radius: 4px;
  }
  :deep(.arco-card-body) {
    width: 100%;
    height: 134px;
    padding: 0;
  }
  .content-wrap {
    width: 100%;
    padding: 16px;
    white-space: nowrap;
  }
  :deep(.content) {
    float: left;
    width: 108px;
    height: 102px;
  }
  :deep(.arco-statistic) {
    .arco-statistic-title {
      font-size: 16px;
      font-weight: bold;
      white-space: nowrap;
    }
    .arco-statistic-content {
      margin-top: 10px;
    }
  }

  .chart {
    float: right;
    width: calc(100% - 108px);
    height: 90px;
    vertical-align: bottom;
  }

  .label {
    padding-right: 8px;
    font-size: 12px;
  }
</style>
