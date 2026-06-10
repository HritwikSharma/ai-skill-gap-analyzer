import streamlit as st

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Initialize session state tracking variables
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_info" not in st.session_state:
    st.session_state["user_info"] = None

# --- APP GATE FIREWALL ---
if not st.session_state["authenticated"]:
    from views.login import render_login
    render_login()
    st.stop() 

# --- DASHBOARD ACCESSIBILITY ---
from views.dashboard import render_dashboard
render_dashboard()
