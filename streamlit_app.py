import streamlit as st

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Initialize state management variables
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_info" not in st.session_state:
    st.session_state["user_info"] = None

# --- FIREWALL GUARD ROUTING ---
if not st.session_state["authenticated"]:
    from views.login import render_login
    render_login()
    st.stop()

# --- ACCESSIBLE DASHBOARD HOME ---
from views.dashboard import render_dashboard
render_dashboard()
