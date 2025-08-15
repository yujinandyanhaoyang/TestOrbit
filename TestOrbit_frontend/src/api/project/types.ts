import type { DataResponse } from '@/api/response/types';

// 项目详细信息数据类型
export interface ProjectInfo {
  id: number;
  position: number;
  name: string;
}

// 项目列表数据结构
export interface ProjectListData {
  total: number;
  data: ProjectInfo[];
}

// 获取项目信息响应类型
export type GetProjectInfoResponse = DataResponse<ProjectListData>;