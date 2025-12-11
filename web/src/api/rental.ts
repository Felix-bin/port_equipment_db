import axios from 'axios';
import qs from 'query-string';

export interface RentalApplicationRecord {
  id: string;
  applicationCode: string;
  applicant: string;
  equipmentType: string;
  equipmentCode: string;
  quantity: number;
  startDate: string;
  endDate: string;
  purpose?: string;
  applicationTime: string;
  status: 'pending' | 'approved' | 'rejected' | 'completed';
  remark?: string;
}

export interface RentalApplicationParams
  extends Partial<RentalApplicationRecord> {
  current: number;
  pageSize: number;
}

export interface RentalApplicationListRes {
  list: RentalApplicationRecord[];
  total: number;
}

export function queryRentalApplicationList(params: RentalApplicationParams) {
  return axios.get<RentalApplicationListRes>('/api/rental/application', {
    params,
    paramsSerializer: (obj) => {
      return qs.stringify(obj);
    },
  });
}

export function createRentalApplication(
  data: Partial<RentalApplicationRecord>
) {
  return axios.post('/api/rental/application', data);
}

export function approveRentalApplication(id: string) {
  return axios.post(`/api/rental/application/${id}/approve`);
}

export function rejectRentalApplication(id: string) {
  return axios.post(`/api/rental/application/${id}/reject`);
}

export interface RentalVoyageRecord {
  id: string;
  voyageNumber: string;
  rentalOrder: string;
  vesselName: string;
  equipmentList?: string;
  usageHours?: number;
  voyageDate: string;
  status: 'in-progress' | 'completed' | 'cancelled';
  remark?: string;
}

export interface RentalVoyageParams extends Partial<RentalVoyageRecord> {
  current: number;
  pageSize: number;
}

export interface RentalVoyageListRes {
  list: RentalVoyageRecord[];
  total: number;
}

export function queryRentalVoyageList(params: RentalVoyageParams) {
  return axios.get<RentalVoyageListRes>('/api/rental/voyage', {
    params,
    paramsSerializer: (obj) => {
      return qs.stringify(obj);
    },
  });
}

export function createRentalVoyage(data: Partial<RentalVoyageRecord>) {
  return axios.post('/api/rental/voyage', data);
}

export function completeRentalVoyage(id: string) {
  return axios.post(`/api/rental/voyage/${id}/complete`);
}

export interface RentalReturnRecord {
  id: string;
  returnCode: string;
  rentalOrder: string;
  equipmentCode: string;
  equipmentName?: string;
  quantity: number;
  returnTime: string;
  equipmentCondition: 'good' | 'normal' | 'damaged';
  damageDescription?: string;
  inspectionResult?: string;
  inspector?: string;
  inspectionStatus: 'pending' | 'passed' | 'failed';
  remark?: string;
}

export interface RentalReturnParams extends Partial<RentalReturnRecord> {
  current: number;
  pageSize: number;
}

export interface RentalReturnListRes {
  list: RentalReturnRecord[];
  total: number;
}

export function queryRentalReturnList(params: RentalReturnParams) {
  return axios.get<RentalReturnListRes>('/api/rental/return', {
    params,
    paramsSerializer: (obj) => {
      return qs.stringify(obj);
    },
  });
}

export function createRentalReturn(data: Partial<RentalReturnRecord>) {
  return axios.post('/api/rental/return', data);
}

export function inspectRentalReturn(data: Partial<RentalReturnRecord>) {
  return axios.post(`/api/rental/return/${data.id}/inspect`, data);
}

// 租赁分析统计
export interface RentalAnalysisStats {
  total_orders: number;
  total_outbound: number;
  total_renting: number;
  total_returned: number;
  orders_growth: number;
  outbound_growth: number;
  renting_growth: number;
  returned_growth: number;
  category_ratio: Array<{ name: string; value: number }>;
  popular_equipment: Array<{
    equipment_name: string;
    rental_count: number;
    rental_days: number;
  }>;
  period_analysis: {
    xAxis: string[];
    data: Array<{ name: string; value: number[] }>;
  };
}

export function queryRentalAnalysis() {
  return axios.get<RentalAnalysisStats>('/api/rental/analysis');
}
