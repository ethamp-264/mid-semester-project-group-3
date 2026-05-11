"""
Data Layer - Handles all data persistence and retrieval operations
"""

import json
from pathlib import Path
from typing import List, Dict, Any
import shutil
from datetime import datetime


class DataManager:
    """
    DataManager class handles all data operations including loading, saving, and validating data.
    Centralizes access to inventory, orders, and user data from JSON files.
    """

    def __init__(self, data_dir: str = "."):
        """
        Initialize DataManager with paths to JSON data files.
        
        Args:
            data_dir: Directory where JSON files are stored (default: current directory)
        """
        self.data_dir = Path(data_dir)
        self.inventory_file = self.data_dir / "inventory.json"
        self.orders_file = self.data_dir / "orders.json"
        self.users_file = self.data_dir / "users.json"

    def load_inventory(self) -> List[Dict[str, Any]]:
        """
        Load inventory data from JSON file.
        
        Returns:
            List of inventory items, or empty list if file doesn't exist
        """
        try:
            if self.inventory_file.exists():
                with open(self.inventory_file, "r") as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading inventory: {e}")
            return []

    def save_inventory(self, inventory_data: List[Dict[str, Any]]) -> bool:
        """
        Save inventory data to JSON file.
        
        Args:
            inventory_data: List of inventory items to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.inventory_file, "w", encoding="utf-8") as f:
                json.dump(inventory_data, f)
            return True
        except Exception as e:
            print(f"Error saving inventory: {e}")
            return False

    def load_orders(self) -> List[Dict[str, Any]]:
        """
        Load orders data from JSON file.
        
        Returns:
            List of orders, or empty list if file doesn't exist
        """
        try:
            if self.orders_file.exists():
                with open(self.orders_file, "r") as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading orders: {e}")
            return []

    def save_orders(self, orders_data: List[Dict[str, Any]]) -> bool:
        """
        Save orders data to JSON file.
        
        Args:
            orders_data: List of orders to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.orders_file, "w", encoding="utf-8") as f:
                json.dump(orders_data, f)
            return True
        except Exception as e:
            print(f"Error saving orders: {e}")
            return False

    def load_users(self) -> List[Dict[str, Any]]:
        """
        Load users data from JSON file. Returns default users if file doesn't exist.
        
        Returns:
            List of users
        """
        try:
            if self.users_file.exists():
                with open(self.users_file, "r") as f:
                    return json.load(f)
            return self._get_default_users()
        except Exception as e:
            print(f"Error loading users: {e}")
            return self._get_default_users()

    def save_users(self, users_data: List[Dict[str, Any]]) -> bool:
        """
        Save users data to JSON file.
        
        Args:
            users_data: List of users to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.users_file, "w", encoding="utf-8") as f:
                json.dump(users_data, f)
            return True
        except Exception as e:
            print(f"Error saving users: {e}")
            return False

    def validate_data(self, data: Dict[str, Any], data_type: str) -> bool:
        """
        Validate data structure based on data type.
        
        Args:
            data: Data dictionary to validate
            data_type: Type of data ('user', 'inventory', 'order')
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(data, dict):
            return False

        if data_type == "user":
            required_fields = {"id", "email", "password", "role"}
            return required_fields.issubset(data.keys())

        elif data_type == "inventory":
            required_fields = {"id", "name", "price", "stock", "type"}
            return required_fields.issubset(data.keys())

        elif data_type == "order":
            required_fields = {"Order_ID", "Customer", "Item", "Quantity", "Status", "Total"}
            return required_fields.issubset(data.keys())

        return False

    def backup_data(self) -> bool:
        """
        Create backup of all data files.
        
        Returns:
            True if backup successful, False otherwise
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.data_dir / f"backup_{timestamp}"
            backup_dir.mkdir(exist_ok=True)

            if self.inventory_file.exists():
                shutil.copy2(self.inventory_file, backup_dir / "inventory.json")
            if self.orders_file.exists():
                shutil.copy2(self.orders_file, backup_dir / "orders.json")
            if self.users_file.exists():
                shutil.copy2(self.users_file, backup_dir / "users.json")

            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False

    def _get_default_users(self) -> List[Dict[str, Any]]:
        """
        Get default users for initial setup.
        
        Returns:
            List of default users
        """
        return [
            {
                "id": "1",
                "email": "manager@HEV.com",
                "password": "123",
                "role": "Manager",
            },
            {
                "id": "2",
                "email": "customer@HEV.com",
                "password": "456",
                "role": "Customer",
            },
            {
                "id": "3",
                "email": "customer2@HEV.com",
                "password": "789",
                "role": "Customer",
            }
        ]
