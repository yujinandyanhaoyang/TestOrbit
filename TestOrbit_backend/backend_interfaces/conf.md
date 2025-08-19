# Configuration Module API Documentation

## Overview
The Configuration (Conf) module provides essential APIs for managing system-wide configurations, including environment settings and parameter types. This module is fundamental to the system's operation as it controls environment-specific behaviors and parameter handling across the platform.

## Base URL
All API endpoints are prefixed with `/conf/`

## API Endpoints

### 1. Environment Management

#### Environment CRUD Operations
**Endpoint**: `/envir-view`
**Handler**: `EnvirView.as_view()`

**Supported Methods**:
- **GET**
  - Description: Retrieve list of environments
  - Response: List of environment configurations ordered by position
  - Parameters: None

- **POST**
  - Description: Create new environment
  - Required Fields:
    - `name`: Environment name (unique)
  - Auto-handled:
    - `position`: Automatically set to max_position + 1
  - Response:
    - Success: `{"msg": "Creation successful"}`
    - Error: `{"msg": "Environment name already exists"}` (400)

- **PUT/PATCH**
  - Description: Update environment settings
  - Parameters:
    - `id`: Environment ID
    - `name`: New environment name (optional)
    - `position`: New position (optional)

- **DELETE**
  - Description: Remove environment
  - Validation:
    - Prevents deletion if it's the last environment
    - Response: `{"msg": "Must keep at least one environment!"}` (400)

#### Environment Position Management
**Endpoint**: `/change-envir-position`
**Handler**: `change_envir_position`
**Method**: POST

- Description: Reorder environments by updating their positions
- Parameters:
  - `id`: Environment ID to move
  - `position`: New position value
- Features:
  - Maintains sequential ordering
  - Updates affected environments' positions
  - Ensures data consistency

### 2. Parameter Type Management

#### Parameter Type Retrieval
**Endpoint**: `/param-type`
**Handler**: `get_param_type`
**Method**: GET

- Description: Retrieve available parameter types for API testing
- Response Format:
  ```json
  {
    "types": [
      {
        "id": "string",
        "name": "String Type",
        "position": 1
      },
      // ... other types
    ]
  }
  ```
- Features:
  - Cached results (@lru_cache)
  - Ordered by position
  - Used in API testing parameter validation

## Data Models

### 1. ConfEnvir
- Purpose: Stores environment configurations
- Fields:
  - `id`: SmallAutoField (PK)
  - `name`: CharField (unique)
  - `position`: SmallIntegerField
- Meta:
  - Table: conf_envir
  - Ordering: position ascending

### 2. ConfParamType
- Purpose: Defines available parameter types
- Fields:
  - `id`: CharField (PK, max_length=8)
  - `name`: CharField
  - `position`: SmallIntegerField
- Meta:
  - Table: conf_param_type
  - Ordering: position ascending

## Implementation Notes

1. **Environment Management**:
   - At least one environment must exist
   - Environment names must be unique
   - Position values are auto-managed
   - Changes are protected by transactions

2. **Parameter Types**:
   - Results are cached for performance
   - Types are ordered by position
   - Used across the system for parameter validation

3. **Security**:
   - All endpoints require authentication
   - Protected by Django REST framework permissions
   - Validation checks on all operations

## Common Response Format
```json
{
    "msg": "Operation result message",
    "data": {
        // Operation specific data
    }
}
```

## Error Responses
- 400: Bad Request (validation errors)
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

## Usage Context
- Environment configurations are used by:
  - API Test Cases
  - Project Settings
  - User Preferences
- Parameter types are used in:
  - API Testing
  - Variable Management
  - Data Validation
