import streamlit as st

# MUST be the very first Streamlit command in the script
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Initialize universal navigation parameters if missing
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "listings"

# FIXED: Using the native st.user object properties
if not st.user.is_logged_in:
    st.session_state["authenticated"] = False
    
    # Import and render your customized login screen layout
    from views.login import render_login
    render_login()
    
    # FORCE STREAMLIT TO HALT HERE UNTIL THEY CLICK LOG IN
    st.stop() 
else:
    # Google account authenticated successfully! Forward to your dashboard
    st.session_state["authenticated"] = True
    st.session_state["user_info"] = st.user
    
    from views.dashboard import render_dashboard
    render_dashboard()
