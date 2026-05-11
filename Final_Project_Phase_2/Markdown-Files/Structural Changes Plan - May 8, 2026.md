# Structural Changes Plan - May 8, 2026

## Prompter: Nathan Martin

## Origin Prompt
Create a plan for structural changes. This plan should focus on improving organization, layering, maintainability, and separation of concerns. The plan should include separating the code into 3 layers: service, ui, and data. Each of these layers should have at least one python file. In each layer, create one class and define methods under the class for app functionality. All classes will be called into the main python file ("inv_manager.py"). Place the prompt in the correct order in the document created, under Origin Prompt. Save the plan version with today's date in case the plan goes through multiple rounds. Do NOT code anything, just create a plan in a logical order.

## Overview
This plan outlines a structured approach to refactor the monolithic `inv_manager.py` application into a three-layered architecture focusing on separation of concerns. The current application mixes UI, business logic, and data access in a single file. The proposed changes will separate the code into three distinct layers (Service, UI, and Data), with each layer containing at least one Python file with a class that encapsulates the layer's functionality. All layer classes will be integrated into the main `inv_manager.py` file, which will serve as the application orchestrator.

## Current Structural Issues
- **Monolithic Design**: All functionality is contained in a single file with over 600 lines
- **Mixed Responsibilities**: UI components, business logic, and data operations are tightly coupled
- **Poor Maintainability**: Changes in one area risk breaking unrelated functionality
- **Testing Difficulties**: Impossible to unit test individual components in isolation
- **Code Duplication**: Repeated patterns for data handling and UI rendering
- **Scalability Problems**: Adding new features requires modifying the entire file
- **Error Handling**: Inconsistent error management scattered throughout the code

## Proposed Three-Layer Architecture

### Layer Overview
The application will be restructured into three main layers:

1. **Data Layer**: Handles data persistence, retrieval, and basic data operations
2. **Service Layer**: Contains business logic, validation rules, and application workflows
3. **UI Layer**: Manages user interface components and user interactions

### Directory Structure
```
project_root/
├── inv_manager.py          # Main application orchestrator
├── data/
│   ├── __init__.py
│   └── data_manager.py     # DataManager class
├── service/
│   ├── __init__.py
│   └── business_service.py # BusinessService class
├── ui/
│   ├── __init__.py
│   └── ui_manager.py       # UIManager class
├── data/                   # Data files directory (renamed to avoid conflict)
│   ├── inventory.json
│   ├── orders.json
│   └── users.json
└── requirements.txt
```

### Layer Responsibilities

#### Data Layer (`data/data_manager.py`)
**DataManager Class**: Centralizes all data operations
- Methods for loading and saving JSON data
- Data validation and error handling
- CRUD operations for users, inventory, and orders
- Data backup and recovery functionality

#### Service Layer (`service/business_service.py`)
**BusinessService Class**: Implements core business logic
- User authentication and authorization methods
- Inventory management operations (restocking, assembly)
- Order processing and management workflows
- Business rule validation and calculations
- Data transformation between layers

#### UI Layer (`ui/ui_manager.py`)
**UIManager Class**: Handles all user interface operations
- Methods for rendering different pages and components
- User input handling and validation
- Session state management
- UI feedback and messaging
- Navigation between different views

### Main Application File (`inv_manager.py`)
The main file will be refactored to:
- Import and initialize the three layer classes
- Orchestrate interactions between layers
- Handle application startup and configuration
- Manage the main application loop and routing

## Implementation Plan

### Phase 1: Layer Setup and Data Layer (Week 1-2)
**Objective**: Create the basic layer structure and implement the Data layer

1. **Directory Structure Creation**
   - Create `data/`, `service/`, and `ui/` directories
   - Add `__init__.py` files to make directories Python packages
   - Move data files to a dedicated `data_files/` directory

2. **DataManager Class Design**
   - Define `DataManager` class in `data/data_manager.py`
   - Implement methods for JSON file operations:
     - `load_inventory()`, `save_inventory()`
     - `load_orders()`, `save_orders()`
     - `load_users()`, `save_users()`
   - Add data validation methods
   - Implement error handling for file operations

