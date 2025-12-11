import Mock from 'mockjs';
import qs from 'query-string';
import setupMock, { successResponseWrap } from '@/utils/setup-mock';
import { GetParams } from '@/types/global';

const { Random } = Mock;

const data = Mock.mock({
  'list|25': [
    {
      'id|8': /[A-Z][0-9]/,
      'settlementCode|8': /ST[0-9]{6}/,
      'rentalOrder|8': /RO[0-9]{6}/,
      'applicant': '@cname',
      'rentalDays|1-30': 1,
      'dailyRate|500-5000': 1,
      'equipmentFee|1000-10000': 1,
      'usageFee|500-5000': 1,
      'damageFee|0-5000': 1,
      'discount|0-20': 1,
      'totalAmount|5000-50000': 1,
      'paymentMethod|1': ['cash', 'transfer', 'check', 'other'],
      'settlementTime': Random.datetime(),
      'status|1': ['pending', 'paid', 'overdue'],
      'remark': '@cparagraph(1)',
    },
  ],
});

setupMock({
  mock: false, // 禁用 mock，使用真实 API
  setup() {
    Mock.mock(new RegExp('/api/settlement/fee'), (params: GetParams) => {
      const { current = 1, pageSize = 10 } = qs.parseUrl(params.url).query;
      const p = current as number;
      const ps = pageSize as number;
      return successResponseWrap({
        list: data.list.slice((p - 1) * ps, p * ps),
        total: 25,
      });
    });

    Mock.mock(new RegExp('/api/settlement/fee'), 'post', () => {
      return successResponseWrap({});
    });

    Mock.mock(new RegExp('/api/settlement/fee/.*/pay'), 'post', () => {
      return successResponseWrap({});
    });
  },
});
