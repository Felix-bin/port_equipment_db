import axios from 'axios';
import qs from 'query-string';

export interface SettlementFeeRecord {
  id: string;
  settlementCode: string;
  rentalOrder: string;
  applicant: string;
  rentalDays: number;
  dailyRate: number;
  equipmentFee: number;
  usageFee: number;
  damageFee: number;
  discount: number;
  totalAmount: number;
  paymentMethod: 'cash' | 'transfer' | 'check' | 'other';
  settlementTime: string;
  status: 'pending' | 'paid' | 'overdue';
  remark?: string;
}

export interface SettlementFeeParams extends Partial<SettlementFeeRecord> {
  current: number;
  pageSize: number;
}

export interface SettlementFeeListRes {
  list: SettlementFeeRecord[];
  total: number;
}

export function querySettlementFeeList(params: SettlementFeeParams) {
  return axios.get<SettlementFeeListRes>('/api/settlement/fee', {
    params,
    paramsSerializer: (obj) => {
      return qs.stringify(obj);
    },
  });
}

export function createSettlementFee(data: Partial<SettlementFeeRecord>) {
  return axios.post('/api/settlement/fee', data);
}

export function paySettlementFee(id: string) {
  return axios.post(`/api/settlement/fee/${id}/pay`);
}
