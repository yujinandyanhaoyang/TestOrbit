import type { DataResponse, ListResponse } from '@/api/response/types';

// 场景测试文件/模块节点接口
export interface TestModuleNode {
  id: string;           // 模块ID
  parent_id: string | null; // 父模块ID，顶级模块为null
  name: string;         // 模块名称
  module_related: string[]; // 相关模块ID列表
  children: TestModuleNode[]; // 子模块列表，递归定义
}

// 场景测试文件树响应接口
export type TestModuleTreeResponse = ListResponse<TestModuleNode>;

// 适用于Element Plus的Tree组件数据结构
export interface ElTreeNode {
  id?: string;          // 节点ID
  label: string;        // 显示的文本
  children?: ElTreeNode[]; // 子节点
  isLeaf?: boolean;     // 是否为叶子节点
  disabled?: boolean;   // 是否禁用
  data?: any;           // 节点原始数据，可用于存储完整的TestModuleNode
}

// 转换函数：将API返回的模块树转换为Element Plus Tree组件所需格式
export function convertToElTreeData(modules: TestModuleNode[]): ElTreeNode[] {
  return modules.map(module => ({
    id: module.id,
    label: module.name,
    children: module.children?.length > 0 ? convertToElTreeData(module.children) : undefined,
    isLeaf: module.children?.length === 0,
    data: module // 保存原始数据
  }));
}


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
    envir_1_host: string;
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
    project_id: number;        // 项目ID
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
