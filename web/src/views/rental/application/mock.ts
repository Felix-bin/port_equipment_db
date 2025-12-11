import Mock from 'mockjs';
import qs from 'query-string';
import setupMock, { successResponseWrap } from '@/utils/setup-mock';
import { GetParams } from '@/types/global';

const { Random } = Mock;

const data = Mock.mock({
  'list|60': [
    {
      'id|8': /[A-Z][0-9]/,
      'applicationCode|8': /AP[0-9]{6}/,
      'applicant': '@cname',
      'equipmentType|1': ['crane', 'forklift', 'container', 'other'],
      'equipmentCode|8': /EQ[0-9]{6}/,
      'quantity|1-5': 1,
      'startDate': Random.date('yyyy-MM-dd'),
      'endDate': Random.date('yyyy-MM-dd'),
      'purpose': '@cparagraph(1,2)',
      'applicationTime': Random.datetime(),
      'status|1': ['pending', 'approved', 'rejected', 'completed'],
      'remark': '@cparagraph(1)',
    },
  ],
});

setupMock({
  mock: false, // 禁用 mock，使用真实 API
  setup() {
    Mock.mock(new RegExp('/api/rental/application'), (params: GetParams) => {
      const { current = 1, pageSize = 10 } = qs.parseUrl(params.url).query;
      const p = current as number;
      const ps = pageSize as number;
      return successResponseWrap({
        list: data.list.slice((p - 1) * ps, p * ps),
        total: 60,
      });
    });

    Mock.mock(new RegExp('/api/rental/application'), 'post', () => {
      return successResponseWrap({});
    });

    Mock.mock(new RegExp('/api/rental/application/.*/approve'), 'post', () => {
      return successResponseWrap({});
    });

    Mock.mock(new RegExp('/api/rental/application/.*/reject'), 'post', () => {
      return successResponseWrap({});
    });
  },
});
