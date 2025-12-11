import axios from 'axios';
import qs from 'query-string';

export interface EquipmentInboundRecord {
  id: string;
  equipmentCode: string;
  equipmentName: string;
  equipmentType: string;
  specification?: string;
  quantity: number;
  supplier: string;
  warehouse: string;
  location?: string;
  inboundTime: string;
  status: 'pending' | 'completed' | 'rejected';
  remark?: string;
}

export interface EquipmentInboundParams
  extends Partial<EquipmentInboundRecord> {
  current: number;
  pageSize: number;
}

export interface EquipmentInboundListRes {
  list: EquipmentInboundRecord[];
  total: number;
}

export function queryEquipmentInboundList(params: EquipmentInboundParams) {
  return axios.get<EquipmentInboundListRes>('/api/equipment/inbound', {
    params,
    paramsSerializer: (obj) => {
      return qs.stringify(obj);
    },
  });
}

export function createEquipmentInbound(data: Partial<EquipmentInboundRecord>) {
  return axios.post('/api/equipment/inbound', data);
}

export interface EquipmentInventoryRecord {
  id: string;
  equipmentCode: string;
  equipmentName: string;
  equipmentType: string;
  totalQuantity: number;
  availableQuantity: number;
  rentedQuantity: number;
  warehouse: string;
  location?: string;
  status: 'available' | 'rented' | 'maintenance' | 'damaged';
  dailyRate?: number;
  inboundDate?: string;
  supplier?: string;
  specifications?: string;
}

export interface EquipmentInventoryParams
  extends Partial<EquipmentInventoryRecord> {
  current: number;
  pageSize: number;
  keyword?: string;
}

export interface EquipmentInventoryListRes {
  list: EquipmentInventoryRecord[];
  total: number;
}

export function queryEquipmentInventoryList(params: EquipmentInventoryParams) {
  return axios.get<EquipmentInventoryListRes>('/api/equipment/inventory', {
    params,
    paramsSerializer: (obj) => {
      return qs.stringify(obj);
    },
  });
}

export interface EquipmentOutboundRecord {
  id: string;
  outboundCode: string;
  rentalOrder: string;
  equipmentCode: string;
  equipmentName?: string;
  quantity: number;
  outboundTime: string;
  operator: string;
  status: 'pending' | 'completed' | 'cancelled';
  remark?: string;
}

export interface EquipmentOutboundParams
  extends Partial<EquipmentOutboundRecord> {
  current: number;
  pageSize: number;
}

export interface EquipmentOutboundListRes {
  list: EquipmentOutboundRecord[];
  total: number;
}

export function queryEquipmentOutboundList(params: EquipmentOutboundParams) {
  return axios.get<EquipmentOutboundListRes>('/api/equipment/outbound', {
    params,
    paramsSerializer: (obj) => {
      return qs.stringify(obj);
    },
  });
}

export function createEquipmentOutbound(
  data: Partial<EquipmentOutboundRecord>
) {
  return axios.post('/api/equipment/outbound', data);
}

export function deleteEquipmentOutbound(outboundId: string) {
  return axios.delete(`/api/equipment/outbound/${outboundId}`);
}

export interface EquipmentUpdateParams {
  equipment_name?: string;
  category?: string;
  status?: 'available' | 'rented' | 'maintenance';
  storage_location?: string;
  daily_rental_rate?: number;
  specifications?: string;
  remarks?: string;
}

export function updateEquipment(
  equipmentId: string,
  data: EquipmentUpdateParams
) {
  return axios.put(`/api/equipment/${equipmentId}`, data);
}

export function getEquipmentById(equipmentId: string) {
  return axios.get(`/api/equipment/${equipmentId}`);
}

export function deleteEquipment(equipmentId: string) {
  return axios.delete(`/api/equipment/${equipmentId}`);
}

export interface EquipmentCreateParams {
  equipment_code?: string;
  equipment_name: string;
  category: string;
  storage_location?: string;
  purchase_price?: number;
  daily_rental_rate?: number;
  specifications?: string;
  remarks?: string;
}

export function createEquipment(data: EquipmentCreateParams) {
  return axios.post('/api/equipment', data);
}
