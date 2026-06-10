import streamlit as st
import json
import os

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

DB_FILE = "users.json"

# Helper function to read the user accounts database
def load_users():
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

# Initialize session state variables
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_info" not in st.session_state:
    st.session_state["user_info"] = None
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "listings"

# --- FIREWALL GUARD ROUTING ---
if not st.session_state["authenticated"]:
    from views.login import render_login
    render_login()
    st.stop() # Stops execution so unauthenticated users cannot see the dashboard

# --- DASHBOARD RENDERING (Only runs if authenticated is True) ---
from views.dashboard import render_dashboard
render_dashboard()
