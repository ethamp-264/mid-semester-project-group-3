"""
UI Layer - Handles all user interface operations and Streamlit components
"""

from typing import Dict, Any, List, Optional
import streamlit as st # type: ignore
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
        """
        self.business_service = business_service
        self.data_manager = data_manager

    def apply_custom_styling(self) -> None:
        """
        Injects CSS to define custom fonts, background styling, and button colors.
        """
        st.markdown("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
            
            html, body, [class*="css"]  {
                font-family: 'Inter', sans-serif;
            }

            h1, h2, h3 {
                color: #00D4FF; 
                font-weight: 700;
            }

            [data-testid="stMetricValue"] {
                font-size: 28px;
                color: #FFB703;
            }
            
            div.stButton > button:first-child {
                border-radius: 8px;
                height: 3em;
                transition: 0.3s;
            }
            </style>
        """, unsafe_allow_html=True)

    def initialize_session(self) -> None:
        """
        Set up Streamlit page configuration and initialize session state.
        This matches the call in your app.py on line 49.
        """
        self.apply_custom_styling()
        if "logged_in" not in st.session_state:
            st.session_state["logged_in"] = False
        if "user" not in st.session_state:
            st.session_state["user"] = None
        if "role" not in st.session_state:
            st.session_state["role"] = None
        if "page" not in st.session_state:
            st.session_state["page"] = "login"

    def render_login_page(self) -> Optional[str]:
        """
        Render login and registration page. Handles logic for auth and account creation.
        """
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("### Welcome Back")
            
            with st.container(border=True):
                email_input = st.text_input("Email", key="email_login")
                password_input = st.text_input("Password", type="password", key="password_login")
                
                if st.button("Log In", type="primary", use_container_width=True):
                    with st.status("Authenticating...", expanded=False) as status:
                        user = self.business_service.authenticate_user(email_input, password_input)
                        time.sleep(1)
                        if user:
                            status.update(label="Success!", state="complete")
                            st.session_state["logged_in"] = True
                            st.session_state["user"] = user
                            st.session_state["role"] = user["role"]
                            st.session_state["page"] = "home"
                            st.rerun()
                        else:
                            status.update(label="Login Failed", state="error")
                            st.error("Invalid credentials")
            
            st.subheader("New Account")
            self.render_user_registration()
            
            st.write("---")
            users = self.data_manager.load_users()
            st.dataframe(users)
        return None

    def render_user_registration(self) -> None:
        """
        Component for new user registration.
        """
        with st.container(border=True):
            new_email = st.text_input("Email", key="email_register")
            new_password = st.text_input("Password", type="password", key="password_register")
            role = st.radio("Role", ["Manager", "Customer"], horizontal=True)

            if st.button("Create Account", key="register_btn", use_container_width=True):
                user_data = {"email": new_email, "password": new_password, "role": role}
                if self.business_service.register_user(user_data):
                    st.success("Account created!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("An account with this email already exists!")

    def render_manager_dashboard(self) -> None:
        """
        Render the manager dashboard with metrics and administration tabs.
        """
        st.title("Manager Control Center")
        
        inventory = self.data_manager.load_inventory()
        orders = self.data_manager.load_orders()
        
        m1, m2 = st.columns(2)
        m1.metric("Stock Volume", sum(i["stock"] for i in inventory))
        m2.metric("Active Orders", len(orders))

        st.divider()

        tab11, tab22, tab33, tab44 = st.tabs(["Inventory", "Update Inventory", "Order Management", "Delete Order"])

        with tab11:
            self.render_inventory_tab()

        with tab22:
            self.render_update_inventory_tab()

        with tab33:
            self.render_order_management_tab()

        with tab44:
            self.render_delete_order_tab()

        with st.sidebar:
            st.title("HEV Portal")
            st.divider()
            st.subheader("User Profile")
            st.info(f"**Role:** {st.session_state['role']}")
            st.caption(f"Welcome back {st.session_state['user']['email']}!")
            st.divider()
            if st.button("Log out", use_container_width=True):
                st.session_state.clear()
                st.rerun()

    def render_customer_dashboard(self) -> None:
        """
        Render the customer dashboard for ordering.
        """
        st.title("Customer Experience")
        tab1, tab2, tab3 = st.tabs(["Car Information", "Place Order", "Previous Orders"])

        with tab1:
            self.render_car_information_tab()

        with tab2:
            self.render_place_order_tab()

        with tab3:
            self.render_previous_orders_tab()

        with st.sidebar:
            st.title("HEV Portal")
            st.divider()
            st.subheader("User Profile")
            st.info(f"**Role:** {st.session_state['role']}")
            st.caption(f"Welcome back {st.session_state['user']['email']}!")
            st.divider()
            if st.button("Log out", use_container_width=True):
                st.session_state.clear()
                st.rerun()

    def render_previous_orders_tab(self) -> None:
        """
        Render previous orders for the current customer.
        """
        st.subheader("Previous Orders")
            
        orders = self.data_manager.load_orders()
        current_user_email = st.session_state["user"]["email"]

        filtered_orders = []
        for order in orders:
            if order.get("Customer Email") == current_user_email:
                filtered_orders.append(order)

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

    def render_place_order_tab(self) -> None:
        """
        Render order placement form with summary.
        """
        col1, col2 = st.columns([3, 2])
        
        with col1:
            order_selection = st.selectbox("Cars for Sale:",
                                         ["Select a Car", "Sedan", "Truck", "SUV", "Van"],
                                         help="Select an item from the drop down menu",
                                         key="order_select")
            order_quantity = st.number_input("Quantity:", step=1, key="order_qty")
            order_name = st.text_input("Name:", placeholder="Ex. John", key="cust_name")
            order_btn = st.button("Place Order", disabled=False, use_container_width=True, type="primary")
            
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
                        st.success("Order Placed Successfully!")
                        # Store order details for summary
                        st.session_state["last_order"] = result
                        st.session_state["last_order_total"] = self.business_service.calculate_order_total(order_selection, order_quantity)
                    else:
                        st.error(result.get("error", "Failed to place order"))

        with col2:
            if "last_order" in st.session_state and order_btn:
                with st.container(border=True):
                    st.markdown("### Order Summary")
                    st.divider()

                    st.markdown(f"**Car:** {st.session_state['last_order']['Item']}")
                    st.markdown(f"**Quantity:** {st.session_state['last_order']['Quantity']}")
                    st.markdown(f"**Total:** ${st.session_state['last_order_total']:.2f}")
                    st.markdown(f"**Customer:** {st.session_state['last_order']['Customer']}")
                    st.divider()
                    st.caption("*Thank you valued customer!*")

    def render_car_information_tab(self) -> None:
        """
        Render car information display.
        """
        st.subheader("Car Information")

        inventory = self.data_manager.load_inventory()
        car_names = []

        for item in inventory:
            if item["type"] == "Product":
                car_names.append(item["name"])

        selected_car = st.selectbox(
            "Select a Car",
            car_names,
            key="car_info_select"
        )

        for item in inventory:
            if item["name"] == selected_car:
                col5, col6 = st.columns([2, 1])

                with col5:
                    st.markdown(f"### {item['name']}")
                    st.markdown(f"**Price:** ${item['price']}")
                    st.markdown(f"**Stock:** {item['stock']}")
                    st.markdown(f"**Batteries:** {item['batteries']}")

                with col6:
                    st.markdown("**Colors:**")
                    for color in item["colors"]:
                        st.markdown(f"- {color}")

    def render_inventory_tab(self) -> None:
        """
        Render detailed inventory view with search and metrics.
        """
        inventory = self.data_manager.load_inventory()

        st.subheader("View Inventory")

        col3, col4 = st.columns([2, 3])

        with col3:
            with st.container(border=True):
                search_item = st.text_input("Search Item", placeholder="Enter item here...")

                total_stock = 0
                WIP_total = 0
                product_total = 0

                for item in inventory:
                    total_stock += item["stock"]

                    if item["type"] == "WIP":
                        WIP_total += item["stock"]

                    elif item["type"] == "Product":
                        product_total += item["stock"]

                st.metric("Total Items in Stock", total_stock)
                st.metric("Total WIP Stock", WIP_total)
                st.metric("Total Product Stock", product_total)

        with col4:
            with st.container(border=True):
                if search_item != "":
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

    def render_update_inventory_tab(self) -> None:
        """
        Render restock and assembly interface.
        """
        col7, col8 = st.columns([1, 1])

        with col7:
            with st.container(border=True):
                st.subheader("Restock WIP")

                restock_item = st.selectbox("Restock Options:",
                                            ["Select an item", "Wheels", "Engine", "Battery", "Frame"],
                                            help="Select an item from the drop down menu to restock",
                                            key="restock_select")

                restock_qty = st.number_input("Add to stock:", step=1, min_value=1, key="restock_qty")

                restock_btn = st.button("Restock Item", 
                                        key="restock_btn", 
                                        use_container_width=True, 
                                        type="primary")

                if restock_btn:
                    if restock_item == "Select an item":
                        st.warning("Please select a valid item to restock.")
                    else:
                        with st.spinner("Updating Stock..."):
                            time.sleep(2)
                        success = self.business_service.restock_item(restock_item, restock_qty)
                        if success:
                            st.success("Item Restocked Successfully!")
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("Failed to restock item.")

        with col8:
            with st.container(border=True):
                st.subheader("Restock Cars")

                car_assemble_selection = st.selectbox("Cars for Assembly:",
                                                     ["Select a Car", "Sedan", "Truck", "SUV", "Van"],
                                                     key="assemble_select")
                
                assemble_qty = st.number_input("Quantity to Assemble:", 
                                               step=1, 
                                               min_value=1, 
                                               key="assemble_qty")
                
                assemble_btn = st.button("Assemble Cars", 
                                        key="assemble_btn", 
                                        use_container_width=True, 
                                        type="primary")

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
                            st.error(message)

    def render_order_management_tab(self) -> None:
        """
        Render order management interface for shipping orders.
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
                                success = self.business_service.update_order_status(order['Order_ID'], "Shipped")
                                if success:
                                    st.success("Order updated!")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("Failed to update order.")
                        else:
                            st.write("Task Complete")

    def render_delete_order_tab(self) -> None:
        """
        Render order deletion interface.
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
                                success = self.business_service.delete_order(order['Order_ID'])
                                if success:
                                    st.error("Order removed from system.")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("Failed to delete order.")