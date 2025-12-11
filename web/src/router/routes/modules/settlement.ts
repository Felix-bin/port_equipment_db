import { DEFAULT_LAYOUT } from '../base';
import { AppRouteRecordRaw } from '../types';

const SETTLEMENT: AppRouteRecordRaw = {
  path: '/settlement',
  name: 'settlement',
  component: DEFAULT_LAYOUT,
  meta: {
    locale: 'menu.settlement',
    requiresAuth: true,
    icon: 'icon-bookmark',
    order: 3,
  },
  children: [
    {
      path: 'fee',
      name: 'SettlementFee',
      component: () => import('@/views/settlement/fee/index.vue'),
      meta: {
        locale: 'menu.settlement.fee',
        requiresAuth: true,
        roles: ['*'],
      },
    },
  ],
};

export default SETTLEMENT;
