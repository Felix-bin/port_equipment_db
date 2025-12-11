import localeMessageBox from '@/components/message-box/locale/zh-CN';

import localeWorkplace from '@/views/dashboard/workplace/locale/zh-CN';

import localeUserSetting from '@/views/user/setting/locale/zh-CN';
import localeLogin from '@/views/login/locale/zh-CN';

import localeEquipmentInbound from '@/views/equipment/inbound/locale/zh-CN';
import localeEquipmentInventory from '@/views/equipment/inventory/locale/zh-CN';
import localeEquipmentOutbound from '@/views/equipment/outbound/locale/zh-CN';
import localeRentalApplication from '@/views/rental/application/locale/zh-CN';
import localeRentalVoyage from '@/views/rental/voyage/locale/zh-CN';
import localeRentalReturn from '@/views/rental/return/locale/zh-CN';
import localeSettlementFee from '@/views/settlement/fee/locale/zh-CN';

import localeDataAnalysis from '@/views/visualization/data-analysis/locale/zh-CN';
import localeMultiDAnalysis from '@/views/visualization/multi-dimension-data-analysis/locale/zh-CN';

import localeSystemLog from '@/views/system/log/locale/zh-CN';

import localeSettings from './zh-CN/settings';

export default {
  'menu.dashboard': '仪表盘',
  'menu.dashboard.workplace': '工作台',
  'menu.equipment': '装备管理',
  'menu.rental': '租赁管理',
  'menu.settlement': '费用结算',
  'menu.visualization': '数据可视化',
  'menu.system': '系统管理',
  'menu.user': '个人中心',
  'navbar.docs': '文档中心',
  'navbar.action.locale': '切换为中文',
  ...localeSettings,
  ...localeMessageBox,
  ...localeLogin,
  ...localeWorkplace,
  ...localeUserSetting,
  ...localeEquipmentInbound,
  ...localeEquipmentInventory,
  ...localeEquipmentOutbound,
  ...localeRentalApplication,
  ...localeRentalVoyage,
  ...localeRentalReturn,
  ...localeSettlementFee,
  ...localeDataAnalysis,
  ...localeMultiDAnalysis,
  ...localeSystemLog,
};