3. **Data Layer Integration**
   - Update `inv_manager.py` to import and initialize `DataManager`
   - Replace direct JSON operations with `DataManager` method calls
   - Test data loading and saving functionality

### Phase 2: Service Layer Implementation (Week 3-4)
**Objective**: Extract and implement business logic in the Service layer

1. **BusinessService Class Design**
   - Define `BusinessService` class in `service/business_service.py`
   - Implement authentication methods:
     - `authenticate_user(email, password)`
     - `register_user(user_data)`
   - Add inventory management methods:
     - `restock_item(item_name, quantity)`
     - `assemble_car(car_type, quantity)`
     - `check_assembly_requirements(car_type, quantity)`
   - Implement order management methods:
     - `place_order(order_data)`
     - `update_order_status(order_id, status)`
     - `delete_order(order_id)`

2. **Business Logic Extraction**
   - Move calculation logic (assembly requirements, pricing) to service methods
   - Implement business rule validation
   - Add error handling for business operations

3. **Service Layer Integration**
   - Update `inv_manager.py` to import and initialize `BusinessService`
   - Pass `DataManager` instance to `BusinessService` for data operations
   - Replace inline business logic with `BusinessService` method calls

### Phase 3: UI Layer Refactoring (Week 5-6)
**Objective**: Extract UI components into the UI layer

1. **UIManager Class Design**
   - Define `UIManager` class in `ui/ui_manager.py`
   - Implement page rendering methods:
     - `render_login_page()`
     - `render_manager_dashboard()`
     - `render_customer_dashboard()`
   - Add component methods:
     - `render_inventory_view()`
     - `render_order_form()`
     - `render_user_registration()`
   - Implement session management methods:
     - `initialize_session()`
     - `update_session_state(key, value)`
     - `clear_session()`

2. **UI Logic Extraction**
   - Move Streamlit UI code into `UIManager` methods
   - Implement callback methods for user interactions
   - Add input validation and error display methods

3. **UI Layer Integration**
   - Update `inv_manager.py` to import and initialize `UIManager`
   - Pass `BusinessService` and `DataManager` instances to `UIManager`
   - Restructure main application flow to use `UIManager` methods

### Phase 4: Integration and Testing (Week 7-8)
**Objective**: Integrate all layers and ensure functionality preservation

1. **Layer Integration**
   - Ensure proper communication between all three layers
   - Implement dependency injection pattern
   - Add configuration management for layer initialization

2. **Functionality Testing**
   - Test each layer independently
   - Verify end-to-end workflows across all layers
   - Ensure all original features work correctly

3. **Refinement and Optimization**
   - Optimize method calls and data flow between layers
   - Add logging and error handling
   - Clean up the main `inv_manager.py` file

### Phase 5: Documentation and Finalization (Week 9-10)
**Objective**: Document the new structure and prepare for maintenance

1. **Code Documentation**
   - Add docstrings to all classes and methods
   - Create method usage examples
   - Document layer interactions and responsibilities

2. **Architecture Documentation**
   - Update README with new architecture explanation
   - Create developer guide for working with the layered structure
   - Document testing procedures

3. **Final Validation**
   - Comprehensive functionality testing
   - Performance verification
   - Code review and cleanup

## Class Method Specifications

### DataManager Class Methods
- `load_inventory() -> list`: Load inventory data from JSON
- `save_inventory(inventory_data: list)`: Save inventory data to JSON
- `load_orders() -> list`: Load orders data from JSON
- `save_orders(orders_data: list)`: Save orders data to JSON
- `load_users() -> list`: Load users data from JSON
- `save_users(users_data: list)`: Save users data to JSON
- `validate_data(data: dict, data_type: str) -> bool`: Validate data structure
- `backup_data()`: Create backup of all data files

