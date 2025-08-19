# ApiData Module API Documentation

## Overview
The ApiData module provides comprehensive REST APIs for managing API test cases, test execution, and result reporting. The module is organized into several functional categories for better organization and usage.

## Base URL
All API endpoints are prefixed with `/apiData/`

## API Categories

### 1. Module Management APIs

#### Test Case Module Management
| Endpoint | Method | Description |
|----------|---------|-------------|
| `/tree-case-module` | GET | Retrieves the hierarchical tree structure of test case modules. Used for navigation and organization of test cases. |
| `/tree-cascader-module-case` | GET | Returns a cascading selection structure of modules and their test cases. Optimized for frontend dropdown components. |
| `/case-module-view` | GET/POST/PUT/DELETE | Complete CRUD operations for test case modules. Supports creation of hierarchical module structures with parent-child relationships. |

#### API Module Management
| Endpoint | Method | Description |
|----------|---------|-------------|
| `/tree-api-module` | GET | Retrieves the hierarchical tree structure of API modules. Used for organizing API definitions. |
| `/api-module-view` | GET/POST/PUT/DELETE | Complete CRUD operations for API modules. Manages the organizational structure of APIs. |

### 2. Test Case Management APIs

#### Core Case Operations
| Endpoint | Method | Description |
|----------|---------|-------------|
| `/case-view` | GET/POST/PUT/DELETE | Complete CRUD operations for API test cases. Supports:<br>- GET: List cases or get case details<br>- POST: Create new test case with steps<br>- PUT: Update existing test case<br>- DELETE: Logical deletion with reference check |
| `/delete-selected-cases` | POST | Batch deletion of multiple test cases. Performs reference checking before deletion. |
| `/clean-deleted-cases` | POST | Physically removes logically deleted test cases from the database. Use with caution. |

#### Case Organization
| Endpoint | Method | Description |
|----------|---------|-------------|
| `/case-sort-list` | GET | Retrieves a sorted list of test cases based on position field. |
| `/set-case-position` | POST | Updates the position/order of test cases within their module. |

#### Case Management Operations
| Endpoint | Method | Description |
|----------|---------|-------------|
| `/copy-cases` | POST | Creates copies of existing test cases, including all their steps and configurations. |
| `/merge-cases` | POST | Combines multiple test cases into a single case, preserving steps and logic. |
| `/copy-step-to-other-case` | POST | Copies specific steps from one test case to another. |

### 3. API Management APIs

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/api-view` | GET/POST/PUT/DELETE | Complete CRUD operations for API definitions. Features:<br>- Default parameter management<br>- Method and path validation<br>- Project-specific API organization |
| `/search-api` | GET | Searches APIs based on various criteria (name, path, method, etc.). |
| `/search-case-by-api` | GET | Finds test cases that use a specific API. Useful for impact analysis. |
| `/test-api-data` | POST | Validates API configuration by making a test request. Returns response data and validation results. |

### 4. Test Execution APIs

#### Execution Control
| Endpoint | Method | Description |
|----------|---------|-------------|
| `/run-api-cases` | POST | Executes multiple test cases in batch. Features:<br>- Parallel execution support<br>- Environment selection<br>- Execution parameter configuration |
| `/run-api-case-step` | POST | Executes a single step within a test case. Useful for debugging and step-by-step validation. |
| `/stop-casing` | POST | Interrupts ongoing test execution. Ensures clean termination of running tests. |

#### Results and Reporting
| Endpoint | Method | Description |
|----------|---------|-------------|
| `/api-report` | GET | Generates comprehensive test execution reports. Includes:<br>- Execution statistics<br>- Step-level results<br>- Failure analysis<br>- Duration metrics |

## Common Response Format
```json
{
    "msg": "Operation status message",
    "data": {
        // Response data specific to each endpoint
    },
    "status": 200  // HTTP status code
}
```

## Error Handling
- All endpoints perform validation and return appropriate HTTP status codes
- 400: Bad Request (validation errors)
- 401: Unauthorized
- 403: Forbidden
- 404: Resource not found
- 500: Internal server error

## Notes
1. All list endpoints support filtering, sorting, and pagination
2. Module-related operations maintain hierarchical integrity
3. Delete operations check for dependencies before execution
4. Test execution can be configured per user preferences
5. Batch operations are wrapped in transactions for data consistency
