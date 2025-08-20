//用户相关接口
//引入二次封装的请求方法
import request from '@/utils/request'

//引入请求和响应的类型规则
import type { GetProjectInfoResponse } from './types'

//API枚举
enum API {

    // 项目接口
    PROJECTLIST_URL = '/project/project-view',

}


// 获取项目列表
export const getProjectList = (page: Number, page_size: Number) : Promise<GetProjectInfoResponse> => {
    return request.get(API.PROJECTLIST_URL, 
        { params:{
            page,
            page_size
        }

     })
}
//添加新项目
export const addProject = (name: string) : Promise<any> => {
    return request.post(API.PROJECTLIST_URL, { name })
}
// 编辑项目
export const editProject = (id: number, name:string) : Promise<any> => {
    return request.patch(
        API.PROJECTLIST_URL,
        { id, name }
    )
}
// 删除项目
export const deleteProject = (id:number) : Promise<any> => {
    return request.delete(
        API.PROJECTLIST_URL,
        { params: { id } }
    )
}

