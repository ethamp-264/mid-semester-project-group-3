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

    STATUS_PLACED = "Placed"
    STATUS_SHIPPED = "Shipped"
    STATUS_CANCELLED = "Cancelled"
    STATUS_DELETED = "Deleted"
    STATUS_COMPLETED = "Completed"
    COMPLETED_STATUSES = {STATUS_SHIPPED, STATUS_COMPLETED}
    TERMINAL_STATUSES = {STATUS_CANCELLED, STATUS_DELETED, STATUS_SHIPPED, STATUS_COMPLETED}

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
        name = user_data.get("name", "").strip()
        email = user_data.get("email", "").strip()
        password = user_data.get("password", "")

        if not name or not email or not password:
            return False

        # Check if email already exists
        for user in self.users:
            if user["email"].strip().lower() == email.lower():
                return False

        # Create new user
        new_user = {
            "id": str(uuid.uuid4()),
            "email": email,
            "password": password,
            "role": user_data.get("role", "Customer"),
            "name": name
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

        # check_assembly_requirements reloads inventory, so reselect the car
        # from the current list before mutating and saving.
        car_item = None
        for item in self.inventory:
            if item["name"] == car_type and item["type"] == "Product":
                car_item = item
                break

        if not car_item:
            return False, "Car type not found"

        # Deduct parts from inventory
        wheels_needed = requirements.get("wheels", 0)
        engine_needed = requirements.get("engines", 0)
        battery_needed = requirements.get("batteries", 0)
        frame_needed = requirements.get("frames", 0)

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
        customer_name = order_data.get("customer_name", "").strip()
        customer_email = order_data.get("customer_email", "").strip()
        selected_color = order_data.get("color")

        # Validate input
        if not item_name or quantity < 1 or not customer_name or not customer_email:
            return False, {"error": "Invalid order data"}

        # Check if item exists and has stock
        item_found = False
        total_price = 0
        item_id = None
        item_colors = []

        for item in self.inventory:
            if item["name"] == item_name:
                item_found = True
                item_id = item.get("id")
                item_colors = item.get("colors", [])
                if item_colors and selected_color not in item_colors:
                    return False, {"error": "Please select a valid color"}
                if item["stock"] >= quantity:
                    total_price = item["price"] * quantity
                    item["stock"] -= quantity
                    break
                else:
                    return False, {"error": "Insufficient stock"}

        if not item_found:
            return False, {"error": "Item not found"}

        # Save updated inventory
        if not self.data_manager.save_inventory(self.inventory):
            return False, {"error": "Failed to update inventory"}

        # Create order
        new_order = {
            "Order_ID": self._generate_order_id(),
            "Customer": customer_name,
            "Customer Email": customer_email,
            "Item": item_name,
            "Item ID": item_id,
            "Color": selected_color,
            "Quantity": quantity,
            "Status": self.STATUS_PLACED,
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
                if order.get("Status") in {self.STATUS_CANCELLED, self.STATUS_DELETED}:
                    return False
                if order.get("Status") in self.COMPLETED_STATUSES and status == self.STATUS_DELETED:
                    return False
                order["Status"] = status
                return self.data_manager.save_orders(self.orders)

        return False

    def delete_order(self, order_id: str) -> bool:
        """
        Soft delete an order from the system.

        Args:
            order_id: Order ID to delete

        Returns:
            True if successful, False otherwise
        """
        success, _message = self.soft_delete_order(order_id)
        return success

    def soft_delete_order(self, order_id: str) -> Tuple[bool, str]:
        """
        Mark an order as deleted while preserving the order record.

        Args:
            order_id: Order ID to mark deleted

        Returns:
            Tuple of (success: bool, message: str)
        """
        self.orders = self.data_manager.load_orders()

        for order in self.orders:
            if order["Order_ID"] == order_id:
                status = order.get("Status")
                if status in self.COMPLETED_STATUSES:
                    return False, "Completed orders cannot be deleted"
                if status == self.STATUS_DELETED:
                    return False, "Order is already deleted"

                if status == self.STATUS_PLACED:
                    restored, message = self._restore_order_stock(order)
                    if not restored:
                        return False, message

                order["Status"] = self.STATUS_DELETED
                if self.data_manager.save_orders(self.orders):
                    return True, "Order marked as deleted"
                return False, "Failed to save order status"

        return False, "Order not found"

    def cancel_order(self, order_id: str, customer_email: str) -> Tuple[bool, str]:
        """
        Cancel a placed order owned by a customer and restore the reserved stock.

        Args:
            order_id: Order ID to cancel
            customer_email: Email of the customer requesting cancellation

        Returns:
            Tuple of (success: bool, message: str)
        """
        self.orders = self.data_manager.load_orders()

        for order in self.orders:
            if order["Order_ID"] != order_id:
                continue

            order_email = order.get("Customer Email", "").strip().lower()
            if order_email != customer_email.strip().lower():
                return False, "You can only cancel your own orders"

            if order.get("Status") != self.STATUS_PLACED:
                return False, "Only placed orders can be cancelled"

            restored, message = self._restore_order_stock(order)
            if not restored:
                return False, message

            order["Status"] = self.STATUS_CANCELLED
            if self.data_manager.save_orders(self.orders):
                return True, "Order cancelled"
            return False, "Failed to save order status"

        return False, "Order not found"

    def get_available_colors(self, item_name: str) -> List[str]:
        """
        Get available colors for a product.

        Args:
            item_name: Name of the product

        Returns:
            List of color names
        """
        self.inventory = self.data_manager.load_inventory()

        for item in self.inventory:
            if item["name"] == item_name and item.get("type") == "Product":
                return item.get("colors", [])

        return []

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
            if not data.get("color"):
                return False, "Color is required"
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

    def _generate_order_id(self) -> str:
        """
        Generate the next order ID without reusing IDs from soft-deleted orders.
        """
        highest_order_number = 100

        for order in self.orders:
            order_id = order.get("Order_ID", "")
            try:
                highest_order_number = max(highest_order_number, int(order_id.split("_")[1]))
            except (IndexError, ValueError):
                continue

        return f"Order_{highest_order_number + 1}"

    def _restore_order_stock(self, order: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Return reserved product stock for an order that is no longer active.
        """
        self.inventory = self.data_manager.load_inventory()
        item_id = order.get("Item ID")
        item_name = order.get("Item")
        quantity = order.get("Quantity", 0)

        for item in self.inventory:
            if item.get("id") == item_id or item.get("name") == item_name:
                item["stock"] += quantity
                if self.data_manager.save_inventory(self.inventory):
                    return True, "Stock restored"
                return False, "Failed to restore inventory"

        return False, "Order item not found in inventory"
