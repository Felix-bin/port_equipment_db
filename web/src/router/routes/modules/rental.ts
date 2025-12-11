import { DEFAULT_LAYOUT } from '../base';
import { AppRouteRecordRaw } from '../types';

const RENTAL: AppRouteRecordRaw = {
  path: '/rental',
  name: 'rental',
  component: DEFAULT_LAYOUT,
  meta: {
    locale: 'menu.rental',
    requiresAuth: true,
    icon: 'icon-calendar',
    order: 2,
  },
  children: [
    {
      path: 'application',
      name: 'RentalApplication',
      component: () => import('@/views/rental/application/index.vue'),
      meta: {
        locale: 'menu.rental.application',
        requiresAuth: true,
        roles: ['*'],
      },
    },
    {
      path: 'voyage',
      name: 'RentalVoyage',
      component: () => import('@/views/rental/voyage/index.vue'),
      meta: {
        locale: 'menu.rental.voyage',
        requiresAuth: true,
        roles: ['*'],
      },
    },
    {
      path: 'return',
      name: 'RentalReturn',
      component: () => import('@/views/rental/return/index.vue'),
      meta: {
        locale: 'menu.rental.return',
        requiresAuth: true,
        roles: ['*'],
      },
    },
  ],
};

export default RENTAL;
