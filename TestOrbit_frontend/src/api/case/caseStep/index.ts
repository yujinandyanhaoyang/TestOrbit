// 场景测试相关API接口
// 引入二次封装的请求方法
import request from '@/utils/request'
import type { GlobalVarListResponse } from '@/api/case/caseStep/types';


// API枚举
enum API {
    // 用例组单步骤相关接口
    // 步骤接口
    CASE_GROUP_STEP_URL = '/api-data/api-view',
    // 运行单步测试用例
    CASE_GROUP_STEP_RUN_URL = '/api-data/test-api-data',

    // 变量相关接口
    // 全局变量
    GLOBAL_VARIABLES = '/config/env-view',
}


// 用例步骤相关接口
// 添加新步骤
export const addCaseStep = (data:any): Promise<any> => {
    return request.post(
        API.CASE_GROUP_STEP_URL,
        data
    )
}
// 运行单步骤
export const runCaseStep = (data:any) : Promise<any> => {
    return request.post(
        API.CASE_GROUP_STEP_RUN_URL,
        data
    )
}

// 获取步骤详情
export const getStepDetail = (id:number,is_case=true): Promise<any> => {
    return request.get(`${API.CASE_GROUP_STEP_URL}`, {
        params: {
            id,
            is_case
        }
    })
}





// 获取全局变量列表
export const getGlobalVariables = (): Promise<GlobalVarListResponse> => {
    return request.get(`${API.GLOBAL_VARIABLES}`, {
        params: {
            page: 1,
            page_size: 50
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