"""
Service Layer - Contains business logic and application workflows
"""

from typing import Dict, List, Any, Tuple
import uuid
from Data.data import DataManager


class BusinessService:
    """
    BusinessService class contains all business logic including user authentication,
    inventory management, order processing, and validation of business rules.
    """

    def __init__(self, data_manager: DataManager):
        """
        Initialize BusinessService with a DataManager instance.
        
        Args:
            data_manager: DataManager instance for data operations
        """
        self.data_manager = data_manager
        self.users = self.data_manager.load_users()
        self.inventory = self.data_manager.load_inventory()
        self.orders = self.data_manager.load_orders()

    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            User dictionary if authenticated, None otherwise
        """
        self.users = self.data_manager.load_users()
        for user in self.users:
            if user["email"].strip().lower() == email.strip().lower() and user["password"] == password:
                return user
        return None

    def register_user(self, user_data: Dict[str, Any]) -> bool:
        """
        Register a new user.
        
        Args:
            user_data: Dictionary containing email, password, and role
            
        Returns:
            True if registration successful, False otherwise
        """
        self.users = self.data_manager.load_users()
        
        # Check if email already exists
        for user in self.users:
            if user["email"].strip().lower() == user_data["email"].strip().lower():
                return False

        # Create new user
        new_user = {
            "id": str(uuid.uuid4()),
            "email": user_data["email"],
            "password": user_data["password"],
            "role": user_data.get("role", "Customer")
        }

        self.users.append(new_user)
        return self.data_manager.save_users(self.users)

    def restock_item(self, item_name: str, quantity: int) -> bool:
        """
        Restock an inventory item by adding quantity.
        
        Args:
            item_name: Name of the item to restock
            quantity: Quantity to add
            
        Returns:
            True if successful, False otherwise
        """
        self.inventory = self.data_manager.load_inventory()
        
        for item in self.inventory:
            if item["name"] == item_name:
                item["stock"] += quantity
                return self.data_manager.save_inventory(self.inventory)
        
        return False

    def assemble_car(self, car_type: str, quantity: int) -> Tuple[bool, str]:
        """
        Assemble cars by consuming required parts from inventory.
        
        Args:
            car_type: Type of car to assemble
            quantity: Number of cars to assemble
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        self.inventory = self.data_manager.load_inventory()
        
        # Get car item
        car_item = None
        for item in self.inventory:
            if item["name"] == car_type and item["type"] == "Product":
                car_item = item
                break

        if not car_item:
            return False, "Car type not found"

        # Check assembly requirements
        requirements = self.check_assembly_requirements(car_type, quantity)
        if not requirements["possible"]:
            return False, requirements["message"]

        # Deduct parts from inventory
        wheels_needed = car_item.get("wheels", 0) * quantity
        engine_needed = car_item.get("engine", 0) * quantity
        battery_needed = car_item.get("batteries", 0) * quantity
        frame_needed = car_item.get("frame", 0) * quantity

        for item in self.inventory:
            if item["name"] == "Wheels":
                item["stock"] -= wheels_needed
            elif item["name"] == "Engine":
                item["stock"] -= engine_needed
            elif item["name"] == "Battery":
                item["stock"] -= battery_needed
            elif item["name"] == "Frame":
                item["stock"] -= frame_needed

        # Add assembled cars to inventory
        car_item["stock"] += quantity

        success = self.data_manager.save_inventory(self.inventory)
        message = f"Successfully assembled {quantity} {car_type}(s)!" if success else "Failed to save inventory"
        return success, message

    def check_assembly_requirements(self, car_type: str, quantity: int) -> Dict[str, Any]:
        """
        Check if assembly is possible given current inventory.
        
        Args:
            car_type: Type of car to check
            quantity: Quantity to check assembly for
            
        Returns:
            Dictionary with 'possible' bool and 'message' string, plus part counts
        """
        self.inventory = self.data_manager.load_inventory()
        
        # Find car item
        car_item = None
        for item in self.inventory:
            if item["name"] == car_type and item["type"] == "Product":
                car_item = item
                break

        if not car_item:
            return {"possible": False, "message": "Car type not found"}

        # Get required parts
        wheels_needed = car_item.get("wheels", 0) * quantity
        engine_needed = car_item.get("engine", 0) * quantity
        battery_needed = car_item.get("batteries", 0) * quantity
        frame_needed = car_item.get("frame", 0) * quantity

        # Check available parts
        wheels_in_stock = 0
        engine_in_stock = 0
        battery_in_stock = 0
        frame_in_stock = 0

        for item in self.inventory:
            if item["name"] == "Wheels":
                wheels_in_stock = item["stock"]
            elif item["name"] == "Engine":
                engine_in_stock = item["stock"]
            elif item["name"] == "Battery":
                battery_in_stock = item["stock"]
            elif item["name"] == "Frame":
                frame_in_stock = item["stock"]

        # Validate requirements
        missing_parts = []
        if wheels_in_stock < wheels_needed:
            missing_parts.append(f"Wheels (need {wheels_needed}, have {wheels_in_stock})")
        if engine_in_stock < engine_needed:
            missing_parts.append(f"Engines (need {engine_needed}, have {engine_in_stock})")
        if battery_in_stock < battery_needed:
            missing_parts.append(f"Batteries (need {battery_needed}, have {battery_in_stock})")
        if frame_in_stock < frame_needed:
            missing_parts.append(f"Frames (need {frame_needed}, have {frame_in_stock})")

        if missing_parts:
            return {
                "possible": False,
                "message": f"Insufficient parts: {', '.join(missing_parts)}"
            }

        return {
            "possible": True,
            "message": "Assembly requirements met",
            "wheels": wheels_needed,
            "engines": engine_needed,
            "batteries": battery_needed,
            "frames": frame_needed
        }

    def place_order(self, order_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Place a new customer order.
        
        Args:
            order_data: Dictionary containing item, quantity, customer name, and email
            
        Returns:
            Tuple of (success: bool, order_dict: dict)
        """
        self.inventory = self.data_manager.load_inventory()
        self.orders = self.data_manager.load_orders()

        item_name = order_data.get("item")
        quantity = order_data.get("quantity", 0)
        customer_name = order_data.get("customer_name")
        customer_email = order_data.get("customer_email")

        # Validate input
        if not item_name or quantity < 1 or not customer_name:
            return False, {"error": "Invalid order data"}

        # Check if item exists and has stock
        item_found = False
        total_price = 0
        item_id = None

        for item in self.inventory:
            if item["name"] == item_name:
                item_found = True
                item_id = item.get("id")
                if item["stock"] >= quantity:
                    total_price = item["price"] * quantity
                    item["stock"] -= quantity
                    break
                else:
                    return False, {"error": "Insufficient stock"}

        if not item_found:
            return False, {"error": "Item not found"}

        # Save updated inventory
        self.data_manager.save_inventory(self.inventory)

        # Create order
        new_order = {
            "Order_ID": f"Order_{len(self.orders) + 101}",
            "Customer": customer_name,
            "Customer Email": customer_email,
            "Item": item_name,
            "Item ID": item_id,
            "Quantity": quantity,
            "Status": "Placed",
            "Total": total_price
        }

        self.orders.append(new_order)
        success = self.data_manager.save_orders(self.orders)

        return success, new_order

    def update_order_status(self, order_id: str, status: str) -> bool:
        """
        Update the status of an order.
        
        Args:
            order_id: Order ID to update
            status: New status for the order
            
        Returns:
            True if successful, False otherwise
        """
        self.orders = self.data_manager.load_orders()
        
        for order in self.orders:
            if order["Order_ID"] == order_id:
                order["Status"] = status
                return self.data_manager.save_orders(self.orders)
        
        return False

    def delete_order(self, order_id: str) -> bool:
        """
        Delete an order from the system.
        
        Args:
            order_id: Order ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        self.orders = self.data_manager.load_orders()
        
        for index, order in enumerate(self.orders):
            if order["Order_ID"] == order_id:
                self.orders.pop(index)
                return self.data_manager.save_orders(self.orders)
        
        return False

    def calculate_order_total(self, item_name: str, quantity: int) -> float:
        """
        Calculate the total price for an order.
        
        Args:
            item_name: Name of the item
            quantity: Quantity being ordered
            
        Returns:
            Total price as float
        """
        self.inventory = self.data_manager.load_inventory()
        
        for item in self.inventory:
            if item["name"] == item_name:
                return item["price"] * quantity
        
        return 0.0

    def validate_business_rules(self, operation: str, data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate business rules for operations.
        
        Args:
            operation: Type of operation (e.g., 'order', 'assembly', 'restock')
            data: Data related to the operation
            
        Returns:
            Tuple of (valid: bool, message: str)
        """
        if operation == "order":
            if data.get("quantity", 0) < 1:
                return False, "Quantity must be at least 1"
            if not data.get("customer_name"):
                return False, "Customer name is required"
            if not data.get("item"):
                return False, "Item is required"
            return True, "Order validation passed"

        elif operation == "assembly":
            if data.get("quantity", 0) < 1:
                return False, "Quantity must be at least 1"
            if not data.get("car_type"):
                return False, "Car type is required"
            return True, "Assembly validation passed"

        elif operation == "restock":
            if data.get("quantity", 0) < 1:
                return False, "Quantity must be at least 1"
            if not data.get("item_name"):
                return False, "Item name is required"
            return True, "Restock validation passed"

        return False, "Unknown operation"
