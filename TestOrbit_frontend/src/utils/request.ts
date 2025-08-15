//二次封装axios
//目的：简化请求，统一处理错误，添加请求拦截器和响应拦截器
import axios from 'axios'
import type { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import router from '@/router'
import { ElMessage } from 'element-plus'


// 创建axios实例
const request: AxiosInstance = axios.create({
    baseURL: '/api', // 使用代理路径
    timeout: 5000, //请求超时时间
})

// 请求拦截器
request.interceptors.request.use((config: InternalAxiosRequestConfig) => {
    // 在请求发送之前添加token
    const token = localStorage.getItem('token')
    
    // 如果有token就添加到请求头中
    if (token) {
        // 添加Authorization头，格式为 'Bearer ' + token 或直接使用token，取决于后端要求
        config.headers.Authorization = `Token ${token}`
        // console.log(config)
    }
    
    return config
})

// 使用上面导入的router和ElMessage

// 响应拦截器
request.interceptors.response.use(
    (response: AxiosResponse) => {
        // 在响应数据到达then之前做一些处理
        const data = response.data
        
        // 可以在这里统一处理某些业务逻辑的错误
        // 例如，如果后端返回的code不是200，可以在这里统一处理
        // 当前已经在各个API调用处处理，这里只是提供一个示例
        
        return data
    },
    (error) => {
        // 统一处理HTTP错误
        const { status } = error.response || {}
        
        // 处理常见的HTTP状态码
        switch (status) {
            case 401: // 未授权
                ElMessage.error('登录已过期，请重新登录')
                // 清除token并重定向到登录页
                localStorage.removeItem('token')
                localStorage.removeItem('userInfo')
                router.push('/login')
                break
            case 403: // 禁止访问
                ElMessage.error('您没有权限访问此资源')
                break
            case 404: // 资源不存在
                ElMessage.error('请求的资源不存在')
                break
            case 500: // 服务器错误
                ElMessage.error('服务器错误，请稍后再试')
                break
            default:
                ElMessage.error(error.message || '请求失败，请稍后再试')
        }
        
        return Promise.reject(error)
    }
)

export default request
