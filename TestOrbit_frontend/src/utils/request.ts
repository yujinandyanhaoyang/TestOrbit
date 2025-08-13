//二次封装axios
//目的：简化请求，统一处理错误，添加请求拦截器和响应拦截器
import axios from 'axios'
import type { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios'


// 创建axios实例
const request: AxiosInstance = axios.create({
    baseURL: '/api', // 使用代理路径
    timeout: 5000, //请求超时时间
})

// 请求拦截器
request.interceptors.request.use((config: InternalAxiosRequestConfig) => {
    // 在请求发送之前做一些处理
    // console.log(config)
    return config
})

// 响应拦截器
request.interceptors.response.use(
    (response: AxiosResponse) => {
        // 在响应数据到达then之前做一些处理
        // console.log(response)
        return response.data
    },
    (error) => {
        // 统一处理错误
        console.log(error)
        return Promise.reject(error)
    }
)

export default request
