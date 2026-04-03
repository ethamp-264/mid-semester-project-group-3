import streamlit as st # type: ignore
import json
from pathlib import Path
from datetime import datetime
import uuid
import time

json_users = Path("users.json")
json_inv = Path("inventory.json")
json_orders = Path("orders.json")

if json_inv.exists():
    with open(json_inv, "r") as f:
        inventory = json.load(f)
else:
    #Default data if file doesn't exist
    inventory = []

if json_orders.exists():
    with open(json_orders, "r") as f:
        Orders = json.load(f)
else:
    #Default data if file doesn't exist
    Orders = []


st.set_page_config(page_title = "Inventory Manager", layout = "centered")

if json_users.exists():
    with open(json_users, "r") as f:
        users = json.load(f)
else:
    users = [
        {
            "id": "1",
            "email": "manager@HEV.com",
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
                    with st.container(border = True):
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
                    with st.container(border = True):
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
            col7, col8 = st.columns([1,1])

            with col7:
                with st.container(border = True):
                    st.subheader("Restock WIP")

                    restock_item = st.selectbox("Restock Options:",
                                                    ["Select an item", "Wheels", "Engine", "Battery", "Frame"],
                                                    help = "Select an item from the drop down menu to restock",
                                                    key = "restock_select")

                    restock_qty = st.number_input("Add to stock:", step = 1, min_value = 1, key = "restock_qty")

                    restock_btn = st.button("Restock Item", 
                                            key = "restock_btn", 
                                            use_container_width = True, 
                                            type = "primary")

                    if restock_btn:
                        with st.spinner("Updating Stock..."):
                                        time.sleep(2)
                        for item in inventory:
                                if item["name"] == restock_item:
                                    item["stock"] += restock_qty

                                    with json_inv.open("w", encoding = "utf-8") as f:
                                        json.dump(inventory, f)

                                        st.success("Item Restocked Successfully!")
                                        time.sleep(2) 
                                        st.rerun()

            with col8:
                with st.container(border = True):
                    st.subheader("Restock Cars")

                    car_assemble_selection = st.selectbox("Cars for Assembly:",
                                     ["Select a Car", "Sedan", "Truck", "SUV", "Van"],
                                     key = "assemble_select")
                    
                    assemble_qty = st.number_input("Quantity to Assemble:", 
                                                   step = 1, 
                                                   min_value = 1, 
                                                   key = "assemble_qty")
                    
                    assemble_btn = st.button("Assemble Cars", 
                                            key = "assemble_btn", 
                                            use_container_width = True, 
                                            type = "primary")

                    if assemble_btn:
                        if car_assemble_selection == "Select a Car":
                            st.warning("Please select a valid car to assemble.")
                        else:
                            with st.spinner("Assembling car..."):
                                time.sleep(2)
                                

                                car_item = None
                                for item in inventory:
                                    if item["name"] == car_assemble_selection:
                                        car_item = item
                                

                                wheels_needed = 0
                                if "wheels" in car_item:
                                    wheels_needed = car_item["wheels"]
                                    
                                engine_needed = 0
                                if "engine" in car_item:
                                    engine_needed = car_item["engine"]
                                    
                                battery_needed = 0
                                if "batteries" in car_item:
                                    battery_needed = car_item["batteries"]
                                    
                                frame_needed = 0
                                if "frame" in car_item:
                                    frame_needed = car_item["frame"]
                                    
                                
                                total_wheels_needed = wheels_needed * assemble_qty
                                total_engine_needed = engine_needed * assemble_qty
                                total_battery_needed = battery_needed * assemble_qty
                                total_frame_needed = frame_needed * assemble_qty
                                
                                
                                wheels_in_stock = 0
                                engine_in_stock = 0
                                battery_in_stock = 0
                                frame_in_stock = 0
                                
                                for item in inventory:
                                    if item["name"] == "Wheels":
                                        wheels_in_stock = item["stock"]
                                    if item["name"] == "Engine":
                                        engine_in_stock = item["stock"]
                                    if item["name"] == "Battery":
                                        battery_in_stock = item["stock"]
                                    if item["name"] == "Frame":
                                        frame_in_stock = item["stock"]
                                
                                
                                have_enough_parts = True
                                
                                if wheels_in_stock < total_wheels_needed:
                                    have_enough_parts = False
                                    st.error("Assembly Failed: Not enough Wheels!")
                                    
                                if engine_in_stock < total_engine_needed:
                                    have_enough_parts = False
                                    st.error("Assembly Failed: Not enough Engines!")
                                    
                                if battery_in_stock < total_battery_needed:
                                    have_enough_parts = False
                                    st.error("Assembly Failed: Not enough Batteries!")
                                    
                                if frame_in_stock < total_frame_needed:
                                    have_enough_parts = False
                                    st.error("Assembly Failed: Not enough Frames!")
                                
                                
                                if have_enough_parts == True:
                                    for item in inventory:
                                        if item["name"] == "Wheels":
                                            item["stock"] = item["stock"] - total_wheels_needed
                                        if item["name"] == "Engine":
                                            item["stock"] = item["stock"] - total_engine_needed
                                        if item["name"] == "Battery":
                                            item["stock"] = item["stock"] - total_battery_needed
                                        if item["name"] == "Frame":
                                            item["stock"] = item["stock"] - total_frame_needed
                                        
                                       
                                        if item["name"] == car_assemble_selection:
                                            item["stock"] = item["stock"] + assemble_qty
                                            
                                   
                                    with json_inv.open("w", encoding = "utf-8") as f:
                                        json.dump(inventory, f)
                                        
                                    st.success(f"Successfully assembled!")
                                    time.sleep(2)
                                    st.rerun()
                    
            
        if st.button("Log out", type = "primary", use_container_width = True, key = "restock_logout"):
                        with st.spinner("Logging out..."):
                            st.session_state["logged_in"] = False
                            st.session_state["user"] = None
                            st.session_state["role"] = None
                            st.session_state["page"]= "login"
                            time.sleep(2)
                            st.rerun()


        with tab33:
            pass

        with tab44:
            pass



elif st.session_state['role'] == "Customer":
    st.markdown("Customer Dashboard")

    tab1, tab2, tab3 = st.tabs(["Car Information", "Place Order","Previous Orders"])

    with tab1:
        st.subheader("Car Information")
        with st.container(border = True):

            car_names = []

            for item in inventory:
                if item["type"] == "Product":
                    car_names.append(item["name"])

            selected_car = st.selectbox("Select a Car",
                car_names,
                key = "car_info_select"
            )

            for item in inventory:
                if item["name"] == selected_car:
                    col5, col6 = st.columns([2,1])

                    with col5:
                        st.markdown(f"### {item['name']}")
                        st.markdown(f"**Price:** ${item['price']}")
                        st.markdown(f"**Stock:** {item['stock']}")
                        st.markdown(f"**Batteries:** {item['batteries']}")

                    with col6:
                        st.markdown("**Colors:**")
                        for color in item["colors"]:
                            st.markdown(f"- {color}")

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

                        if in_stock:
                            Orders.append(
                                {
                                    "Order_ID": new_order_id, 
                                    "Customer": order_name, 
                                    "Item": item_search, 
                                    "Quantity": order_quantity,
                                    "Total": total_price,
                                    "Status": "Placed" 
                                }
                            )

                            with json_orders.open("w", encoding = "utf-8") as f:
                                    json.dump(Orders, f)

                            with json_inv.open("w", encoding = "utf-8") as f:
                                    json.dump(inventory, f)


                                    st.success("Order Placed Successfully!") 
                        else:
                            print("Out of Stock")


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
        st.subheader("Previous Orders")

        if "orders" not in st.session_state or len(st.session_state["orders"]) == 0:
            st.info("No orders have been placed yet.")
        else:
            st.divider()
            order_number = 1

            for order in st.session_state["orders"]:
                with st.container(border = True):
                    st.markdown(f"### Order #{order_number}")
                    st.markdown(f"**Car:** {order['car']}")
                    st.markdown(f"**Quantity:** {order['quantity']}")
                    st.markdown(f"**Total:** ${order['total']:.2f}")
                    st.markdown(f"**Customer:** {order['customer']}")
                    
                order_number = order_number + 1


    if st.button("Log out", type = "primary", use_container_width = True, key = "previous_orders_logout"):
        with st.spinner("Logging out..."):
            st.session_state["logged_in"] = False
            st.session_state["user"] = None
            st.session_state["role"] = None
            st.session_state["page"]= "login"
            time.sleep(2)
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