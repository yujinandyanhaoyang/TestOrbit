import type { DataResponse, ListResponse } from '@/api/response/types';
/***
 * 
 * 模块文件类型定义
 */
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
