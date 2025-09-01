import type { DataResponse, ListResponse } from '@/api/response/types';
import type { CaseStep } from '../caseStep/types';

//场景用例信息
export interface CaseGroupInfo {
  id: number;           // 用例ID
  name: string;         // 用例名称
  creater_name: string; // 创建者名称
  latest_run_time: string | null; // 最近运行时间
  updater_name?: string | null; // 更新者名称，可选
  updated: string;      // 更新时间
  created: string;      // 创建时间
  status: number;       // 状态码，表示用例状态
  updater?: number | null; // 更新者ID，可选
}

// 场景用例列表返回结果
export type CaseGroupListResult = {
    total: number;
    data: CaseGroupInfo[];
}

// 场景用例列表响应接口
export type CaseGroupListResponse = DataResponse<CaseGroupListResult>;

// 用例组创建/更新请求体
export interface AddCaseGroupRequest {
  name: string;            // 用例组名称
  env_id: number;          // 环境ID
  case_id?: number;             // 用例组ID，更新时需要
  module_id: string;      // 模块ID
  steps: CaseStep[];       // 测试步骤列表
}

// 用例组创建响应
export type AddCaseGroupResponse = DataResponse<{
  id: number;              // 创建的用例组ID
  success: boolean;        // 是否成功
  message?: string;        // 消息
}>;


// 用例组详情接口
export interface CaseGroupDetail {
  id: number;               // 用例组ID
  name: string;             // 用例组名称
  remark: string | null;    // 备注
  steps: CaseStep[];        // 测试步骤列表
  module_id: string;        // 模块ID
  latest_run_time: string | null; // 最近运行时间
  updated: string;          // 更新时间
  module_related: string[]; // 关联的模块ID列表
  only_show: boolean;       // 是否仅显示
}

// 用例组详情响应接口
export type CaseGroupDetailResponse = DataResponse<CaseGroupDetail>;
