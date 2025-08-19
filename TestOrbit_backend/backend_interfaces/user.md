# User Module API Documentation

## 1. Overview

### 1.1 Base URL
Base path: `/user/`

### 1.2 Authentication
All endpoints except `/login` require Token authentication:
```http
Authorization: Token <token_key>
```

### 1.3 Common Response Format
```json
{
    "msg": "Operation message",
    "data": {
        // Response payload (optional)
    }
}
```

### 1.4 Error Response Format
```json
{
    "msg": "Error description"
}
```

## 2. API Endpoints

### 2.1 Authentication

#### Login
```http
POST /user/login
```

**Request Body**:
```json
{
    "username": "string",
    "password": "string"
}
```

**Success Response** (200):
```json
{
    "msg": "登录成功！",
    "token": "token_string",
    "user_info": {
        "username": "string",
        "name": "string"
    }
}
```

**Error Response** (403):
```json
{
    "msg": "密码错误或该账号被禁用！"
}
```

#### Change Password
```http
POST /user/change-password
```

**Request Body**:
```json
{
    "password": "string"  // New password
}
```

**Success Response** (200):
```json
{
    "msg": "修改成功"
}
```

### 2.2 User Management

#### Get/Update User Information
```http
GET/POST/PATCH /user/user-view
```

**GET Query Parameters**:
- `is_active` (optional): Filter by user status

**GET Response** (200):
```json
{
    "data": [{
        "id": "integer",
        "username": "string",
        "real_name": "string",
        "is_active": "boolean",
        "date_joined": "datetime"
    }]
}
```

**POST Request Body**:
```json
{
    "username": "string",
    "real_name": "string",
    "password": "string",     // Optional, defaults to "123456"
    "is_active": "boolean"
}
```

**PATCH Request Body**:
```json
{
    "id": "integer",
    "username": "string",     // Optional
    "real_name": "string",    // Optional
    "is_active": "boolean"    // Optional
}
```

**Special Rules**:
- Cannot modify admin username
- Cannot disable admin account
- Cannot delete any user account

### 2.3 User Configuration

#### Get User Configuration and Parameters
```http
GET /user/user-cfg-params
```

**Success Response** (200):
```json
{
    "data": {
        "user": "integer",
        "envir": "integer",
        "failed_stop": "boolean",
        "only_failed_log": "boolean",
        "exec_status": "integer",
        "params": {
            "3": [],  // VAR_PARAM
            "4": [],  // HEADER_PARAM
            "6": []   // HOST_PARAM
        }
    }
}
```

#### Set User Configuration
```http
POST /user/set-user-cfg
```

**Request Body**:
```json
{
    "envir": "integer",
    "failed_stop": "boolean",
    "only_failed_log": "boolean",
    "exec_status": "integer"
}
```

**Success Response** (200):
```json
{
    "msg": "修改成功！"
}
```

#### Clear User Temporary Parameters
```http
DELETE /user/clear-user-temp-params
```

**Success Response** (200):
```json
{
    "msg": "清除成功！"
}
```

## 3. Data Models

### 3.1 User Model (LimUser)
```json
{
    "id": "integer",
    "username": "string",
    "real_name": "string",
    "is_active": "boolean",
    "date_joined": "datetime",
    "password": "string"      // Hashed, write-only
}
```

### 3.2 User Configuration (UserCfg)
```json
{
    "user": "integer",        // OneToOne with LimUser
    "envir": "integer",       // ForeignKey to ConfEnvir
    "failed_stop": "boolean", // Stop on failure flag
    "only_failed_log": "boolean",
    "exec_status": "integer"  // Default: WAITING
}
```

### 3.3 Temporary Parameters (UserTempParams)
```json
{
    "id": "integer",
    "user": "integer",
    "name": "string",
    "value": "json",
    "case": "integer",        // Optional, ForeignKey to ApiCase
    "step_name": "string",
    "type": "integer",        // 3:VAR_PARAM, 4:HEADER_PARAM, 6:HOST_PARAM
    "param_type": "string"    // ForeignKey to ConfParamType
}
```

## 4. Implementation Notes

### 4.1 Authentication Flow
1. User submits credentials
2. System validates credentials
3. On success, generates/returns token
4. Token required for all subsequent requests

### 4.2 Password Management
- New users default password: "123456"
- Passwords are hashed using Django's make_password
- Password changes invalidate existing sessions

### 4.3 User Configuration
- Each user has one configuration record
- Configuration is created automatically
- Temporary parameters are session-specific
- Parameters are categorized by type (VAR, HEADER, HOST)

### 4.4 Security Considerations
- Token-based authentication
- Password hashing
- Special protection for admin account
- No physical user deletion

## 2. API Endpoints

### 2.1 Authentication

#### Login
```http
POST /user/login
```

