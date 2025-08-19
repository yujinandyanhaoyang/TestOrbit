# TestOrbit - API Testing Platform Documentation

## Core Functionalities

1. **Project Management**
   - Project creation and configuration
   - Project-specific environment settings
   - Project overview and statistics
   - Database configuration per project
   - SQL execution capabilities
   - Environment-specific configuration management

2. **API Management**
   - API definition and documentation
   - Support for multiple HTTP methods
   - API module organization with tree structure
   - Default parameter configuration
   - API source tracking (User API vs System API)
   - API search and filtering capabilities
   - Request timeout configuration
   - Unique API path validation per project

3. **Test Case Management**
   - Hierarchical module organization
   - Test case CRUD operations
   - Test step configuration
   - Support for various step types:
     - API calls
     - Case references (reusability)
     - SQL execution
     - Header manipulation
     - Variable operations
     - Host configuration
   - Step execution control (enable/disable)
   - Test case copying and merging
   - Logical deletion with recovery option
   - Position-based ordering

4. **Advanced Test Flow Control**
   - Foreach loop implementation for steps
   - Nested test case references
   - Step retry configuration
   - Execution flow control (continue/stop on failure)
   - Step execution status tracking
   - Interrupt handling for test execution

5. **Variables and Parameters**
   - Global variable management
   - Environment-specific variables
   - Dynamic parameter configuration
   - Parameter type management
   - Temporary parameter storage
   - JSON parameter support
   - Form data support

6. **Test Execution**
   - Single test case execution
   - Batch test execution
   - Real-time execution status
   - Execution history tracking
   - Latest run time recording
   - Execution interruption support
   - Step-by-step execution capability

7. **Test Results and Reporting**
   - Detailed test execution results
   - Statistical analysis
   - JSON-formatted test reports
   - Execution status tracking
   - Success/Failure statistics
   - Step-level result recording

8. **User Management**
   - User authentication
   - User configuration management
   - Password management
   - User-specific settings:
     - Default environment
     - Failure handling preferences
     - Execution status tracking
     - Log preferences

9. **Module Organization**
   - Tree-structured module management
   - Module relationship tracking
   - Parent-child hierarchy
   - Module position management
   - Default module handling

10. **Security and Access Control**
    - User authentication
    - Protected operations
    - Delete protection for referenced cases
    - Data integrity checks
    - Environment isolation

## Technical Features

- Built on Django and Django REST framework
- JSON-based data storage
- Transaction support for data integrity
- Bulk operations for performance
- Flexible filtering and ordering
- Customizable serialization
- Exception handling and error reporting