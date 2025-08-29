//用户相关接口
//引入二次封装的请求方法
import request from '@/utils/request'

//引入请求和响应的类型规则
import type { GetUserInfoResponse,LoginResponse } from './types'


//API枚举
enum API {

    //用户接口
    USERLIST_URL = '/user/user-view',
    USERLOGIN_URL = '/user/login',


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
