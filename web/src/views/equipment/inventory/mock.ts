import Mock from 'mockjs';
import qs from 'query-string';
import setupMock, { successResponseWrap } from '@/utils/setup-mock';
import { GetParams } from '@/types/global';

const { Random } = Mock;

const data = Mock.mock({
  'list|40': [
    {
      'id|8': /[A-Z][0-9]/,
      'equipmentCode|8': /EQ[0-9]{6}/,
      'equipmentName|1': ['门式起重机', '桥式起重机', '叉车', '集装箱', '吊具'],
      'equipmentType|1': ['crane', 'forklift', 'container', 'other'],
      'totalQuantity|10-100': 1,
      'availableQuantity|5-50': 1,
      'rentedQuantity|0-30': 1,
      'warehouse|1': ['1号仓库', '2号仓库', '3号仓库'],
      'location': '@word(2,4)区@word(1,2)号位',
      'status|1': ['available', 'rented', 'maintenance', 'damaged'],
    },
  ],
});

// 禁用 mock，使用真实的后端 API
setupMock({
  mock: false, // 设置为 false 禁用 mock
  setup() {
    Mock.mock(new RegExp('/api/equipment/inventory'), (params: GetParams) => {
      const { current = 1, pageSize = 10 } = qs.parseUrl(params.url).query;
      const p = current as number;
      const ps = pageSize as number;
      return successResponseWrap({
        list: data.list.slice((p - 1) * ps, p * ps),
        total: 40,
      });
    });
  },
});
