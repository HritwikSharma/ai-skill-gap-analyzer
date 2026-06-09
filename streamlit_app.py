import streamlit as st

login_page     = st.Page("views/login.py",     title="Sign In",          icon="🔒")
dashboard_page = st.Page("views/dashboard.py", title="Market Analytics", icon="📊")

if not st.user.is_logged_in:
    pg = st.navigation([login_page], position="hidden")
else:
    pg = st.navigation(
        {"TalentPulse": [dashboard_page]},
        position="hidden"   # you have your own nav bar in the dashboard
    )
    with st.sidebar:
        st.markdown(f"**{st.user.name}**")
        st.caption(st.user.email)
        st.divider()
        if st.button("Log Out", use_container_width=True):
            st.logout()

pg.run()
