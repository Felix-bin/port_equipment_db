import Mock from 'mockjs';
import qs from 'query-string';
import setupMock, { successResponseWrap } from '@/utils/setup-mock';
import { GetParams } from '@/types/global';

const { Random } = Mock;

const data = Mock.mock({
  'list|30': [
    {
      'id|8': /[A-Z][0-9]/,
      'returnCode|8': /RT[0-9]{6}/,
      'rentalOrder|8': /RO[0-9]{6}/,
      'equipmentCode|8': /EQ[0-9]{6}/,
      'equipmentName|1': ['门式起重机', '桥式起重机', '叉车', '集装箱', '吊具'],
      'quantity|1-5': 1,
      'returnTime': Random.datetime(),
      'equipmentCondition|1': ['good', 'normal', 'damaged'],
      'damageDescription': '@cparagraph(1)',
      'inspectionResult': '@cparagraph(1)',
      'inspector': '@cname',
      'inspectionStatus|1': ['pending', 'passed', 'failed'],
      'remark': '@cparagraph(1)',
    },
  ],
});

setupMock({
  mock: false, // 禁用 mock，使用真实 API
  setup() {
    Mock.mock(new RegExp('/api/rental/return'), (params: GetParams) => {
      const { current = 1, pageSize = 10 } = qs.parseUrl(params.url).query;
      const p = current as number;
      const ps = pageSize as number;
      return successResponseWrap({
        list: data.list.slice((p - 1) * ps, p * ps),
        total: 30,
      });
    });

    Mock.mock(new RegExp('/api/rental/return'), 'post', () => {
      return successResponseWrap({});
    });

    Mock.mock(new RegExp('/api/rental/return/.*/inspect'), 'post', () => {
      return successResponseWrap({});
    });
  },
});
