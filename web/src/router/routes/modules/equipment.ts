import { DEFAULT_LAYOUT } from '../base';
import { AppRouteRecordRaw } from '../types';

const EQUIPMENT: AppRouteRecordRaw = {
  path: '/equipment',
  name: 'equipment',
  component: DEFAULT_LAYOUT,
  meta: {
    locale: 'menu.equipment',
    requiresAuth: true,
    icon: 'icon-archive',
    order: 1,
  },
  children: [
    {
      path: 'inbound',
      name: 'EquipmentInbound',
      component: () => import('@/views/equipment/inbound/index.vue'),
      meta: {
        locale: 'menu.equipment.inbound',
        requiresAuth: true,
        roles: ['*'],
      },
    },
    {
      path: 'inventory',
      name: 'EquipmentInventory',
      component: () => import('@/views/equipment/inventory/index.vue'),
      meta: {
        locale: 'menu.equipment.inventory',
        requiresAuth: true,
        roles: ['*'],
      },
    },
    {
      path: 'outbound',
      name: 'EquipmentOutbound',
      component: () => import('@/views/equipment/outbound/index.vue'),
      meta: {
        locale: 'menu.equipment.outbound',
        requiresAuth: true,
        roles: ['*'],
      },
    },
  ],
};

export default EQUIPMENT;
