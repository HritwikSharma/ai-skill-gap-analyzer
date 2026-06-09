import streamlit as st
from httpx_oauth.clients.google import GoogleOAuth2
import asyncio

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Read your existing credentials directly from Streamlit secrets
CLIENT_ID = st.secrets["auth"]["client_id"]
CLIENT_SECRET = st.secrets["auth"]["client_secret"]
REDIRECT_URI = st.secrets["auth"]["redirect_uri"]

client = GoogleOAuth2(CLIENT_ID, CLIENT_SECRET)

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Handle incoming redirects after clicking "Sign in"
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
        st.error(f"Authentication failed: {e}")

# Page routing firewall
if not st.session_state["authenticated"]:
    # Generate the Google Link
    async def get_url():
        return await client.get_authorization_url(REDIRECT_URI, scope=["profile", "email"])
    google_login_url = asyncio.run(get_url())
    
    # Pass the link directly into your custom login page layout
    from views.login import render_login
    render_login(google_login_url)  # This matches the function definition exactly!
    st.stop()

# Load dashboard on successful validation
from views.dashboard import render_dashboard
render_dashboard()
