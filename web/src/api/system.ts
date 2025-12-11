import axios from 'axios';

export interface TriggerLog {
  id: number;
  log_type: 'success' | 'info' | 'warning' | 'error';
  trigger_name: string;
  operation: string;
  table_name: string | null;
  record_id: number | null;
  description: string | null;
  created_at: string;
}

export interface TriggerLogListParams {
  page?: number;
  page_size?: number;
  log_type?: string;
  trigger_name?: string;
  start_date?: string;
  end_date?: string;
}

export interface TriggerLogListResponse {
  items: TriggerLog[];
  total: number;
  page: number;
  page_size: number;
}

export function queryTriggerLogs(params: TriggerLogListParams) {
  return axios.get<TriggerLogListResponse>('/api/trigger-logs', { params });
}

export function getTriggerLogById(logId: number) {
  return axios.get<TriggerLog>(`/api/trigger-logs/${logId}`);
}

export interface TriggerLogCreate {
  log_type: string;
  trigger_name: string;
  operation: string;
  table_name?: string;
  record_id?: number;
  description?: string;
}

export function createTriggerLog(data: TriggerLogCreate) {
  return axios.post<TriggerLog>('/api/trigger-logs', data);
}

