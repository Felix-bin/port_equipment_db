import axios from 'axios';
import type { TableData } from '@arco-design/web-vue/es/table/interface';

export interface ContentDataRecord {
  x: string;
  y: number;
}

export function queryContentData() {
  return axios.get<ContentDataRecord[]>('/api/content-data');
}

export interface PopularRecord {
  key: number;
  clickNumber: string;
  title: string;
  increases: number;
}

export function queryPopularList(params: { type: string }) {
  return axios.get<TableData[]>('/api/popular/list', { params });
}

export interface DashboardStats {
  total_equipment: number;
  in_stock: number;
  out_stock: number;
  maintenance: number;
  pending_checkout: number;
  in_progress_orders: number;
  pending_inspection: number;
  total_revenue: number;
  pending_amount: number;
  overdue_bills: number;
}

export function queryDashboardStats() {
  return axios.get<DashboardStats>('/api/dashboard/stats');
}
