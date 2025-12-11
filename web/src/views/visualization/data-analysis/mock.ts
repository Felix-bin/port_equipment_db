import Mock from 'mockjs';
import setupMock, { successResponseWrap } from '@/utils/setup-mock';
import { PostData } from '@/types/global';

setupMock({
  setup() {
    Mock.mock(
      new RegExp('/api/public-opinion-analysis'),
      (params: PostData) => {
        const { quota = 'visitors' } = JSON.parse(params.body);
        if (['visitors', 'comment'].includes(quota)) {
          const year = new Date().getFullYear();
          const getLineData = (name: number) => {
            return new Array(12).fill(0).map((_item, index) => ({
              x: `${index + 1}月`,
              y: Mock.Random.natural(0, 100),
              name: String(name),
            }));
          };
          return successResponseWrap({
            count: 5670,
            growth: 206.32,
            chartData: [...getLineData(year), ...getLineData(year - 1)],
          });
        }
        if (['published'].includes(quota)) {
          const year = new Date().getFullYear();
          const getLineData = (name: number) => {
            return new Array(12).fill(0).map((_item, index) => ({
              x: `${index + 1}日`,
              y: Mock.Random.natural(20, 100),
              name: String(name),
            }));
          };
          return successResponseWrap({
            count: 5670,
            growth: 206.32,
            chartData: [...getLineData(year)],
          });
        }
        return successResponseWrap({
          count: 1250,
          growth: 18.5,
          chartData: [
            // itemStyle for demo
            { name: '起重机', value: 36, itemStyle: { color: '#8D4EDA' } },
            { name: '叉车', value: 42, itemStyle: { color: '#165DFF' } },
            { name: '集装箱', value: 22, itemStyle: { color: '#00B2FF' } },
          ],
        });
      }
    );

    Mock.mock(new RegExp('/api/content-period-analysis'), () => {
      const getLineData = (name: string) => {
        return {
          name,
          value: new Array(12).fill(0).map(() => Mock.Random.natural(30, 90)),
        };
      };
      return successResponseWrap({
        xAxis: new Array(12).fill(0).map((_item, index) => `${index * 2}:00`),
        data: [
          getLineData('起重机'),
          getLineData('叉车'),
          getLineData('集装箱'),
        ],
      });
    });

    Mock.mock(new RegExp('/api/content-publish'), () => {
      const generateLineData = (name: string) => {
        const result = {
          name,
          x: [] as string[],
          y: [] as number[],
        };
        new Array(12).fill(0).forEach((_item, index) => {
          result.x.push(`${index * 2}:00`);
          result.y.push(Mock.Random.natural(1000, 3000));
        });
        return result;
      };
      return successResponseWrap([
        generateLineData('起重机'),
        generateLineData('叉车'),
        generateLineData('集装箱'),
      ]);
    });

    Mock.mock(new RegExp('/api/popular-author/list'), () => {
      const equipmentNames = [
        '门式起重机 QZ-50T',
        '电动叉车 CPCD-3T',
        '桥式起重机 QD-32T',
        '集装箱 40英尺',
        '塔式起重机 QTZ-80',
        '仓储叉车 CPD-2T',
        '汽车起重机 QY-25T',
      ];
      const generateData = () => {
        const list = new Array(7).fill(0).map((_item, index) => ({
          ranking: index + 1,
          author: equipmentNames[index],
          contentCount: Mock.Random.natural(50, 300),
          clickCount: Mock.Random.natural(500, 5000),
        }));
        return {
          list,
        };
      };
      return successResponseWrap({
        ...generateData(),
      });
    });
  },
});
