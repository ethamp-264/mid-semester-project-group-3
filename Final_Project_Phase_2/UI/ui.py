"""
UI Layer - Handles all user interface operations and Streamlit components
"""

from typing import Dict, Any, List, Optional
import streamlit as st # type: ignore
import time
from AI.ai_assistant import AIChatAssistant
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

    def get_current_user_name(self) -> str:
        """
        Return the current user's saved name with an email-based fallback.
        """
        user = st.session_state.get("user") or {}
        name = user.get("name", "").strip()
        if name:
            return name

        email = user.get("email", "")
        return email.split("@")[0] if email else ""

    def format_order_status(self, status: str) -> str:
        """
        Format order statuses consistently across manager and customer views.
        """
        status_colors = {
            "Placed": "orange",
            "Shipped": "green",
            "Completed": "green",
            "Cancelled": "red",
            "Deleted": "gray",
        }
        color = status_colors.get(status, "gray")
        return f":{color}[{status}]"

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
            new_name = st.text_input("Name", key="name_register")
            new_email = st.text_input("Email", key="email_register")
            new_password = st.text_input("Password", type="password", key="password_register")
            role = st.radio("Role", ["Manager", "Customer"], horizontal=True)

            if st.button("Create Account", key="register_btn", use_container_width=True):
                if not new_name.strip() or not new_email.strip() or not new_password:
                    st.error("Name, email, and password are required.")
                    return

                user_data = {
                    "name": new_name,
                    "email": new_email,
                    "password": new_password,
                    "role": role
                }
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
        active_orders = [
            order for order in orders
            if order.get("Status", "Placed") == "Placed"
        ]
        
        m1, m2 = st.columns(2)
        m1.metric("Stock Volume", sum(i["stock"] for i in inventory))
        m2.metric("Active Orders", len(active_orders))

        st.divider()

        tab11, tab22, tab33, tab44, tab55 = st.tabs(["Inventory", "Update Inventory", "Order Management", "Delete Order", "AI Assistant"])

        with tab11:
            self.render_inventory_tab()

        with tab22:
            self.render_update_inventory_tab()

        with tab33:
            self.render_order_management_tab()

        with tab44:
            self.render_delete_order_tab()

        with tab55:
            self.render_ai_assistant_tab()

        with st.sidebar:
            st.title("HEV Portal")
            st.divider()
            st.subheader("User Profile")
            st.info(f"**Role:** {st.session_state['role']}")
            st.caption(f"Welcome back {self.get_current_user_name()}!")
            st.divider()
            if st.button("Log out", use_container_width=True):
                st.session_state.clear()
                st.rerun()

    def render_customer_dashboard(self) -> None:
        """
        Render the customer dashboard for ordering.
        """
        st.title("Customer Experience")
        tab1, tab2, tab3, tab4 = st.tabs(["Car Information", "Place Order", "Previous Orders", "AI Assistant"])

        with tab1:
            self.render_car_information_tab()

        with tab2:
            self.render_place_order_tab()

        with tab3:
            self.render_previous_orders_tab()

        with tab4:
            self.render_ai_assistant_tab()

        with st.sidebar:
            st.title("HEV Portal")
            st.divider()
            st.subheader("User Profile")
            st.info(f"**Role:** {st.session_state['role']}")
            st.caption(f"Welcome back {self.get_current_user_name()}!")
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
                        color_text = f" | **Color:** {order.get('Color')}" if order.get("Color") else ""
                        st.markdown(
                            f"**Item:** {order['Item']}{color_text} | "
                            f"**Qty:** {order['Quantity']} | **Total:** ${order['Total']}"
                        )
                        status = order.get("Status", "Placed")
                        st.markdown(f"**Status:** {self.format_order_status(status)}")

                    with col_action:
                        if status == "Placed":
                            if st.button("Cancel Order", key=f"cancel_{index}", use_container_width=True):
                                success, message = self.business_service.cancel_order(
                                    order["Order_ID"],
                                    current_user_email
                                )
                                if success:
                                    st.success(message)
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(message)
                        elif status in {"Shipped", "Completed"}:
                            st.write("Completed")
                        else:
                            st.write("No action")

    def render_place_order_tab(self) -> None:
        """
        Render order placement form with summary.
        """
        col1, col2 = st.columns([3, 2])
        inventory = self.data_manager.load_inventory()
        car_names = [
            item["name"] for item in inventory
            if item.get("type", "").lower() == "product"
        ]
        
        with col1:
            order_selection = st.selectbox("Cars for Sale:",
                                         ["Select a Car"] + car_names,
                                         help="Select an item from the drop down menu",
                                         key="order_select")

            available_colors = self.business_service.get_available_colors(order_selection)
            color_options = ["Select a Color"] + available_colors
            selected_color = st.selectbox("Color:", color_options, key="order_color")
            order_quantity = st.number_input("Quantity:", step=1, min_value=1, key="order_qty")
            order_name = self.get_current_user_name()
            st.text_input("Name:", value=order_name, key="cust_name", disabled=True)
            order_btn = st.button("Place Order", disabled=False, use_container_width=True, type="primary")
            
            if order_btn:
                if order_selection == "Select a Car":
                    st.warning("Please select a car.")
                elif selected_color == "Select a Color":
                    st.warning("Please select a color.")
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
                        "customer_email": st.session_state["user"]["email"],
                        "color": selected_color
                    }
                    success, result = self.business_service.place_order(order_data)
                    
                    if success:
                        st.success("Order Placed Successfully!")
                        # Store order details for summary
                        st.session_state["last_order"] = result
                        st.session_state["last_order_total"] = result["Total"]
                    else:
                        st.error(result.get("error", "Failed to place order"))

        with col2:
            if "last_order" in st.session_state and order_btn:
                with st.container(border=True):
                    st.markdown("### Order Summary")
                    st.divider()

                    st.markdown(f"**Car:** {st.session_state['last_order']['Item']}")
                    st.markdown(f"**Color:** {st.session_state['last_order'].get('Color')}")
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
                    # Check for 'product' regardless of capitalization
                is_product = item.get("type", "").lower() == "product"
    
                if is_product:
                    colors_list = item.get("colors", [])
                    color_display = f" | Colors: {', '.join(colors_list)}" if colors_list else ""
        
                    if item["stock"] < threshold:
                            st.markdown(f"**{item['name']}** | Price: ${item['price']} | Stock: {item['stock']}{color_display} | **LOW STOCK!**")
                    else:
                        st.markdown(f"{item['name']} | Price: ${item['price']} | Stock: {item['stock']}{color_display}")
                else:
                    # This handles WIP parts like Wheels, Engines, etc.
                    st.markdown(f"{item['name']} | Stock: {item['stock']} (WIP Part)")

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
                
                available_colors = []
                if car_assemble_selection != "Select a Car":
                    available_colors = self.business_service.get_available_colors(car_assemble_selection)
        
                color_options = ["Select a Color"] + available_colors
                selected_assemble_color = st.selectbox("Assembly Color:", color_options, key="assemble_color")

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
        active_orders = [
            order for order in orders
            if order.get("Status", "Placed") == "Placed"
        ]

        if not active_orders:
            st.info("No orders currently in the system.")
        else:
            for index, order in enumerate(active_orders):
                with st.container(border=True):
                    col_info, col_action = st.columns([3, 1])
                    
                    with col_info:
                        st.markdown(f"**Order ID:** {order['Order_ID']} | **Customer:** {order['Customer']}")
                        color_text = f" | **Color:** {order.get('Color')}" if order.get("Color") else ""
                        st.markdown(
                            f"**Item:** {order['Item']}{color_text} | "
                            f"**Qty:** {order['Quantity']} | **Total:** ${order['Total']}"
                        )
                        status = order.get("Status", "Placed")
                        st.markdown(f"**Status:** {self.format_order_status(status)}")
                    
                    with col_action:
                        if st.button(f"Mark Shipped", key=f"ship_{index}", use_container_width=True):
                            success = self.business_service.update_order_status(order['Order_ID'], "Shipped")
                            if success:
                                st.success("Order updated!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Failed to update order.")

    def render_delete_order_tab(self) -> None:
        """
        Render order deletion interface.
        """
        st.subheader("Delete Orders")
        st.info("Deleting an order marks it as Deleted while keeping the order record.")

        orders = self.data_manager.load_orders()

        if not orders:
            st.info("No orders found to delete.")
        else:
            for index, order in enumerate(orders):
                with st.container(border=True):
                    col_text, col_delete = st.columns([3, 1])
                    
                    with col_text:
                        st.write(f"**{order['Order_ID']}** - {order['Customer']}")
                        color_text = f" | Color: {order.get('Color')}" if order.get("Color") else ""
                        st.caption(f"{order['Item']}{color_text} | Qty: {order['Quantity']}")
                        st.markdown(f"**Status:** {self.format_order_status(order.get('Status', 'Placed'))}")
                    
                    with col_delete:
                        status = order.get("Status", "Placed")
                        if status in {"Shipped", "Completed"}:
                            st.write("Cannot delete completed orders")
                        elif status == "Deleted":
                            st.write("Already deleted")
                        else:
                            confirm_check = st.checkbox(f"Confirm delete {order['Order_ID']}", key=f"conf_{index}")
                            if confirm_check:
                                if st.button("Mark Deleted", key=f"del_{index}", type="primary", use_container_width=True):
                                    success, message = self.business_service.soft_delete_order(order['Order_ID'])
                                    if success:
                                        st.success(message)
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error(message)

    def render_ai_assistant_tab(self) -> None:
        """
        Render AI assistant chat for app-specific questions.
        """
        st.subheader("AI Assistant")

        if "ai_messages" not in st.session_state:
            st.session_state["ai_messages"] = [
                {
                    "role": "assistant",
                    "content": "Hi, ask me a question about inventory, orders, vehicles, or using the app.",
                }
            ]

        for message in st.session_state["ai_messages"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        user_question = st.chat_input("Ask the HEV assistant")

        if user_question:
            st.session_state["ai_messages"].append(
                {
                    "role": "user",
                    "content": user_question,
                }
            )

            with st.chat_message("user"):
                st.markdown(user_question)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        assistant = AIChatAssistant()
                        response = assistant.generate_response(
                            user_question,
                            self.build_ai_app_context(),
                        )
                        st.markdown(response)
                    except RuntimeError as error:
                        response = str(error)
                        st.error(response)
                    except Exception as error:
                        response = f"AI assistant request failed: {error}"
                        st.error(response)

            st.session_state["ai_messages"].append(
                {
                    "role": "assistant",
                    "content": response,
                }
            )

        if st.button("Clear AI chat", use_container_width=True):
            st.session_state["ai_messages"] = [
                {
                    "role": "assistant",
                    "content": "Hi, ask me a question about inventory, orders, vehicles, or using the app.",
                }
            ]
            st.rerun()

    def build_ai_app_context(self) -> Dict[str, Any]:
        """
        Build a role-aware context snapshot for the AI assistant.
        """
        user = st.session_state.get("user") or {}
        role = st.session_state.get("role")
        email = user.get("email")
        orders = self.data_manager.load_orders()

        if role == "Customer":
            orders = [
                order for order in orders
                if order.get("Customer Email") == email
            ]

        return {
            "current_user": {
                "email": email,
                "role": role,
            },
            "inventory": self.data_manager.load_inventory(),
            "orders": orders,
        }
