import streamlit as st  # type: ignore
import json
from pathlib import Path
import uuid
import time

# --- file paths (keeping these simple for now) ---
users_file = Path("users.json")
inv_file   = Path("inventory.json")
wip_file   = Path("wip.json")
cars_file  = Path("cars.json")


# --- helpers ---
def read_json(path, default_val):
    # basic loader — nothing fancy, just gets the job done
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    return default_val  # fallback if file doesn't exist


def write_json(path, data):
    # NOTE: adding encoding explicitly (burned by this before...)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# --- data setup ---
inventory = read_json(inv_file, [])

# TODO: passwords should definitely be hashed... this is just for demo
users = read_json(users_file, [
    {"id": "1", "email": "admin@HEV.com",   "password": "123", "role": "Admin"},
    {"id": "2", "email": "manager@HEV.com", "password": "123", "role": "Manager"},
])

# initial WIP stock — numbers are kinda arbitrary
wip_materials = read_json(wip_file, [
    {"id": "wip-001", "name": "Wheels",       "quantity": 20, "unit": "units"},
    {"id": "wip-002", "name": "Transmission", "quantity": 15, "unit": "units"},
    {"id": "wip-003", "name": "Engine",       "quantity": 10, "unit": "units"},
    {"id": "wip-004", "name": "Frame",        "quantity": 30, "unit": "units"},
    {"id": "wip-005", "name": "Body",         "quantity": 25, "unit": "units"},
    {"id": "wip-006", "name": "Battery",      "quantity": 18, "unit": "units"},
])

cars = read_json(cars_file, [])

# default "bill of materials" presets
PRESETS = {
    "Truck": {"Wheels": 4, "Transmission": 1, "Engine": 1, "Frame": 1, "Body": 1, "Battery": 2},
    "Sedan": {"Wheels": 4, "Transmission": 1, "Engine": 1, "Frame": 1, "Body": 1, "Battery": 1},
    "SUV":   {"Wheels": 4, "Transmission": 1, "Engine": 1, "Frame": 1, "Body": 1, "Battery": 2},
    "Van":   {"Wheels": 4, "Transmission": 1, "Engine": 1, "Frame": 1, "Body": 1, "Battery": 1},
}


STATUS_COLORS = {
    "In Production": "#1d6fa4",
    "QA Check": "#d4820a",
    "Complete": "#1a7a4a",
    "On Hold": "#8b0000",
}


# --- streamlit setup ---
st.set_page_config(page_title="HEV — Inventory Manager", layout="wide", page_icon="⚡")

# NOTE: trimmed CSS — original was huge, might re-add later if needed
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0f1117; }
</style>
""", unsafe_allow_html=True)


# --- session state init ---
defaults = {
    "logged_in": False,
    "user": None,
    "role": None,
    "page": "login"
}

for key in defaults:
    if key not in st.session_state:
        st.session_state[key] = defaults[key]


def manager_dashboard():

    role = st.session_state.get("role")

    st.markdown(f"""
    <div>
        <h1>⚡ Horizon Electric Vehicles</h1>
        <p>{role} Dashboard</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["WIP", "Transfer", "Cars"])


    with tab1:
        # total units (doing it manually instead of sum just for clarity)
        total_units = 0
        for item in wip_materials:
            total_units += item["quantity"]

        low_stock = len([x for x in wip_materials if x["quantity"] <= 5])
        healthy   = len([x for x in wip_materials if x["quantity"] > 10])

        st.write("Total Units:", total_units)
        st.write("Low Stock:", low_stock)
        st.write("Healthy Stock:", healthy)



    with tab2:

        # NOTE: this section feels a bit messy... revisit later
        build_options = ["Create new"] + [
            f"{c['car_id']} - {c['model']}" for c in cars
        ]

        selected_build = st.selectbox("Build target", build_options)

        chosen_items = []

        for part in wip_materials:
            selected = st.checkbox(part["name"], key=f"chk_{part['id']}")

            if selected:
                qty_val = st.number_input(
                    f"{part['name']} qty",
                    min_value=1,
                    max_value=max(part["quantity"], 1),
                    value=1
                )

                chosen_items.append({
                    "id": part["id"],
                    "name": part["name"],
                    "quantity": int(qty_val),
                    "unit": part["unit"]
                })

        # confirm transfer
        if st.button("Confirm Transfer"):

            if selected_build == "Create new":
                new_id = f"HEV-{str(uuid.uuid4())[:6].upper()}"
                new_car = {
                    "car_id": new_id,
                    "model": "Unknown",  # TODO: actually capture model properly
                    "status": "In Production",
                    "materials": []
                }
                cars.append(new_car)
                target_car = new_car
            else:
                car_id = selected_build.split(" - ")[0]
                target_car = next((c for c in cars if c["car_id"] == car_id), None)

            problems = []

            for item in chosen_items:
                w = next((x for x in wip_materials if x["id"] == item["id"]), None)

                if not w:
                    problems.append(f"{item['name']} missing??")
                    continue

                if w["quantity"] < item["quantity"]:
                    problems.append(f"Not enough {item['name']}")
                    continue

                # subtract from WIP
                w["quantity"] -= item["quantity"]

                # add to car
                existing = next((m for m in target_car["materials"] if m["id"] == item["id"]), None)

                if existing:
                    existing["quantity"] += item["quantity"]
                else:
                    target_car["materials"].append(item)

            if problems:
                for p in problems:
                    st.error(p)
            else:
                write_json(wip_file, wip_materials)
                write_json(cars_file, cars)
                st.success("Transfer complete ✔")
                time.sleep(1)
                st.rerun()

    # -------- TAB 3 --------
    with tab3:

        if not cars:
            st.info("No cars in production yet...")
        else:
            for car in cars:

                if car["materials"]:
                    for m in car["materials"]:
                        st.write(f" - {m['name']}: {m['quantity']}")
                else:
                    st.write(" - no materials yet")

                # update status
                new_status = st.selectbox(
                    "Update status",
                    ["In Production", "QA Check", "Complete", "On Hold"],
                    key=f"status_{car['car_id']}"
                )

                if st.button("Save", key=f"save_{car['car_id']}"):
                    car["status"] = new_status
                    write_json(cars_file, cars)
                    st.success("Updated")
                    time.sleep(0.5)
                    st.rerun()



if st.session_state["role"] in ("Manager", "Admin"):
    manager_dashboard()

else:
    # simple login (keeping it minimal for now)
    st.title("⚡ HEV Login")

    email_input = st.text_input("Email")
    password_input = st.text_input("Password", type="password")

    if st.button("Login"):
        user = next(
            (u for u in users if u["email"] == email_input and u["password"] == password_input),
            None
        )

        if user:
            st.session_state["logged_in"] = True
            st.session_state["user"] = user
            st.session_state["role"] = user["role"]

            st.success("Logged in successfully")
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("Invalid credentials")