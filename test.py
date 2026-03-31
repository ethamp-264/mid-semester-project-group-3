import streamlit as st
import json
from pathlib import Path
import uuid
import time

# Paths for JSON files
json_users = Path("users.json")
json_inv = Path("inventory.json")

# Load inventory
if json_inv.exists():
    with open(json_inv, "r") as f:
        inventory = json.load(f)
else:
    inventory = []

# Load users if file exists
if json_users.exists():
    with open(json_users, "r") as f:
        users = json.load(f)
else:
    users = [
        {"id": "1", "email": "admin@HEV.com", "password": "123", "role": "Admin"}
    ]

# Streamlit page config
st.set_page_config(page_title="Inventory Manager", layout="centered")

# Title
st.title("Horizon Electric Vehicles")
st.divider()

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None
if "role" not in st.session_state:
    st.session_state["role"] = None
if "page" not in st.session_state:
    st.session_state["page"] = "login"

# Manager Dashboard
if st.session_state["role"] == "Manager":
    if st.session_state["page"] == "home":
        st.markdown("Manager Dashboard")
        if st.button("Go to Dashboard"):
            st.session_state["page"] = "dashboard"
            st.rerun()

    elif st.session_state["page"] == "dashboard":
        st.markdown("Dashboard")
        st.markdown("Inventory and other management features can go here.")

# Customer Dashboard
elif st.session_state["role"] == "Customer":
    st.markdown("Customer Dashboard")
    if st.button("Log out"):
        with st.spinner("Logging out..."):
            st.session_state["logged_in"] = False
            st.session_state["user"] = None
            st.session_state["role"] = None
            st.session_state["page"] = "login"
            time.sleep(1)
            st.rerun()

# Login / Registration
else:
    st.subheader("Log In")
    with st.container():
        email_input = st.text_input("Email", key="email_login")
        password_input = st.text_input("Password", type="password", key="password_login")
        if st.button("Log In"):
            with st.spinner("Logging in..."):
                time.sleep(1)
                found_user = next(
                    (u for u in users if u["email"].lower() == email_input.lower() and u["password"] == password_input),
                    None
                )
                if found_user:
                    st.success(f"Welcome back, {found_user['email']}!")
                    st.session_state["logged_in"] = True
                    st.session_state["user"] = found_user
                    st.session_state["role"] = found_user["role"]
                    st.session_state["page"] = "home"
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    st.subheader("New Account")
    with st.container():
        new_email = st.text_input("Email", key = "email_register")
        new_password = st.text_input("Password", type = "password", key = "password_register")
        if st.button("Create Account", key = "register_btn"):
            with st.spinner("Creating account..."):
                time.sleep(1)
                new_user = {
                    "id": str(uuid.uuid4()),
                    "email": new_email,
                    "password": new_password,
                    "role": "Instructor"
                }
                users.append(new_user)
                with open(json_users, "w", encoding="utf-8") as f:
                    json.dump(users, f, indent=4)
                st.success("Account created!")
                st.rerun()

    st.write("---")
    st.dataframe(users)

# Sidebar
with st.sidebar:
    st.markdown("Inventory Manager Sidebar")
    if st.session_state["logged_in"] and st.session_state["user"]:
        user = st.session_state["user"]
        st.markdown(f"Logged User Email: {user['email']}")
        st.markdown("Inventory List:")
        st.dataframe(inventory)
