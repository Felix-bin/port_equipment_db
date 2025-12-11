import Mock from 'mockjs';
import qs from 'query-string';
import dayjs from 'dayjs';
import { GetParams } from '@/types/global';
import setupMock, { successResponseWrap } from '@/utils/setup-mock';

const craneList = [
  {
    key: 1,
    clickNumber: '156',
    title: '门式起重机 QZ-50T',
    increases: 35,
  },
  {
    key: 2,
    clickNumber: '142',
    title: '桥式起重机 QD-32T',
    increases: 22,
  },
  {
    key: 3,
    clickNumber: '128',
    title: '塔式起重机 QTZ-80',
    increases: 9,
  },
  {
    key: 4,
    clickNumber: '98',
    title: '门座式起重机 MQ-25T',
    increases: 17,
  },
  {
    key: 5,
    clickNumber: '76',
    title: '汽车起重机 QY-25T',
    increases: 37,
  },
];
const forkliftList = [
  {
    key: 1,
    clickNumber: '203',
    title: '电动叉车 CPCD-3T',
    increases: 15,
  },
  {
    key: 2,
    clickNumber: '187',
    title: '内燃叉车 CPC-5T',
    increases: 26,
  },
  {
    key: 3,
    clickNumber: '165',
    title: '仓储叉车 CPD-2T',
    increases: 9,
  },
  {
    key: 4,
    clickNumber: '134',
    title: '前移式叉车 CQD-3T',
    increases: 0,
  },
  {
    key: 5,
    clickNumber: '98',
    title: '堆高车 CTY-2T',
    increases: 4,
  },
];
const containerList = [
  {
    key: 1,
    clickNumber: '89',
    title: '20英尺标准集装箱',
    increases: 5,
  },
  {
    key: 2,
    clickNumber: '76',
    title: '40英尺标准集装箱',
    increases: 17,
  },
  {
    key: 3,
    clickNumber: '65',
    title: '40英尺高柜集装箱',
    increases: 30,
  },
  {
    key: 4,
    clickNumber: '54',
    title: '45英尺超长集装箱',
    increases: 12,
  },
  {
    key: 5,
    clickNumber: '42',
    title: '冷藏集装箱',
    increases: 2,
  },
];
setupMock({
  setup() {
    Mock.mock(new RegExp('/api/content-data'), () => {
      const presetData = [58, 81, 53, 90, 64, 88, 49, 79];
      const getLineData = () => {
        const count = 8;
        return new Array(count).fill(0).map((el, idx) => ({
          x: dayjs()
            .day(idx - 2)
            .format('YYYY-MM-DD'),
          y: presetData[idx],
        }));
      };
      return successResponseWrap([...getLineData()]);
    });
    Mock.mock(new RegExp('/api/popular/list'), (params: GetParams) => {
      const { type = 'crane' } = qs.parseUrl(params.url).query;
      if (type === 'forklift') {
        return successResponseWrap([...forkliftList]);
      }
      if (type === 'container') {
        return successResponseWrap([...containerList]);
      }
      return successResponseWrap([...craneList]);
    });
  },
});
