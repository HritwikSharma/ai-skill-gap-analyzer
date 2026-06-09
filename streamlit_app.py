import streamlit as st
from httpx_oauth.clients.google import GoogleOAuth2
import asyncio

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 1. Fetch your secrets directly from your Streamlit Secrets panel
CLIENT_ID = st.secrets["auth"]["client_id"]
CLIENT_SECRET = st.secrets["auth"]["client_secret"]
REDIRECT_URI = st.secrets["auth"]["redirect_uri"]

# Initialize the public Google Client
client = GoogleOAuth2(CLIENT_ID, CLIENT_SECRET)

# Initialize application session tracking states
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "listings"

# Async helper to trade Google's code for user profile info
async def get_access_token(client, code, redirect_uri):
    token = await client.get_access_token(code, redirect_uri)
    return token

async def get_user_info(client, token):
    user_id, user_email = await client.get_id_email(token)
    return user_email

# 2. CATCH THE REDIRECT: Check if Google sent a code back in the URL bar
query_params = st.query_params
if "code" in query_params and not st.session_state["authenticated"]:
    try:
        code = query_params["code"]
        token = asyncio.run(get_access_token(client, code, REDIRECT_URI))
        user_email = asyncio.run(get_user_info(client, token["access_token"]))
        
        # Mark user as logged in successfully
        st.session_state["authenticated"] = True
        st.session_state["user_email"] = user_email
        
        # Clear the code parameter from the browser URL bar for clean look
        st.query_params.clear()
        st.rerun()
    except Exception as e:
        st.error(f"Authentication failed: {e}")

# 3. ROUTING LOGIC
if not st.session_state["authenticated"]:
    # Render your custom login page function manually
    from views.login import render_login
    render_login()
    st.stop()  # Completely safe public halt, no yellow screen!
else:
    # User is logged in! Provide email string to dashboard and load it
    st.session_state["user_info"] = {"email": st.session_state["user_email"]}
    
    from views.dashboard import render_dashboard
    render_dashboard()
