//用户相关接口
//引入二次封装的请求方法
import request from '@/utils/request'

//引入请求和响应的类型规则
import type { GetUserInfoResponse } from './types'

//API枚举
enum API {
    USERLIST_URL = '/user/user-view'
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

