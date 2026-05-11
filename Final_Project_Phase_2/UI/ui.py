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
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Stock Volume", sum(i["stock"] for i in inventory))
        m2.metric("Active Orders", len(orders))
        m3.metric("System Health", "Optimal")

        st.divider()

        tab1, tab2, tab3 = st.tabs(["Inventory", "Update Stock", "Orders"])

        with tab1:
            self.render_inventory_view()
        with tab2:
            st.info("Stock/Assembly interface can be called here.")
        with tab3:
            st.info("Order management interface can be called here.")

        if st.sidebar.button("Log out", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    def render_customer_dashboard(self) -> None:
        """
        Render the customer dashboard for ordering.
        """
        st.title("Customer Experience")
        tab1, tab2 = st.tabs(["Place Order", "History"])

        with tab1:
            self.render_order_form()
        with tab2:
            st.info("Order history can be displayed here.")

        if st.sidebar.button("Log out", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    def render_inventory_view(self) -> None:
        """
        Render inventory viewing component.
        """
        st.subheader("Inventory Status")
        inventory = self.data_manager.load_inventory()
        for item in inventory:
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 1, 1])
                c1.markdown(f"**{item['name']}**")
                c2.write(f"${item['price']}")
                c3.markdown(f":green[Stock: {item['stock']}]" if item['stock'] >= 5 else f":red[LOW: {item['stock']}]")

    def render_order_form(self) -> None:
        """
        Render order placement form.
        """
        with st.container(border=True):
            car = st.selectbox("Vehicle", ["Sedan", "Truck", "SUV", "Van"])
            qty = st.number_input("Quantity", min_value=1, step=1)
            name = st.text_input("Name")
            
            if st.button("Confirm Order", type="primary", use_container_width=True):
                order_data = {
                    "item": car, "quantity": qty, "customer_name": name,
                    "customer_email": st.session_state["user"]["email"]
                }
                success, result = self.business_service.place_order(order_data)
                if success:
                    st.toast("Order Placed!")
                else:
                    st.error("Failed to place order.")