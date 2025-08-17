// 场景测试相关API接口
// 引入二次封装的请求方法
import request from '@/utils/request'
import type { TestModuleTreeResponse, 
            CaseGroupListResponse,
             GlobalVarListResponse
        } from './types'

// API枚举
enum API {
    // 测试场景结构树
    CASE_MODULE_TREE = '/api-data/tree-case-module',
    // 场景测试文件夹接口
    CASEFOLDER_MODULE = '/api-data/case-module-view',
    // 用例操作相关接口
    CASE_TEST_URL = '/api-data/case-view',
    CASE_TEST_COPY_URL = '/api-data/copy-cases',
    CASE_TEST_CLEAR_URL = '/api-data/clean-deleted-cases',
    CASE_GROUP_RUN_URL = '/api-data/run-api-cases',

    // 变量相关接口
    // 全局变量
    GLOBAL_VARIABLES = '/project/project-view'
    
}

/**
 * 获取场景测试文件树
 * @returns 场景测试文件树结构
 */
export const getCaseFolderTree = (): Promise<TestModuleTreeResponse> => {
    return request.get(API.CASE_MODULE_TREE)
}

/**
 * 创建测试模块
 * @param name 模块名称
 * @param parent_id 父模块ID，顶级模块传null
 * @returns 创建结果
 */
export const createTestModule = (name: string, parent?: string | null): Promise<any> => {
    return request.post(API.CASEFOLDER_MODULE, { name, parent })
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

// 获取文件下的用例组列表
export const getCaseGroupList = (page:number = 1,page_size:number = 20,is_deleted:boolean = false,  name?:string, module_id?:string): Promise<CaseGroupListResponse> => {
    return request.get(`${API.CASE_TEST_URL}`, {
        params: {
            page,
            page_size,
            is_deleted,
            module_id, //请求参数包含module_id时根据模块ID过滤
            name //请求参数包含name时根据用例名称过滤
        }
    })
}

// 删除用例组
export const DeleteCaseGroup = (id: number): Promise<any> => {
    return request.delete(`${API.CASE_TEST_URL}?id=` + id)
}

// 复制用例组
export const CopyCaseGroup = (case_id: number): Promise<any> => {
    return request.post(
        API.CASE_TEST_COPY_URL,
        {
            case_id
        }
        
    )
}

// 还原用例组
export const RestoreCaseGroup = (id: number,is_deleted:string): Promise<any> => {
    return request.patch(`${API.CASE_TEST_URL}`, { id,is_deleted })
}
// 彻底删除用例组
export const RealDeleteCaseGroup = (id: number,real_delete:boolean): Promise<any> => {
    return request.delete(`${API.CASE_TEST_URL}`, { params: { id, real_delete } })
}
// 清空回收站
export const ClearCaseGroup = (): Promise<any> => {
    return request.delete(API.CASE_TEST_CLEAR_URL)
}

// 用例组相关接口
// 运行用例组
// 请求体类型caseIds: [4, 32], envir: 1
export const runCaseGroup = (caseIds: number[], envir:number): Promise<any> => {
    return request.post(
        // 路径
        API.CASE_GROUP_RUN_URL,
        // 请求体
        { case: caseIds, envir }
    )
}

// 获取全局变量列表
export const getGlobalVariables = (page:number = 1,page_size:number = 20): Promise< GlobalVarListResponse> => {
    return request.get(`${API.GLOBAL_VARIABLES}`, {
        params: {
            page,
            page_size
        }
    })
}

// 新增全局变量
export const addGlobalVariables = (data:any): Promise<any> => {
    return request.post(
        API.GLOBAL_VARIABLES,
        data
    )
}

// 更新全局变量
export const updateGlobalVariables = (data:any): Promise<any> => {
    return request.patch(
        API.GLOBAL_VARIABLES,
        data
    )
}

// 删除全局变量
export const deleteGlobalVariables = (id: number): Promise<any> => {
    return request.delete(`${API.GLOBAL_VARIABLES}`, { params: { id } })
}