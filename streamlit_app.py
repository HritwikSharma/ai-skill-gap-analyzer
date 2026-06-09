import streamlit as st

st.set_page_config(
    page_title="TalentPulse",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Auth gate ──
if not st.user.is_logged_in:
    st.markdown("""
    <style>
    html, body, .stApp { background: #0f0f0f !important; }
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("## TalentPulse")
        st.caption("India Tech Market Intelligence")
        st.divider()
        if st.button("Continue with Google", use_container_width=True):
            st.login()
    st.stop()

# ── Logged in — show dashboard ──
# Sign out button
with st.sidebar:
    st.markdown(f"**{st.user.name}**")
    st.caption(st.user.email)
    st.divider()
    if st.button("Sign out", use_container_width=True):
        st.logout()

# Import and run dashboard content
exec(open("views/dashboard.py").read())
