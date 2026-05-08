# Current App Structure Analysis

## Prompter: Nathan Martin

## Origin Prompt
In a separate markdown file titled "Current App Structure Analysis," analyze the current app structure of inv_manager.py. The analysis should identify the UI layer, service layer, data/database layer, models/classes, and important dependencies. Explain what should be protected before making changes. Record the prompt that generated this analysis in the correct order in the document created, under a section such as Origin Prompt.

## Overview
The `inv_manager.py` file is a Streamlit-based web application for managing inventory for Horizon Electric Vehicles (HEV). It provides functionality for both managers and customers, including inventory viewing, restocking, car assembly, order management, and user authentication. The application uses a monolithic structure where all layers are combined in a single file.

## UI Layer
The UI layer is implemented using Streamlit throughout the entire application. Key UI components include:
- Login and registration forms
- Tabbed interfaces for manager dashboard (Inventory, Update Inventory, Order Management, Delete Order)
- Tabbed interfaces for customer dashboard (Car Information, Place Order, Previous Orders)
- Columns, containers, and interactive elements like buttons, selectboxes, text inputs, and number inputs
- Session state management for user authentication and page navigation
- Metrics display for inventory statistics
- Spinners and success/error messages for user feedback

The UI handles all user interactions and displays data directly from the loaded JSON files.

## Service Layer
The service layer contains business logic mixed throughout the UI code. Key service functionalities include:
- User authentication and session management
- Inventory restocking logic (adding stock to WIP items like Wheels, Engine, Battery, Frame)
- Car assembly logic (checking part availability, deducting parts from inventory, adding assembled cars)
- Order placement and management (creating orders, updating status from "Placed" to "Shipped", deleting orders)
- Inventory search and filtering
- Low stock alerts and metrics calculation

Business rules are hardcoded, such as:
- Assembly requirements (e.g., Sedan needs 4 wheels, 1 engine, 1 battery, 1 frame)
- Order validation (stock availability, required fields)
- Role-based access control (Manager vs Customer features)

## Data/Database Layer
The data layer uses JSON files for persistence with no database abstraction:
- `inventory.json`: Stores inventory items with fields like id, name, price, stock, type, and assembly requirements
- `orders.json`: Stores customer orders with Order_ID, Customer, Item, Quantity, Status, Total, etc.
- `users.json`: Stores user accounts with id, email, password, role

Data operations are performed directly in the code:
- Loading JSON files at startup
- Writing back to JSON files after modifications
- No data validation or error handling for file operations
- No concurrency control or transaction management

## Models/Classes
There are no explicit model classes or data structures defined. Data is represented as:
- Python dictionaries for individual items/orders/users
- Lists of dictionaries for collections
- No object-oriented design or encapsulation
- Data validation is minimal and scattered throughout the UI logic

## Important Dependencies
- `streamlit`: Core framework for the web application UI
- `json`: For reading/writing JSON data files
- `pathlib.Path`: For file path handling
- `datetime`: Imported but not used in the visible code
- `uuid`: For generating unique user IDs during registration
- `time`: For sleep delays in UI feedback (spinners, success messages)

## What Should Be Protected Before Making Changes
Before refactoring or modifying the application, the following should be backed up and protected:

1. **Data Files**: All JSON files (`inventory.json`, `orders.json`, `users.json`) contain critical business data that should be preserved
2. **User Authentication Logic**: The login and registration system, including default user accounts and session management
3. **Business Rules**: Hardcoded assembly requirements, pricing logic, and inventory management rules
4. **Existing Functionality**: Ensure all current features work before changes (inventory viewing, restocking, assembly, ordering, order management)
5. **User Experience**: The current UI flow and user interactions should be maintained or improved, not broken

Consider implementing proper version control, data backups, and potentially creating unit tests for business logic before architectural changes.</content>
<parameter name="filePath">/Users/nathanmartin/Downloads/26 Senior Spring/MISY350/Mid-Semester Project/Current App Structure Analysis.md