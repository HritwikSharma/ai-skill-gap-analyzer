import streamlit as st
from httpx_oauth.clients.google import GoogleOAuth2
import asyncio

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 1. Pull secret environments
CLIENT_ID = st.secrets["auth"]["client_id"]
CLIENT_SECRET = st.secrets["auth"]["client_secret"]
REDIRECT_URI = st.secrets["auth"]["redirect_uri"]

client = GoogleOAuth2(CLIENT_ID, CLIENT_SECRET)

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# 2. Extract authorization redirects seamlessly from browser query strings
query_params = st.query_params
if "code" in query_params and not st.session_state["authenticated"]:
    try:
        code = query_params["code"]
        token = asyncio.run(client.get_access_token(code, REDIRECT_URI))
        user_id, user_email = asyncio.run(client.get_id_email(token["access_token"]))
        
        st.session_state["authenticated"] = True
        st.session_state["user_info"] = {"email": user_email}
        st.query_params.clear()
        st.rerun()
    except Exception as e:
        st.error(f"Authentication token mismatch or expired: {e}")

# 3. Secure Core Page Verification Checks
if not st.session_state["authenticated"]:
    from views.login import render_login
    render_login() # Look! Clean, parameter-free call back again!
    st.stop()

# --- Post-authentication landing block dashboard environment ---
from views.dashboard import render_dashboard
render_dashboard()
