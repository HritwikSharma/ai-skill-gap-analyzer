import streamlit as st

# Must be the very first Streamlit command called
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Initialize session state for your view tracking if not present
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "listings"

# Streamlit native auth engine mapping check
if not st.experimental_user.get("is_logged_in", False):
    # User is not logged in through Google yet -> show login screen
    st.session_state["authenticated"] = False
    
    # Import and run your view logic directly as a module
    from views.login import render_login
    render_login()
else:
    # Google Auth success! Mark state true and forward traffic
    st.session_state["authenticated"] = True
    st.session_state["user_info"] = st.experimental_user
    
    # Import and run your dashboard view directly as a module
    from views.dashboard import render_dashboard
    render_dashboard()
