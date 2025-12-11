import Mock from 'mockjs';
import qs from 'query-string';
import setupMock, { successResponseWrap } from '@/utils/setup-mock';
import { GetParams } from '@/types/global';

const { Random } = Mock;

const data = Mock.mock({
  'list|35': [
    {
      'id|8': /[A-Z][0-9]/,
      'voyageNumber|8': /VY[0-9]{6}/,
      'rentalOrder|8': /RO[0-9]{6}/,
      'vesselName|1': ['远洋号', '海航号', '顺风号', '乘风号'],
      'equipmentList': '@word(5,10)',
      'usageHours|8-72': 1,
      'voyageDate': Random.date('yyyy-MM-dd'),
      'status|1': ['in-progress', 'completed', 'cancelled'],
      'remark': '@cparagraph(1)',
    },
  ],
});

setupMock({
  mock: false, // 禁用 mock，使用真实 API
  setup() {
    Mock.mock(new RegExp('/api/rental/voyage'), (params: GetParams) => {
      const { current = 1, pageSize = 10 } = qs.parseUrl(params.url).query;
      const p = current as number;
      const ps = pageSize as number;
      return successResponseWrap({
        list: data.list.slice((p - 1) * ps, p * ps),
        total: 35,
      });
    });

    Mock.mock(new RegExp('/api/rental/voyage'), 'post', () => {
      return successResponseWrap({});
    });

    Mock.mock(new RegExp('/api/rental/voyage/.*/complete'), 'post', () => {
      return successResponseWrap({});
    });
  },
});
