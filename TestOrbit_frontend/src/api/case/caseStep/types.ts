import type { DataResponse, ListResponse } from '@/api/response/types';

// =================== 基础类型定义 ===================

// HTTP方法类型
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

// =================== 参数相关类型 ===================

// 参数值类型基础结构
export interface ValueType {
  type: string;
  auto?: boolean;
}

// 基础参数项结构
export interface BaseParam {
  name: string;
  value: string;
}

// 带ID的参数项结构
export interface ParamWithId extends BaseParam {
  id: number;
}

// 请求头/查询参数值的数据类型
export interface ParamValueType {
  type: string;
  auto: boolean;
}

// 带类型的参数项（通用）
export interface TypedParam extends ParamWithId {
  type: ParamValueType;
}

// 请求头项
export interface HeaderSourceItem extends TypedParam {}

// 查询参数项
export interface QuerySourceItem extends TypedParam {}

// 请求体来源
export interface BodySourceItem {
  name: string;
  id: number;
}

// 扩展版的参数类型 (不需要ID)
export interface ExtendedBaseParam {
  name: string;
  type: {
    type: string;
  };
  value: string;
}

// 扩展版的查询参数
export interface ExtendedQueryParam extends ExtendedBaseParam {}

// 扩展版的头部参数
export interface ExtendedHeaderParam extends ExtendedBaseParam {}




// =================== 断言相关类型 ===================
// 断言规则定义
export interface Rule {
  id: number;                // 断言ID
  type: string;              // 断言类型，如 "jsonpath"
  expression: string;        // 断言表达式
  operator: string;          // 操作符，如 "=="
  expected_value: string;    // 期望值
  created: string;           // 创建时间
  updated: string;           // 更新时间
  enabled: boolean;          // 是否启用
  step: number;              // 所属步骤ID
  display_text: string;      // 显示文本
}

// 断言结果定义
export interface Result {
  rule: Rule;                // 断言规则
  message: string;           // 结果信息
  success: boolean;          // 是否成功
  actual_value: any;         // 实际值
}


// =================== 请求/响应相关类型 ===================
// 请求日志定义
export interface RequestLog {
  url: string;               // 请求URL
  body: any;                 // 请求体
  header: Record<string, string>; // 请求头
  method: string;            // 请求方法
  results: any;              // 请求结果
  response: any;             // 响应内容
  res_header: Record<string, string>; // 响应头
  spend_time: number;        // 花费时间
  assertion_results?: Result[]; // 断言结果
}

// 执行结果定义
export interface StepResult {
  message: any;              // 结果消息
  request_log: RequestLog;   // 请求日志
}

// =================== API步骤参数类型 ===================

// 基础API参数
export interface BaseApiParams {
  host: string;                // 主机地址
  path: string;                // 请求路径
  method: HttpMethod;          // HTTP方法
}



// 扩展的步骤参数-具体参数信息
export interface ApiStepParams extends BaseApiParams {
  timeout: number;             // 超时时间
  body_mode: number;           // 请求体模式
  host_type: number;           // 主机类型
  query_mode: number;          // 查询参数模式
  body_source: any;            // 请求体内容
  expect_mode: number;         // 期望模式
  header_mode: number;         // 请求头模式
  output_mode: number;         // 输出模式
  query_source: ExtendedQueryParam[]; // 查询参数列表
  ban_redirects: boolean;      // 禁止重定向
  expect_source: any[];        // 期望源
  header_source: ExtendedHeaderParam[]; // 请求头列表
  output_source: any[];        // 输出源
}

// =================== 用例步骤定义 ===================

// 基础步骤属性
export interface BaseStepProps {
  id: number;                  // 步骤ID
  step_name: string;           // 步骤名称
  type: string;                // 步骤类型，如 "api"
  enabled: boolean;            // 是否启用
}

// 用例步骤定义 - 更新为后端最新格式
export interface CaseStep extends BaseStepProps {
  step_order: number;          // 步骤顺序
  status: number;              // 步骤状态
  controller_data: any | null;        // 控制器数据
  retried_times: any | null;          // 重试次数，可能为null
  results: StepResult;    // 执行结果
  params: ApiStepParams; // 步骤参数（扩展版）
  timeout: number | null;             // 超时时间
  source: string | null;              // 来源
  assertions: Rule[]; // 断言规则列表
}

// =================== 请求/响应相关类型 ===================

// 添加测试步骤请求参数
export interface AddCaseStepRequest {
  case_id: number;             // 所属用例ID
  env_id: number;              // 所属环境ID
  steps: CaseStep[];           // 步骤列表
}

// =================== 全局变量相关类型 ===================

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
