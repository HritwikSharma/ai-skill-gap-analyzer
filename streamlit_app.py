import streamlit as st
import json
import os

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Initialize session state variables for authentication tracking
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_info" not in st.session_state:
    st.session_state["user_info"] = None

# --- FIREWALL GUARD ROUTING ---
if not st.session_state["authenticated"]:
    from views.login import render_login
    render_login() # Call without any arguments!
    st.stop() 

# --- DASHBOARD RENDERING ---
# (This part only executes if authenticated is True)
from views.dashboard import render_dashboard
render_dashboard()
