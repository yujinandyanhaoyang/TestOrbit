// 场景测试相关API接口
// 引入二次封装的请求方法
import request from '@/utils/request'
import type { TestModuleTreeResponse } from '@/api/case/module/types';

// API枚举
enum API {
    // 测试模块（测试场景结构树）
    CASE_MODULE_TREE = '/api-data/tree-case-module',
    // 测试文件夹接口
    CASEFOLDER_MODULE = '/api-data/case-module-view',
}


/**
 * 获取场景测试文件树
 * @param projectId 可选的项目ID
 * @returns 场景测试文件树结构
 */
export const getCaseFolderTree = (projectId?: number): Promise<TestModuleTreeResponse> => {
    // 如果提供了项目ID，则使用它
    if (projectId !== undefined) {
        return request.get(API.CASE_MODULE_TREE, { 
            params: { 
                project_id: projectId 
            } 
        })
    }
    // 否则不传项目ID参数
    return request.get(API.CASE_MODULE_TREE)
}

/**
 * 创建测试模块
 * @param name 模块名称
 * @param parent_id 父模块ID，顶级模块传null
 * @param projectId 项目ID
 * @returns 创建结果
 */
export const createTestModule = (name: string, parent?: string | null, projectId?: number): Promise<any> => {
    return request.post(API.CASEFOLDER_MODULE, { name, parent, project_id: projectId })
}

/**
 * 更新测试模块
 * @param id 模块ID
 * @param name 新的模块名称
 * @returns 更新结果
 */
export const updateTestModule = (id: string, name: string): Promise<any> => {
    return request.patch(API.CASEFOLDER_MODULE, { id, name })
}

/**
 * 删除测试模块
 * @param id 要删除的模块ID
 * @returns 删除结果
 */
export const deleteTestModule = (id: string): Promise<any> => {
    return request.delete(API.CASEFOLDER_MODULE, { params: { id } })
}

/**
 * 通过module_id获取模块详情
 * @param id 模块ID
 * @returns 模块详情
 */
export const getTestModuleDetail = (id: string): Promise<any> => {
    return request.get(API.CASEFOLDER_MODULE, { params: { id } })
}
