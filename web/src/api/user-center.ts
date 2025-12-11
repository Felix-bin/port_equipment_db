import axios from 'axios';

export interface MyProjectRecord {
  id: number;
  name: string;
  description: string;
  peopleNumber: number;
  contributors: {
    name: string;
    email: string;
    avatar: string;
  }[];
}
export function queryMyProjectList() {
  return axios.post('/api/user/my-project/list');
}

export interface MyTeamRecord {
  id: number;
  avatar: string;
  name: string;
  peopleNumber: number;
}
export function queryMyTeamList() {
  return axios.post('/api/user/my-team/list');
}

export interface LatestActivity {
  id: number;
  title: string;
  description: string;
  avatar: string;
}
export function queryLatestActivity() {
  return axios.post<LatestActivity[]>('/api/user/latest-activity');
}

export function saveUserInfo(userId: number, data: BasicInfoModel) {
  return axios.post('/api/user/save-info', data, {
    params: { user_id: userId }
  });
}

export function getUserInfo(userId: number) {
  return axios.get('/api/user/info', {
    params: { user_id: userId }
  });
}

export function updateUserInfo(userId: number, data: BasicInfoModel) {
  return axios.put(`/api/user/info/${userId}`, data);
}

export interface BasicInfoModel {
  email: string;
  nickname: string;
  countryRegion: string;
  area: string;
  address: string;
  profile: string;
}

export function userUploadApi(
  data: FormData,
  onUploadProgress?: (progressEvent: any) => void
) {
  // user_id已经在FormData中，不需要作为查询参数
  // 注意：不要手动设置 Content-Type，axios 会自动为 FormData 设置正确的 Content-Type（包括 boundary）
  
  return axios.post('/api/user/upload', data, {
    onUploadProgress: onUploadProgress || undefined,
  });
}
