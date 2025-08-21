import type { DataResponse, ListResponse } from '@/api/response/types';

// 定义变量数据类型

// 全局变量
export interface GlobalVarInfo {
    id: number;
    created: string;
    updated: string;
    name: string;
    remark: string;
}

// 全局变量列表返回结果
export type GlobalVarListResult = {
    total: number;
    data: GlobalVarInfo[];
}

// 全局变量列表响应接口
export type GlobalVarListResponse = DataResponse<GlobalVarListResult>;

// 创建全局变量请求体
export interface CreateGlobalVarRequest {
    name: string;
    remark: string;
    url: string;
}

// HTTP方法类型
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

// 请求头/查询参数值的数据类型
export interface ParamValueType {
    type: string;
    auto: boolean;
}

// 请求头项
export interface HeaderSourceItem {
    id: number;
    value: string;
    type: ParamValueType;
    name: string;
}

// 查询参数项
export interface QuerySourceItem {
    id: number;
    name: string;
    type: ParamValueType;
    value: string;
}

// 请求体来源
export interface BodySourceItem {
    name: string;
    id: number;
}

// 添加测试步骤请求参数
export interface AddCaseStepRequest {
    step_name: string;         // 步骤名称
    name: string;              // 名称
    env_id: number;        // 项目ID
    method: HttpMethod;        // HTTP方法
    host: string;              // 主机地址
    host_type: number;         // 主机类型
    path: string;              // 请求路径
    ban_redirects: boolean;    // 是否禁止重定向
    header_mode: number;       // 请求头模式
    header_source: HeaderSourceItem[]; // 请求头数据源
    query_mode: number;        // 查询参数模式
    query_source: QuerySourceItem[];   // 查询参数数据源
    body_mode: number;         // 请求体模式
    body_source?: BodySourceItem;      // 请求体数据源
    expect_mode: number;       // 期望模式
    expect_source: any[];      // 期望数据源
    output_mode: number;       // 输出模式
    output_source: any[];      // 输出数据源
    is_case: boolean;          // 是否为测试用例
}

// 请求头或查询参数项（通用结构）
export interface ParamItem {
  id: number;
  name: string;
  value: string;
  type: ParamValueType;
}

// API步骤的参数定义
export interface ApiStepParams {
  host: string;            // API主机地址
  name: string;            // 步骤名称
  path?: string;           // 请求路径
  method?: HttpMethod;     // HTTP方法
  api_id?: number;         // API ID
  body_mode: number;       // 请求体模式
  host_type: number;       // 主机类型
  query_mode: number;      // 查询参数模式
  body_source: {           // 请求体数据
    [key: string]: any;
  };
  expect_mode: number;     // 期望模式
  header_mode: number;     // 请求头模式
  output_mode: number;     // 输出模式
  query_source: ParamItem[]; // 查询参数列表
  ban_redirects: boolean;  // 禁止重定向
  expect_source: any[];    // 期望断言列表
  header_source: ParamItem[]; // 请求头列表
  output_source: any[];    // 输出参数提取列表
}

// 用例步骤定义
export interface CaseStep {
  id: number;               // 步骤ID
  params: ApiStepParams;    // 步骤参数
  step_name: string;        // 步骤名称
  type: string;             // 步骤类型，如 "api"
  status: number;           // 步骤状态
  enabled: boolean;         // 是否启用
  controller_data: any;     // 控制器数据
  retried_times: number;    // 重试次数
  results: any;             // 执行结果
}
