import axios from 'axios';

export interface LoginData {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  password: string;
  real_name?: string;
  email?: string;
  phone?: string;
}

export interface AuthResponse {
  code: number;
  message?: string;
  data?: any;
}

export function login(data: LoginData) {
  return axios.post<AuthResponse>('/api/auth/login', data);
}

export function register(data: RegisterData) {
  return axios.post<AuthResponse>('/api/auth/register', data);
}
