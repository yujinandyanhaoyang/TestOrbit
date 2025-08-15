//用户相关接口
//引入二次封装的请求方法
import request from '@/utils/request'

//引入请求和响应的类型规则
import type { GetUserInfoResponse,GetProjectInfoResponse,LoginResponse } from './types'
import { id } from 'element-plus/es/locales.mjs'

//API枚举
enum API {

    //用户接口
    USERLIST_URL = '/user/user-view',
    USERLOGIN_URL = '/user/login',
    // 项目接口
    PROJECTLIST_URL = '/conf/envir-view',
    // 用例接口
    //测试场景结构树
    CASELIST_URL = '/api-data/tree-case-module',

}

// 用户登录
export const userLogin = (username: string, password: string) : Promise<LoginResponse> => {
    return request.post(API.USERLOGIN_URL, { username, password })
}
// 获取用户列表
export const getUserList = (page: Number, page_size: Number) : Promise<GetUserInfoResponse> => {
    return request.get(API.USERLIST_URL, 
        { params:{
            page,
            page_size
        }

     })
}
// 更新用户状态
export const updateUserStatus = (id: number, is_active: boolean) : Promise<any> => {
    return request.patch(API.USERLIST_URL, { id, is_active })
}
//更新用户信息
export const updateUserInfo = (data: any) : Promise<any> => {
    return request.patch(API.USERLIST_URL, data)
}
// 新增用户
export const addUser = (data: any) : Promise<any> => {
    return request.post(API.USERLIST_URL, data)
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

// 测试用例
// 获取场景树
export const getCaseFolderTree = () : Promise<any> => {
    return request.get(API.CASELIST_URL)
}