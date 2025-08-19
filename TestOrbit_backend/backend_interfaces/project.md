# Project Module API Documentation

## Overview
The Project module serves as the cornerstone of the API testing platform, managing project configurations, environment settings, and database connections. It provides comprehensive APIs for project lifecycle management, environment configuration, and database operations.

## Base URL
All API endpoints are prefixed with `/project/`

## API Categories

### 1. Project Management

#### Core Project Operations
**Endpoint**: `/project-view`
**Handler**: `ProjectView.as_view()`

**Supported Methods**:
- **GET**
  - Description: Retrieve project list or details
  - Parameters:
    - `id` (optional): Get specific project details
  - Response: List of projects or detailed project information
  - Features:
    - Pagination support
    - Sorting options
    - Filtering capabilities

- **POST**
  - Description: Create new project
  - Required Fields:
    - `name`: Project name (unique)
    - `remark` (optional): Project description
  - Auto-created:
    - Default API module
    - Environment configurations
  - Response:
    - Success: `{"msg": "Creation successful", "id": project_id}`
    - Error: `{"msg": "Project name already exists"}` (400)

- **PUT/PATCH**
  - Description: Update project settings
  - Updateable Fields:
    - `name`: Project name
    - `remark`: Project description
  - Validation:
    - Name uniqueness check
    - Reference integrity

- **DELETE**
  - Description: Remove project
  - Validation:
    - Checks for dependent resources
    - Cascading deletion of related data

### 2. Project Overview and Statistics

#### Project Overview
**Endpoint**: `/project-overview`
**Method**: GET
**Handler**: `project_overview`

- Description: Provides statistical overview of project resources
- Parameters:
  - `type`: Resource type to analyze (e.g., 'API')
- Response Format:
  ```json
  {
    "total_count": 100,
    "data": [
      {
        "id": 1,
        "name": "Project Name",
        "count": 25  // Resource count
      }
    ]
  }
  ```

#### Dashboard Statistics
**Endpoint**: `/get-index-statistics`
**Method**: GET
**Handler**: `get_index_statistics`

- Description: Retrieves dashboard statistics
- Returns:
  - Project counts
  - API statistics
  - Recent activities
  - User engagement metrics

### 3. Environment Configuration

#### Environment Data Management
**Endpoint**: `/project-envir-data`
**Method**: GET
**Handler**: `get_project_envir_data`

- Description: Manages project-specific environment configurations
- Features:
  - Environment variables
  - Configuration settings
  - Environment-specific parameters

#### Environment Status
**Endpoint**: `/project-have-envir`
**Method**: GET
**Handler**: `get_project_have_envir`

- Description: Lists environments configured for a project
- Response: List of active environments and their statuses

### 4. Database Operations

#### Connection Testing
**Endpoint**: `/test-db-connect`
**Method**: POST
**Handler**: `test_db_connect`

- Description: Validates database connection settings
- Parameters:
  - Connection string or components
  - Authentication details
- Response:
  - Connection status
  - Error details if failed

#### Database Management
**Endpoint**: `/proj-db-database`
**Method**: GET
**Handler**: `get_proj_db_database`

- Description: Retrieves database information
- Features:
  - Database listings
  - Table information
  - Connection details

#### SQL Execution
**Endpoint**: `/run-sql`
**Method**: POST
**Handler**: `run_sql`

- Description: Executes SQL queries within project context
- Features:
  - Query execution
  - Transaction support
  - Results formatting
  - Error handling
- Security:
  - Query validation
  - Permission checks
  - Connection pooling

## Data Models

### 1. Project
- Fields:
  - `id`: SmallAutoField (PK)
  - `name`: CharField (unique)
  - `remark`: TextField (optional)
- Meta:
  - Table: project
  - Unique constraints on name

### 2. ProjectEnvirData
- Fields:
  - `id`: SmallAutoField (PK)
  - `envir`: ForeignKey(ConfEnvir)
  - `project`: ForeignKey(Project)
  - `data`: JSONField
- Meta:
  - Table: project_envir_data
  - Unique together: (envir, project)

## Implementation Notes

1. **Project Creation**:
   - Automatic default module creation
   - Environment configuration initialization
   - Transaction-protected operations

2. **Environment Management**:
   - Multiple environment support
   - Environment-specific configurations
   - JSON-based configuration storage

3. **Database Operations**:
   - Connection pooling
   - Transaction management
   - Query sanitization
   - Error handling

4. **Security Considerations**:
   - Authentication required
   - Permission-based access control
   - SQL injection prevention
   - Data validation

## Common Response Format
```json
{
    "msg": "Operation status message",
    "data": {
        // Operation specific data
    }
}
```

## Error Handling
- 400: Bad Request
  - Validation errors
  - Duplicate names
  - Invalid configurations
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error
  - Database connection issues
  - Configuration errors
  - SQL execution failures

## Integration Points
- **API Module**: Project context for API definitions
- **User Module**: Project access control
- **Configuration Module**: Environment settings
- **Database Module**: SQL operations and connections