### BusinessService Class Methods
- `authenticate_user(email: str, password: str) -> dict`: Authenticate user credentials
- `register_user(user_data: dict)`: Register new user
- `restock_item(item_name: str, quantity: int)`: Restock inventory item
- `assemble_car(car_type: str, quantity: int) -> bool`: Assemble car if requirements met
- `check_assembly_requirements(car_type: str, quantity: int) -> dict`: Check if assembly possible
- `place_order(order_data: dict)`: Place new customer order
- `update_order_status(order_id: str, status: str)`: Update order status
- `delete_order(order_id: str)`: Delete order
- `calculate_order_total(item_name: str, quantity: int) -> float`: Calculate order total
- `validate_business_rules(operation: str, data: dict) -> bool`: Validate business rules

### UIManager Class Methods
- `initialize_app()`: Set up Streamlit page configuration
- `render_login_page() -> str`: Render login/registration page and return action
- `render_manager_dashboard(user: dict)`: Render manager dashboard
- `render_customer_dashboard(user: dict)`: Render customer dashboard
- `render_inventory_view(inventory: list)`: Render inventory display component
- `render_order_form() -> dict`: Render order placement form and return data
- `render_order_management(orders: list)`: Render order management interface
- `display_message(message: str, type: str)`: Display success/error messages
- `handle_user_input(component: str, data: dict)`: Process user input and trigger actions
- `manage_session(action: str, data: dict = None)`: Manage Streamlit session state

## Integration in Main File
The `inv_manager.py` file will be restructured to:

```python
# Import layer classes
from data.data_manager import DataManager
from service.business_service import BusinessService
from ui.ui_manager import UIManager

# Initialize layers
data_manager = DataManager()
business_service = BusinessService(data_manager)
ui_manager = UIManager(business_service, data_manager)

# Main application logic
def main():
    ui_manager.initialize_app()
    
    # Main application loop
    while True:
        if not ui_manager.is_logged_in():
            action = ui_manager.render_login_page()
            if action == "login":
                # Handle login through business_service
                pass
        else:
            # Render appropriate dashboard
            pass

if __name__ == "__main__":
    main()
```

## Benefits of the Three-Layer Structure

### Improved Organization
- **Clear Separation**: Each layer has distinct, well-defined responsibilities
- **Modular Design**: Changes in one layer don't affect others
- **Logical Grouping**: Related functionality is grouped together

### Enhanced Maintainability
- **Easier Debugging**: Issues can be isolated to specific layers
- **Simplified Updates**: Feature changes are localized
- **Code Reusability**: Layer methods can be reused across the application

### Better Testability
- **Unit Testing**: Each layer can be tested independently
- **Mocking**: Dependencies can be easily mocked for testing
- **Integration Testing**: Layer interactions can be tested separately

### Separation of Concerns
- **Data Layer**: Focuses solely on data persistence and retrieval
- **Service Layer**: Contains all business logic and rules
- **UI Layer**: Handles only user interface and presentation

## Migration Strategy

### Incremental Approach
1. **Create layer structure** without modifying existing code
2. **Implement Data layer** and gradually replace direct JSON operations
3. **Build Service layer** and move business logic incrementally
4. **Refactor UI layer** by extracting components one at a time
5. **Integrate layers** in the main file
6. **Test thoroughly** at each step

### Risk Mitigation
- **Backup Original**: Keep the original `inv_manager.py` as backup
- **Feature Flags**: Use conditional logic to switch between old and new implementations
- **Comprehensive Testing**: Test each migration step before proceeding
- **Rollback Plan**: Ability to revert changes if issues arise

## Success Metrics
- **Functionality Preservation**: All original features work identically
- **Code Reduction**: Main file reduced from 600+ lines to under 100 lines
- **Test Coverage**: Ability to unit test individual layer methods
- **Maintainability**: Easier to locate and modify specific functionality
- **Developer Productivity**: Faster development of new features

## Next Steps
1. **Review and Approval**: Get stakeholder approval for the plan
2. **Team Preparation**: Ensure team understands the layered approach
3. **Development Setup**: Set up development environment with new structure
4. **Phase 1 Kickoff**: Begin implementation of the Data layer
5. **Weekly Reviews**: Regular check-ins to monitor progress and adjust plan</content>
<parameter name="filePath">/Users/nathanmartin/Downloads/26 Senior Spring/MISY350/Mid-Semester Project/Structural Changes Plan - May 8, 2026.md