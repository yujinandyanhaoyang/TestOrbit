
import type { DataResponse } from '@/api/response/types';

// 登录返回数据结构
export interface LoginData {
    token: string;     // token
    user_info: {
        username: string;  // 用户名
        name: string;     // 用户昵称
    };
}

// 登录响应数据类型
export type LoginResponse = DataResponse<LoginData>;

// 登录请求参数接口
export interface LoginRequest {
    username: string;
    password: string;
    remember?: boolean;
}

// 用户详细信息数据类型
export interface UserInfo {
  id: number;
  last_login: string | null; // 可能为 null（未登录过）
  is_superuser: boolean;
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  is_staff: boolean;
  is_active: boolean;
  date_joined: string; // ISO 8601 格式时间字符串
  real_name: string;
  groups: any[]; // 此处可根据实际数据类型细化，如 Group[]
  user_permissions: any[]; // 此处可根据实际数据类型细化，如 Permission[]
}

// 用户列表数据结构
export interface UserListData {
  total: number;
  data: UserInfo[];
}

// API响应类型
export type GetUserInfoResponse = DataResponse<UserListData>;