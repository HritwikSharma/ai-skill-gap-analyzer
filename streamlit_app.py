import streamlit as st

st.set_page_config(
    page_title="TalentPulse — India Tech Market Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

login_page     = st.Page("views/login.py",     title="Sign In",          icon="🔒")
dashboard_page = st.Page("views/dashboard.py", title="Market Analytics", icon="📊")

if not st.user.is_logged_in:
    pg = st.navigation([login_page], position="hidden")
else:
    pg = st.navigation(
        {"TalentPulse": [dashboard_page]},
        position="hidden",
    )

pg.run()
