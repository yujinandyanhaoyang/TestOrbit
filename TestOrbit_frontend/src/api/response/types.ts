/**
 * 通用API响应接口定义
 * 封装后端API返回的标准数据结构
 */

// 基础响应接口
export interface BaseResponse {
  code: number;     // 状态码
  msg: string;      // 消息
  success: boolean; // 是否成功
}

// 带数据的响应接口（泛型）
export interface DataResponse<T> extends BaseResponse {
  results: T;       // 响应数据，类型由泛型参数决定
}

// 分页数据响应接口
export interface PageResponse<T> extends BaseResponse {
  results: {
    count: number;  // 总条数
    items: T[];     // 分页项目列表
    page: number;   // 当前页码
    size: number;   // 每页条数
  };
}

// 列表响应接口（不分页）
export interface ListResponse<T> extends BaseResponse {
  results: T[];     // 列表数据
}

// 空响应接口（用于不需要返回数据的操作）
export interface EmptyResponse extends BaseResponse {
  results: null;
}
