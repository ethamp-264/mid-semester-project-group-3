"""
UI Layer - Handles all user interface operations and Streamlit components
"""

from typing import Dict, Any, List, Optional
import streamlit as st  # type: ignore
import time
from Service.service import BusinessService
from Data.data import DataManager


class UIManager:
    """
    UIManager class handles all user interface operations including
    rendering pages, components, and managing user interactions.
    """

    def __init__(self, business_service: BusinessService, data_manager: DataManager):
        """
        Initialize UIManager with service and data manager instances.
        
        Args:
            business_service: BusinessService instance for business logic
            data_manager: DataManager instance for data operations
        """
        self.business_service = business_service
        self.data_manager = data_manager

    def initialize_app(self) -> None:
        """
        Set up Streamlit page configuration and initialize session state.
        """
        # Session state is initialized in main app.py
        pass

    def render_login_page(self) -> Optional[str]:
        """
        Render login and registration page.
        
        Returns:
            Action string indicating what was clicked, or None
        """
        st.subheader("Log In")
        with st.container(border=True):
            email_input = st.text_input("Email", key="email_login")
            password_input = st.text_input("Password", type="password", key="password_login")

            if st.button("Log In", type="primary", use_container_width=True):
                with st.spinner("Logging in..."):
                    time.sleep(2)

                found_user = self.business_service.authenticate_user(email_input, password_input)

                if found_user:
                    st.success(f"Welcome back, {found_user['email']}!")
                    st.session_state["logged_in"] = True
                    st.session_state["user"] = found_user
                    st.session_state["role"] = found_user["role"]
                    st.session_state["page"] = "home"
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("Invalid credentials")
                return "login"

        # Registration section
        st.subheader("New Account")
        with st.container(border=True):
            new_email = st.text_input("Email", key="email_register")
            new_password = st.text_input("Password", type="password", key="password_register")
            role = st.radio("Role", ["Manager", "Customer"], horizontal=True)

            if st.button("Create Account", key="register_btn"):
                with st.spinner("Creating account..."):
                    time.sleep(2)

                user_data = {
                    "email": new_email,
                    "password": new_password,
                    "role": role
                }

                if self.business_service.register_user(user_data):
                    st.success("Account created!")
                    st.rerun()
                else:
                    st.error("An account with this email already exists! Please log in above.")
                return "register"

        st.write("---")
        users = self.data_manager.load_users()
        st.dataframe(users)
        return None

    def render_manager_dashboard(self) -> None:
        """
        Render the manager dashboard with inventory, restocking, and order management.
        """
        st.markdown("Manager Dashboard")

        tab1, tab2, tab3, tab4 = st.tabs(["Inventory", "Update Inventory", "Order Management", "Delete Order"])

        with tab1:
            self.render_inventory_view()

        with tab2:
            self.render_restock_interface()

        with tab3:
            self.render_order_management()

        with tab4:
            self.render_delete_orders()

        # Logout button
        if st.button("Log out", use_container_width=True, key="manager_logout"):
            with st.spinner("Logging out..."):
                st.session_state["logged_in"] = False
                st.session_state["user"] = None
                st.session_state["role"] = None
                st.session_state["page"] = "login"
                time.sleep(2)
                st.rerun()

    def render_customer_dashboard(self) -> None:
        """
        Render the customer dashboard with car information and ordering.
        """
        st.markdown("Customer Dashboard")

        tab1, tab2, tab3 = st.tabs(["Car Information", "Place Order", "Previous Orders"])

        with tab1:
            self.render_car_information()

        with tab2:
            self.render_order_form()

        with tab3:
            self.render_customer_orders()

        # Logout button
        if st.button("Log out", use_container_width=True, key="customer_logout"):
            with st.spinner("Logging out..."):
                st.session_state["logged_in"] = False
                st.session_state["user"] = None
                st.session_state["role"] = None
                st.session_state["page"] = "login"
                time.sleep(2)
                st.rerun()

    def render_inventory_view(self) -> None:
        """
        Render inventory viewing component with search and stock metrics.
        """
        st.subheader("View Inventory")

        col1, col2 = st.columns([2, 3])

        inventory = self.data_manager.load_inventory()

        with col1:
            with st.container(border=True):
                search_item = st.text_input("Search Item", placeholder="Enter item here...")

                total_stock = sum(item["stock"] for item in inventory)
                wip_total = sum(item["stock"] for item in inventory if item["type"] == "WIP")
                product_total = sum(item["stock"] for item in inventory if item["type"] == "Product")

                st.metric("Total Items in Stock", total_stock)
                st.metric("Total WIP Stock", wip_total)
                st.metric("Total Product Stock", product_total)

        with col2:
            with st.container(border=True):
                if search_item:
                    item_exists = False
                    for item in inventory:
                        if item["name"].lower() == search_item.lower():
                            item_exists = True
                            st.markdown("### Search Result")
                            st.markdown(f"Item ID: {item['id']}")
                            st.markdown(f"Name: {item['name']}")
                            st.markdown(f"Price: ${item['price']}")
                            st.markdown(f"Stock: {item['stock']}")

                    if not item_exists:
                        st.markdown("Item not found. Please try again.")
                else:
                    st.markdown("### All Inventory Items")
                    threshold = 5
                    for item in inventory:
                        if item["stock"] < threshold:
                            st.markdown(
                                f"**{item['name']}** | Price: ${item['price']} | Stock: {item['stock']} | **LOW STOCK!**"
                            )
                        else:
                            st.markdown(
                                f"{item['name']} | Price: ${item['price']} | Stock: {item['stock']}"
                            )

    def render_restock_interface(self) -> None:
        """
        Render restocking and car assembly interface.
        """
        col1, col2 = st.columns([1, 1])

        with col1:
            with st.container(border=True):
                st.subheader("Restock WIP")

                restock_item = st.selectbox(
                    "Restock Options:",
                    ["Select an item", "Wheels", "Engine", "Battery", "Frame"],
                    help="Select an item from the drop down menu to restock",
                    key="restock_select"
                )

                restock_qty = st.number_input("Add to stock:", step=1, min_value=1, key="restock_qty")

                restock_btn = st.button("Restock Item", key="restock_btn", use_container_width=True, type="primary")

                if restock_btn:
                    if restock_item == "Select an item":
                        st.warning("Please select an item to restock")
                    else:
                        with st.spinner("Updating Stock..."):
                            time.sleep(2)
                        if self.business_service.restock_item(restock_item, restock_qty):
                            st.success("Item Restocked Successfully!")
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("Failed to restock item")

        with col2:
            with st.container(border=True):
                st.subheader("Restock Cars")

                car_assemble_selection = st.selectbox(
                    "Cars for Assembly:",
                    ["Select a Car", "Sedan", "Truck", "SUV", "Van"],
                    key="assemble_select"
                )

                assemble_qty = st.number_input(
                    "Quantity to Assemble:", step=1, min_value=1, key="assemble_qty"
                )

                assemble_btn = st.button(
                    "Assemble Cars", key="assemble_btn", use_container_width=True, type="primary"
                )

                if assemble_btn:
                    if car_assemble_selection == "Select a Car":
                        st.warning("Please select a valid car to assemble.")
                    else:
                        with st.spinner("Assembling car..."):
                            time.sleep(2)
                        success, message = self.business_service.assemble_car(car_assemble_selection, assemble_qty)
                        if success:
                            st.success(message)
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error(f"Assembly Failed: {message}")

    def render_order_management(self) -> None:
        """
        Render order management interface for marking orders as shipped.
        """
        st.subheader("Active Customer Orders")

        orders = self.data_manager.load_orders()

        if not orders:
            st.info("No orders currently in the system.")
        else:
            for index, order in enumerate(orders):
                with st.container(border=True):
                    col_info, col_action = st.columns([3, 1])

                    with col_info:
                        st.markdown(f"**Order ID:** {order['Order_ID']} | **Customer:** {order['Customer']}")
                        st.markdown(f"**Item:** {order['Item']} | **Qty:** {order['Quantity']} | **Total:** ${order['Total']}")
                        status = order['Status']
                        if status == "Placed":
                            st.markdown(f"**Status:** :orange[{status}]")
                        else:
                            st.markdown(f"**Status:** :green[{status}]")

                    with col_action:
                        if order['Status'] == "Placed":
                            if st.button(f"Mark Shipped", key=f"ship_{index}", use_container_width=True):
                                if self.business_service.update_order_status(order['Order_ID'], "Shipped"):
                                    st.success("Order updated!")
                                    time.sleep(1)
                                    st.rerun()
                        else:
                            st.write("Task Complete")

    def render_delete_orders(self) -> None:
        """
        Render order deletion interface with confirmation.
        """
        st.subheader("Delete Orders")
        st.warning("Caution: Deleting an order is permanent.")

        orders = self.data_manager.load_orders()

        if not orders:
            st.info("No orders found to delete.")
        else:
            for index, order in enumerate(orders):
                with st.container(border=True):
                    col_text, col_delete = st.columns([3, 1])

                    with col_text:
                        st.write(f"**{order['Order_ID']}** - {order['Customer']}")
                        st.caption(f"{order['Item']} | Qty: {order['Quantity']}")

                    with col_delete:
                        confirm_check = st.checkbox(f"Confirm delete {order['Order_ID']}", key=f"conf_{index}")
                        if confirm_check:
                            if st.button("Permanently Delete", key=f"del_{index}", type="primary", use_container_width=True):
                                if self.business_service.delete_order(order['Order_ID']):
                                    st.error("Order removed from system.")
                                    time.sleep(1)
                                    st.rerun()

    def render_car_information(self) -> None:
        """
        Render car information viewing component for customers.
        """
        st.subheader("Car Information")

        inventory = self.data_manager.load_inventory()
        car_names = [item["name"] for item in inventory if item["type"] == "Product"]

        selected_car = st.selectbox("Select a Car", car_names, key="car_info_select")

        for item in inventory:
            if item["name"] == selected_car:
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"### {item['name']}")
                    st.markdown(f"**Price:** ${item['price']}")
                    st.markdown(f"**Stock:** {item['stock']}")
                    st.markdown(f"**Batteries:** {item.get('batteries', 'N/A')}")

                with col2:
                    st.markdown("**Colors:**")
                    for color in item.get("colors", []):
                        st.markdown(f"- {color}")

    def render_order_form(self) -> Optional[Dict[str, Any]]:
        """
        Render order placement form for customers.
        
        Returns:
            Order data dictionary if order placed, None otherwise
        """
        col1, col2 = st.columns([3, 2])

        with col1:
            order_selection = st.selectbox(
                "Cars for Sale:",
                ["Select a Car", "Sedan", "Truck", "SUV", "Van"],
                help="Select an item from the drop down menu",
                key="order_select"
            )
            order_quantity = st.number_input("Quantity:", step=1, key="order_qty")
            order_name = st.text_input("Name:", placeholder="Ex. John", key="cust_name")
            order_btn = st.button("Place Order", use_container_width=True, type="primary")

            total_price = 0
            if order_btn:
                if order_selection == "Select a Car":
                    st.warning("Please select a car.")
                elif not order_name:
                    st.warning("A name for the order must be provided!")
                elif order_quantity < 1:
                    st.warning("Invalid quantity!")
                else:
                    with st.spinner("Placing Order..."):
                        time.sleep(2)

                    order_data = {
                        "item": order_selection,
                        "quantity": order_quantity,
                        "customer_name": order_name,
                        "customer_email": st.session_state["user"]["email"]
                    }

                    success, result = self.business_service.place_order(order_data)
                    if success:
                        total_price = result.get("Total", 0)
                        st.success("Order Placed Successfully!")
                    else:
                        st.error(f"Order Failed: {result.get('error', 'Unknown error')}")
                    return result if success else None

        with col2:
            if order_btn:
                with st.container(border=True):
                    st.markdown("### Order Summary")
                    st.divider()
                    st.markdown(f"**Car:** {order_selection}")
                    st.markdown(f"**Quantity:** {order_quantity}")
                    st.markdown(f"**Total:** ${total_price:.2f}")
                    st.markdown(f"**Customer:** {order_name}")
                    st.divider()
                    st.caption("*Thank you valued customer!*")
        return None

    def render_customer_orders(self) -> None:
        """
        Render customer's previous orders.
        """
        st.subheader("Previous Orders")

        orders = self.data_manager.load_orders()
        current_user_email = st.session_state["user"]["email"]

        filtered_orders = [order for order in orders if order.get("Customer Email") == current_user_email]

        if not filtered_orders:
            st.info("You have not placed any orders yet.")
        else:
            for index, order in enumerate(filtered_orders):
                with st.container(border=True):
                    col_info, col_action = st.columns([3, 1])

                    with col_info:
                        st.markdown(f"**Order ID:** {order['Order_ID']} | **Customer:** {order['Customer']}")
                        st.markdown(f"**Item:** {order['Item']} | **Qty:** {order['Quantity']} | **Total:** ${order['Total']}")
                        status = order['Status']
                        if status == "Placed":
                            st.markdown(f"**Status:** :orange[{status}]")
                        else:
                            st.markdown(f"**Status:** :green[{status}]")

    def display_message(self, message: str, message_type: str) -> None:
        """
        Display a message to the user.
        
        Args:
            message: Message text to display
            message_type: Type of message ('success', 'error', 'warning', 'info')
        """
        if message_type == "success":
            st.success(message)
        elif message_type == "error":
            st.error(message)
        elif message_type == "warning":
            st.warning(message)
        elif message_type == "info":
            st.info(message)

    def handle_user_input(self, component: str, data: Dict[str, Any]) -> Any:
        """
        Process user input from components.
        
        Args:
            component: Type of component
            data: Data from the component
            
        Returns:
            Result of the operation
        """
        if component == "order":
            return self.business_service.place_order(data)
        elif component == "assembly":
            return self.business_service.assemble_car(data.get("car_type"), data.get("quantity"))
        elif component == "restock":
            return self.business_service.restock_item(data.get("item_name"), data.get("quantity"))
        return None

    def manage_session(self, action: str, data: Dict[str, Any] = None) -> None:
        """
        Manage Streamlit session state.
        
        Args:
            action: Action to perform ('login', 'logout', 'set_page', 'clear')
            data: Optional data to set in session
        """
        if action == "login":
            st.session_state["logged_in"] = True
            if data:
                st.session_state["user"] = data.get("user")
                st.session_state["role"] = data.get("role")
                st.session_state["page"] = data.get("page", "home")

        elif action == "logout":
            st.session_state["logged_in"] = False
            st.session_state["user"] = None
            st.session_state["role"] = None
            st.session_state["page"] = "login"

        elif action == "set_page":
            st.session_state["page"] = data.get("page") if data else "home"

        elif action == "clear":
            for key in list(st.session_state.keys()):
                del st.session_state[key]
