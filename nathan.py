import streamlit as st # type: ignore
import json
from pathlib import Path
from datetime import datetime
import uuid
import time

json_users = Path("users.json")
json_inv = Path("inventory.json")

if json_inv.exists():
    with open(json_inv, "r") as f:
        inventory = json.load(f)
else:
    #Default data if file doesn't exist
    inventory = []


st.set_page_config(page_title = "Inventory Manager", layout = "centered")

if json_users.exists():
    with open(json_users, "r") as f:
        users = json.load(f)
else:
    users = [
        {
            "id": "1",
            "email": "Manager@HEV.com",
            "password": "123",
            "role": "Manager",
        },
        {   "id": "2",
            "email": "customer@HEV.com",
            "password": "456",
            "role": "Customer",
            }
    ]

st.title("Horizon Electric Vehicles")
st.divider()


if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "user" not in st.session_state:
    st.session_state["user"] = None

if "role" not in st.session_state:
    st.session_state["role"] = None

if "page" not in st.session_state:
    st.session_state["page"] = "login"


if st.session_state["role"] == "Manager":
    if st.session_state["page"] == "home":
        st.markdown("Manager Dashboard")

        tab11, tab22, tab33, tab44 = st.tabs(["Inventory", "Update Inventory", "Order Management", "Delete Order"])

        with tab11:
            with open(json_inv, "r") as f:
                inventory = json.load(f)

                st.subheader("View Inventory")

                col3, col4 = st.columns([2,3])

                with col3:
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

                        if item_exists == False:
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

        with tab22:
            pass

        with tab33:
            pass

        with tab44:
            pass




elif st.session_state['role'] == "Customer":
    st.markdown("Customer Dashboard")

    tab1, tab2, tab3 = st.tabs(["Car Information", "Place Order","Previous Orders"])

    with tab1:
            st.subheader("Available Vehicles")

            car_selection = st.selectbox("Cars for Sale:",
                                     ["Select a Car", "Sedan", "Truck", "SUV", "Van"],
                                     help = "Select an item from the drop down menu",
                                     key = "car_select")

            if car_selection:
                car = json_inv[car_selection]

                st.markdown(f"### {car_selection}")
                st.markdown(f"**Price:** ${car['price']:,}")
                st.markdown(f"**Number of Batteries:** {car['batteries']}")

                st.markdown("**Available Colors:**")
                for color in car["colors"]:
                    st.write(f"- {color}")

    with tab2:
            
            col1, col2 = st.columns([3,2])
    with col1:
            order_selection = st.selectbox("Cars for Sale:",
                                     ["Select a Car", "Sedan", "Truck", "SUV", "Van"],
                                     help = "Select an item from the drop down menu",
                                     key = "order_select")
            order_quantity = st.number_input("Quantity:", step = 1, key = "order_qty")
            order_name = st.text_input("Name:", placeholder = "Ex. John", key = "cust_name")
            order_btn = st.button("Place Order", disabled = False, use_container_width=True,type = "primary")
            if order_btn:
                if not order_name:
                    st.warning("A name for the order must be provided!")
                if order_quantity < 1:
                    st.warning("Invalid quantity!")
                else: 
                    with st.spinner("Placing Order..."):
                        time.sleep(2)
                    
                        item_search = order_selection
                        quantity = order_quantity

                        exists = False
                        in_stock = False
                        total_price = 0

                        new_order_id_number = 101
                        new_order_id = "Order_" + str(new_order_id_number)
                        new_order_id_number += 1

                        for inventory_item in inventory:
                            if inventory_item["name"] == item_search:
                                exists = True
                                if inventory_item["stock"] >= quantity:
                                    in_stock = True
                                    inventory_item["stock"] = inventory_item["stock"] - quantity
                                    total_price = inventory_item["price"] * quantity

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


    with tab3:
            pass


    





    if st.button("Log out", use_container_width = True):
        with st.spinner("Logging out..."):
            st.session_state["logged_in"] = False
            st.session_state["user"] = None
            st.session_state["role"] = None
            st.session_state["page"]= "login"
            time.sleep(4)
            st.rerun()


else:
    #Login
    st.subheader("Log In")
    with st.container(border = True):
        email_input = st.text_input("Email", key = "email_login")
        password_input = st.text_input("Password", type = "password", key = "password_login")
        
        if st.button("Log In", type = "primary", use_container_width = True):
            with st.spinner("Logging in..."):
                time.sleep(2)
                
                found_user = None
                for user in users:
                    if user["email"].strip().lower() == email_input.strip().lower() and user["password"] == password_input:
                        found_user = user
                        break
                
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

    #Registration
    st.subheader("New Account")
    with st.container(border = True):
        new_email = st.text_input("Email", key = "email_register")
        new_password = st.text_input("Password", type = "password", key = "password_edit")
        role = st.radio("Role", ["Manager", "Customer"], horizontal = True)
        
        if st.button("Create Account", key = "register_btn"):
            with st.spinner("Creating account..."):
                time.sleep(2) 

                users.append({
                    "id": str(uuid.uuid4()),
                    "email": new_email,
                    "password": new_password,
                    "role": role
                })
                
                with open(json_users, "w") as f:
                    json.dump(users, f)

                st.success("Account created!")
                st.rerun()

    st.write("---")
    st.dataframe(users)

with st.sidebar:
    st.markdown("Inventory Manager Sidebar")
    if  st.session_state["logged_in"] == True:
        user = st.session_state["user"]
        st.markdown(f"Logged User Email: {user['email']}")