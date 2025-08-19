// 场景测试相关API接口
// 引入二次封装的请求方法
import request from '@/utils/request'
import type { 
    AddCaseGroupRequest, 
    AddCaseGroupResponse, 
    CaseGroupDetailResponse 
} from './types'

// API枚举
enum API {

    // 用例组操作相关接口
    CASE_GROUP_URL = '/api-data/case-view',
    CASE_GROUP_COPY_URL = '/api-data/copy-cases',
    CASE_GROUP_CLEAR_URL = '/api-data/clean-deleted-cases',
    CASE_GROUP_RUN_URL = '/api-data/run-api-cases',

}


// 用例组相关接口
// 运行用例组
// 请求体类型
export const runCaseGroup = (caseIds: number[], envir:number): Promise<any> => {
    return request.post(
        // 路径
        API.CASE_GROUP_RUN_URL,
        // 请求体
        { case: caseIds, envir }
    )
}
// 新建用例组
export const addCaseGroup = (data: AddCaseGroupRequest): Promise<AddCaseGroupResponse> => {
    return request.post(
        API.CASE_GROUP_URL,
        data
    )
}
// 获取文件下的用例组列表
export const getCaseGroupList = (page:number = 1,page_size:number = 20,is_deleted:boolean = false,  name?:string, module_id?:string): Promise<any> => {
    return request.get(`${API.CASE_GROUP_URL}`, {
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
    return request.delete(`${API.CASE_GROUP_URL}?id=` + id)
}

// 复制用例组
export const CopyCaseGroup = (case_id: number): Promise<any> => {
    return request.post(
        API.CASE_GROUP_COPY_URL,
        {
            case_id
        }
        
    )
}

// 获取单个用例组详情信息
export const getCaseGroupDetail = (group_id: number): Promise<CaseGroupDetailResponse> => {
    return request.get(`${API.CASE_GROUP_URL}?id=` + group_id)
}






/**
 * 
 回收站部分方法
 */
// 还原用例组
export const RestoreCaseGroup = (id: number,is_deleted:string): Promise<any> => {
    return request.patch(`${API.CASE_GROUP_URL}`, { id,is_deleted })
}
// 彻底删除用例组
export const RealDeleteCaseGroup = (id: number,real_delete:boolean): Promise<any> => {
    return request.delete(`${API.CASE_GROUP_URL}`, { params: { id, real_delete } })
}
// 清空回收站
export const ClearCaseGroup = (): Promise<any> => {
    return request.delete(API.CASE_GROUP_CLEAR_URL)
}







