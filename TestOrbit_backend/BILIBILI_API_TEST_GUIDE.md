# Bilibili API 测试步骤配置指南

## 目标API
```
https://api.bilibili.com/x/web-interface/wbi/search/square?limit=10&platform=web&web_location=333.1007&w_rid=34fb4890fde4ba690fec027923f4e903&wts=1754988669
```

## Postman 配置

### 1. 基本信息
- **Method**: POST
- **URL**: `http://127.0.0.1:8000/api-data/api-view`
- **Headers**: 
  ```
  Content-Type: application/json
  Authorization: Token 93999f4de91dc92a3f7daf476a8445d39bc4703b
  ```

### 2. 请求体 (JSON)

#### 方案A: 完整参数配置（推荐）
```json
{
  "case_id": 12,
  "env_id": 1,
  "steps": [
    {
      "step_name": "测试B站搜索广场API",
      "step_order": 3,
      "type": "api",
      "enabled": true,
      "results": null,
      "params": {
        "path": "/x/web-interface/wbi/search/square",
        "method": "GET",
        "host": "https://api.bilibili.com",
        "timeout": 30,
        "query_mode": "table",
        "query_source": [
          {
            "name": "limit",
            "value": "10",
            "type": {"type": "string"}
          },
          {
            "name": "platform", 
            "value": "web",
            "type": {"type": "string"}
          },
          {
            "name": "web_location",
            "value": "333.1007", 
            "type": {"type": "string"}
          },
          {
            "name": "w_rid",
            "value": "34fb4890fde4ba690fec027923f4e903",
            "type": {"type": "string"}
          },
          {
            "name": "wts",
            "value": "1754988669",
            "type": {"type": "string"}
          }
        ],
        "header_mode": "table",
        "header_source": [
          {
            "name": "User-Agent",
            "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "type": {"type": "string"}
          },
          {
            "name": "Referer",
            "value": "https://www.bilibili.com/",
            "type": {"type": "string"}
          }
        ],
        "body_mode": "raw",
        "body_source": {},
        "output_mode": "table",
        "output_source": [
          {
            "name": "response_code",
            "value": "code",
            "type": {"type": "number"}
          },
          {
            "name": "response_message", 
            "value": "message",
            "type": {"type": "string"}
          }
        ],
        "expect_mode": "table",
        "expect_source": [
          {
            "name": "code",
            "value": "0",
            "rule": "equal",
            "type": {"type": "number"}
          }
        ]
      }
    }
  ]
}
```

#### 方案B: 简化配置
```json
{
  "case_id": 12,
  "env_id": 1, 
  "steps": [
    {
      "step_name": "B站搜索广场API",
      "step_order": 3,
      "type": "api",
      "enabled": true,
      "results": null,
      "params": {
        "path": "/x/web-interface/wbi/search/square?limit=10&platform=web&web_location=333.1007&w_rid=34fb4890fde4ba690fec027923f4e903&wts=1754988669",
        "method": "GET", 
        "host": "https://api.bilibili.com",
        "timeout": 30,
        "query_mode": "raw",
        "header_mode": "raw",
        "body_mode": "raw"
      }
    }
  ]
}
```

## 参数说明

### 核心字段
- **case_id**: 用例组ID（已存在的用例组）
- **env_id**: 环境ID
- **steps**: 步骤数组（可包含多个步骤）

### 步骤字段
- **step_name**: 步骤名称
- **step_order**: 步骤顺序
- **type**: 步骤类型（"api" 表示API请求）
- **enabled**: 是否启用
- **params**: 参数配置

### params详细配置

#### API基本信息
- **host**: API主机地址
- **path**: API路径（包含查询参数）
- **method**: HTTP方法
- **timeout**: 超时时间（秒）

#### 参数模式
- **query_mode**: 查询参数模式
  - `"table"`: 表格模式，使用query_source数组
  - `"raw"`: 原始模式，参数直接写在path中
  
- **header_mode**: 请求头模式
  - `"table"`: 表格模式，使用header_source数组  
  - `"raw"`: 原始模式，使用默认请求头
  
- **body_mode**: 请求体模式
  - `"raw"`: 原始模式
  - `"table"`: 表格模式
  - `"json"`: JSON模式

#### 参数源配置（table模式）
```json
"query_source": [
  {
    "name": "参数名",
    "value": "参数值", 
    "type": {"type": "string|number|boolean"}
  }
]
```

#### 输出参数（可选）
```json
"output_source": [
  {
    "name": "变量名",
    "value": "响应字段路径",
    "type": {"type": "string"}
  }
]
```

#### 断言验证（可选）
```json
"expect_source": [
  {
    "name": "响应字段路径",
    "value": "期望值",
    "rule": "equal|not_equal|contain|not_contain",
    "type": {"type": "string|number"}
  }
]
```

## 测试步骤

1. **打开Postman**
2. **创建新请求**
3. **设置Method为POST**
4. **输入URL**: `http://127.0.0.1:8000/api-data/api-view`
5. **添加Headers**:
   - `Content-Type: application/json`
   - `Authorization: Token 93999f4de91dc92a3f7daf476a8445d39bc4703b`
6. **在Body中选择raw和JSON格式**
7. **粘贴上面的JSON配置**
8. **点击Send发送请求**

## 预期结果

成功响应示例：
```json
{
  "msg": "步骤创建成功！(步骤 ID: 22)",
  "data": {
    "step_id": 22
  }
}
```

## 注意事项

1. **case_id必须存在**: 确保case_id=12的用例组已存在
2. **step_order唯一**: 确保step_order在该用例组中不重复
3. **Token有效**: 确保Authorization Token有效
4. **URL格式**: B站API的参数顺序和签名很重要
5. **请求头**: B站API可能需要特定的User-Agent和Referer

## 高级配置

如果需要更复杂的测试，可以添加：
- **重试机制**: 在controller_data中配置
- **条件执行**: 使用execute_on字段
- **变量提取**: 配置output_source提取响应数据
- **断言验证**: 配置expect_source验证响应

建议先使用方案B的简化配置进行测试，成功后再根据需要使用方案A的完整配置。
