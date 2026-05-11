"""
Main Application Entry Point - Combines Data, Service, and UI layers
Streamlit app orchestrator for the Inventory Manager application
"""

import streamlit as st
from pathlib import Path
from Data.data import DataManager
from Service.service import BusinessService
from UI.ui import UIManager


def main():
    """
    Main application orchestrator that combines all three layers
    """
    # Initialize Streamlit page configuration
    st.set_page_config(page_title="Inventory Manager", layout="centered")
    st.title("Horizon Electric Vehicles")
    st.divider()

    # Initialize session state variables
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if "user" not in st.session_state:
        st.session_state["user"] = None

    if "role" not in st.session_state:
        st.session_state["role"] = None
        
    if "page" not in st.session_state:
        st.session_state["page"] = "login"

    # Get the parent directory where data files are stored
    data_dir = Path(__file__).parent.parent
    
    # Initialize data layer - passing the parent directory for data file access
    data_manager = DataManager(data_dir=str(data_dir))
    
    # Initialize service layer with data manager
    business_service = BusinessService(data_manager)
    
    # Initialize UI layer with business service and data manager
    ui_manager = UIManager(business_service, data_manager)
    
    # Initialize the app
    ui_manager.initialize_session()
    
    # Route to appropriate page based on user role and login status
    if not st.session_state["logged_in"]:
        # Show login page
        ui_manager.render_login_page()
    
    elif st.session_state["role"] == "Manager":
        # Show manager dashboard
        ui_manager.render_manager_dashboard()
    
    elif st.session_state["role"] == "Customer":
        # Show customer dashboard
        ui_manager.render_customer_dashboard()


if __name__ == "__main__":
    main()