**Request Body**:
```json
{
    "username": "string",
    "password": "string"
}
```

**Success Response** (200):
```json
{
    "code": 200,
    "msg": "Login successful",
    "data": {
        "token": "jwt_token_string",
        "user": {
            "id": 1,
            "username": "string",
            "real_name": "string",
            "is_active": true,
            "date_joined": "2025-08-13T10:00:00Z"
        }
    }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid credentials
- `401 Unauthorized`: Account disabled
- `429 Too Many Requests`: Too many login attempts

#### Change Password
```http
POST /user/change-password
```

**Request Body**:
```json
{
    "old_password": "string",
    "new_password": "string",
    "confirm_password": "string"
}
```

**Success Response** (200):
```json
{
    "code": 200,
    "msg": "Password updated successfully",
    "data": null
}
```

**Error Responses**:
- `400 Bad Request`: Passwords don't match or invalid format
- `401 Unauthorized`: Invalid old password

### 2.2 User Management

#### Get User Information
```http
GET /user/user-view
```

**Query Parameters**:
- `is_active` (optional): Filter by user status

**Success Response** (200):
```json
{
    "code": 200,
    "msg": "Success",
    "data": {
        "id": 1,
        "username": "string",
        "real_name": "string",
        "is_active": true,
        "date_joined": "2025-08-13T10:00:00Z",
        "last_login": "2025-08-13T10:00:00Z"
    }
}
```

#### Update User Information
```http
PATCH /user/user-view
```

**Request Body**:
```json
{
    "real_name": "string",    // Optional
    "is_active": boolean      // Optional, superuser only
}
```

**Success Response** (200):
```json
{
    "code": 200,
    "msg": "User updated successfully",
    "data": {
        // Updated user object
    }
}
```

### 2.3 User Configuration

#### Get User Configuration
```http
GET /user/user-cfg-params
```

**Query Parameters**:
- `param_name` (optional): Filter specific parameter

**Success Response** (200):
```json
{
    "code": 200,
    "msg": "Success",
    "data": {
        "envir": 1,
        "failed_stop": true,
        "only_failed_log": false,
        "exec_status": 0
    }
}
```

#### Set User Configuration
```http
POST /user/set-user-cfg
```

**Request Body**:
```json
{
    "envir": 1,              // Environment ID
    "failed_stop": true,     // Stop on failure flag
    "only_failed_log": false // Log only failures flag
}
```

**Success Response** (200):
```json
{
    "code": 200,
    "msg": "Configuration updated",
    "data": {
        // Updated configuration object
    }
}
```

#### Clear Temporary Parameters
```http
POST /user/clear-user-temp-params
```

**Success Response** (200):
```json
{
    "code": 200,
    "msg": "Temporary parameters cleared",
    "data": null
}
```

## 3. Models

### 3.1 User Model
```json
{
    "id": "integer",
    "username": "string",
    "real_name": "string",
    "is_active": "boolean",
    "date_joined": "datetime",
    "last_login": "datetime"
}
```

### 3.2 UserConfig Model
```json
{
    "user": "integer",       // Reference to User
    "envir": "integer",      // Reference to Environment
    "failed_stop": "boolean",
    "only_failed_log": "boolean",
    "exec_status": "integer" // 0: Waiting, 1: Running, etc.
}
```

## 4. Error Codes

| Code | Description                  | Solution                                    |
|------|------------------------------|---------------------------------------------|
| 400  | Bad Request                 | Check request parameters                    |
| 401  | Unauthorized                | Verify credentials or refresh token         |
| 403  | Forbidden                   | Check user permissions                      |
| 404  | Not Found                   | Verify resource exists                      |
| 429  | Too Many Requests           | Implement rate limiting                     |
| 500  | Internal Server Error       | Contact system administrator               |

## 5. Implementation Notes

### 5.1 Authentication
- JWT tokens expire after 24 hours
- Refresh tokens available through separate endpoint
- Rate limiting: 5 requests/minute for login attempts

### 5.2 Security Considerations
- Passwords must meet complexity requirements:
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one number
  - At least one special character
- User sessions are invalidated on password change
- Failed login attempts are logged and monitored

### 5.3 Configuration Management
- Environment-specific settings are cached
- Temporary parameters are cleared on session end
- Configuration changes trigger real-time updates

## 6. Testing Guidelines

### 6.1 Postman Collections
Available test collections:
- Authentication Flow Tests
- User Management Tests
- Configuration Management Tests

### 6.2 Environment Setup
```json
{
    "base_url": "http://localhost:8000",
    "token": "",
    "test_username": "test_user",
    "test_password": "test_password"
}
```

### 6.3 Test Scenarios
1. Authentication Flow
2. User Management Operations
3. Configuration Updates
4. Error Handling
5. Rate Limiting
6. Permission Controls
