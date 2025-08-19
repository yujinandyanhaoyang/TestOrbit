# TestOrbit Platform Extension Technical Design Document

## 1. Overview

### 1.1 Purpose
This document outlines the technical design for extending the TestOrbit platform with new features focusing on concurrent execution, variable management, test scheduling, and organizational management capabilities.

### 1.2 Scope
The extension encompasses seven major feature areas that will enhance the platform's testing capabilities and multi-tenant support.

### 1.3 System Context
Building upon the existing Django-based REST API platform with its current test case management and execution framework.

## 2. Technical Architecture

### 2.1 Concurrent Test Execution System

#### Design Overview
- Implementation of asynchronous test execution engine
- Parallel processing of test scenarios while maintaining data isolation

#### Key Components
```python
class TestExecutionManager:
    def __init__(self):
        self.execution_pool = ThreadPoolExecutor(max_workers=config.MAX_CONCURRENT_TESTS)
        self.scenario_queues = {}
        
    async def execute_scenario(self, scenario_id: int, test_cases: List[TestCase]):
        # Implementation for concurrent scenario execution
```

#### Database Schema Extensions
```sql
CREATE TABLE test_scenario_execution (
    id SERIAL PRIMARY KEY,
    scenario_id INTEGER REFERENCES api_case(id),
    status VARCHAR(20),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    concurrent_group_id UUID
);
```

### 2.2 Variable Priority Management

#### Architecture
- Hierarchical variable resolution system
- Scope-based variable inheritance

#### Implementation Details
```python
class VariableScope:
    GLOBAL = 'global'
    BUSINESS_UNIT = 'business_unit'
    PROJECT = 'project'
    SCENARIO = 'scenario'
    TEST_CASE = 'test_case'

class VariableResolver:
    def resolve_variable(self, var_name: str, context: ExecutionContext) -> Any:
        # Implementation for variable resolution with priority
```

#### Database Changes
```sql
CREATE TABLE variable_definition (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    value JSONB,
    scope VARCHAR(20),
    scope_id INTEGER,
    priority INTEGER,
    UNIQUE(name, scope, scope_id)
);
```

### 2.3 Enhanced Parameter Extraction

#### Supported Extractors
1. JSON Path Extractor
2. Regular Expression Extractor
3. XPath Extractor
4. Header Extractor
5. Cookie Extractor

#### Implementation
```python
class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, response: Response) -> Dict[str, Any]: pass

class JsonPathExtractor(BaseExtractor):
    def extract(self, response: Response) -> Dict[str, Any]:
        # Implementation for JSON extraction

class RegexExtractor(BaseExtractor):
    def extract(self, response: Response) -> Dict[str, Any]:
        # Implementation for regex extraction
```

### 2.4 Test Plan Scheduling System

#### Architecture Components
- Schedule Manager
- Task Queue
- Execution Tracker

#### Implementation
```python
class TestScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        
    def schedule_test(self, test_plan: TestPlan, schedule: ScheduleConfig):
        # Implementation for test scheduling
```

#### Database Schema
```sql
CREATE TABLE test_schedule (
    id SERIAL PRIMARY KEY,
    test_plan_id INTEGER REFERENCES api_case(id),
    schedule_type VARCHAR(20),
    cron_expression VARCHAR(100),
    next_run TIMESTAMP,
    last_run TIMESTAMP,
    status VARCHAR(20)
);
```

### 2.5 Business Unit Management

#### Data Model
```sql
CREATE TABLE business_unit (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE business_unit_member (
    id SERIAL PRIMARY KEY,
    business_unit_id INTEGER REFERENCES business_unit(id),
    user_id INTEGER REFERENCES auth_user(id),
    role VARCHAR(50),
    UNIQUE(business_unit_id, user_id)
);
```

#### API Endpoints
```python
@api_view(['POST'])
def create_business_unit(request):
    # Implementation for business unit creation

class BusinessUnitViewSet(viewsets.ModelViewSet):
    serializer_class = BusinessUnitSerializer
    permission_classes = [IsAuthenticated, BusinessUnitPermission]
```

### 2.6 Access Control System

#### Permission Hierarchy
1. System-level Permissions
2. Business Unit Permissions
3. Project Permissions
4. Resource-level Permissions

#### Implementation
```python
class BusinessUnitPermission(BasePermission):
    def has_permission(self, request, view):
        # Implementation for business unit permission check

class ProjectAccessMiddleware:
    def process_request(self, request):
        # Implementation for project access control
```

#### Database Schema
```sql
CREATE TABLE permission_assignment (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES auth_user(id),
    permission_type VARCHAR(50),
    resource_type VARCHAR(50),
    resource_id INTEGER,
    granted_by INTEGER REFERENCES auth_user(id),
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 3. API Changes

### 3.1 New Endpoints

#### Test Execution
```
POST /api/v1/test/scenario/execute
POST /api/v1/test/scenario/status
GET  /api/v1/test/scenario/results
```

#### Variable Management
```
POST /api/v1/variables
GET  /api/v1/variables/{scope}/{id}
PUT  /api/v1/variables/{id}
```

#### Schedule Management
```
POST /api/v1/schedules
GET  /api/v1/schedules
PUT  /api/v1/schedules/{id}
DELETE /api/v1/schedules/{id}
```

#### Business Unit Management
```
POST /api/v1/business-units
GET  /api/v1/business-units
PUT  /api/v1/business-units/{id}
POST /api/v1/business-units/{id}/members
```

## 4. Security Considerations

### 4.1 Authentication
- JWT-based authentication
- Token refresh mechanism
- Session management for concurrent access

### 4.2 Authorization
- Role-based access control (RBAC)
- Business unit isolation
- Resource-level permissions

### 4.3 Data Security
- Variable encryption for sensitive data
- Audit logging for all operations
- Data isolation between business units

## 5. Performance Considerations

### 5.1 Concurrent Execution
- Connection pooling for database access
- Rate limiting for API requests
- Resource allocation for parallel test execution

### 5.2 Caching Strategy
- Redis-based caching for:
  - Variable resolution
  - User permissions
  - Execution results

### 5.3 Database Optimization
- Indexed queries for frequent operations
- Partitioning for execution history
- Archival strategy for old test results

## 6. Migration Plan

### 6.1 Database Migration
1. Create new tables
2. Add foreign key relationships
3. Migrate existing data
4. Add indexes and constraints

### 6.2 Code Deployment
1. Deploy database changes
2. Deploy new API endpoints
3. Deploy background workers
4. Update frontend applications

### 6.3 Testing Strategy
1. Unit tests for new components
2. Integration tests for workflows
3. Performance testing for concurrent execution
4. Security testing for access control

## 7. Monitoring and Logging

### 7.1 Metrics
- Test execution metrics
- API performance metrics
- Resource utilization metrics
- Business unit usage statistics

### 7.2 Logging
- Structured logging format
- Log aggregation system
- Alert mechanisms for failures

## 8. Future Considerations

### 8.1 Scalability
- Horizontal scaling of test executors
- Distributed test execution
- Multi-region support

### 8.2 Integration
- CI/CD pipeline integration
- Third-party tool integration
- API gateway integration
  
