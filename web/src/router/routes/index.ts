import type { RouteRecordNormalized } from 'vue-router';

// 只导入需要的路由模块
import dashboard from './modules/dashboard';
import equipment from './modules/equipment';
import rental from './modules/rental';
import settlement from './modules/settlement';
import visualization from './modules/visualization';
import system from './modules/system';
import user from './modules/user';

// 排除不需要的外部模块
// 加载外部模块，但排除 arco 和 faq
const allExternalModules = import.meta.glob('./externalModules/*.ts', {
  eager: true,
});

// 过滤掉不需要的外部模块
const externalModules: Record<string, any> = {};
Object.keys(allExternalModules).forEach((key) => {
  if (!key.includes('arco.ts') && !key.includes('faq.ts')) {
    externalModules[key] = allExternalModules[key];
  }
});

function formatModules(_modules: any, result: RouteRecordNormalized[]) {
  Object.keys(_modules).forEach((key) => {
    const module = _modules[key];
    const defaultModule = module.default || module;
    if (!defaultModule) return;
    const moduleList = Array.isArray(defaultModule)
      ? [...defaultModule]
      : [defaultModule];
    result.push(...moduleList);
  });
  return result;
}

// 只包含需要的路由模块
const modules = {
  dashboard: { default: dashboard },
  equipment: { default: equipment },
  rental: { default: rental },
  settlement: { default: settlement },
  visualization: { default: visualization },
  system: { default: system },
  user: { default: user },
};

export const appRoutes: RouteRecordNormalized[] = formatModules(modules, []);

export const appExternalRoutes: RouteRecordNormalized[] = formatModules(
  externalModules,
  []
);
