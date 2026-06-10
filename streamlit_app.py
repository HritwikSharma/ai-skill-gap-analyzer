import streamlit as st
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_info" not in st.session_state:
    st.session_state["user_info"] = None

# Custom HTML Event Listener catch logic for clean communication
# This intercepts data sent from our custom card frame component
html_listener = """
window.addEventListener('message', function(event) {
    if (event.data && event.data.type === 'streamlit:login_submission') {
        const d = event.data.data;
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: d
        }, '*');
    }
});
"""

# Call the listener passively backgrounded
js_data = streamlit_js_eval(js_expressions=html_listener, key="login_listener")
if js_data and isinstance(js_data, dict):
    st.session_state["login_payload"] = js_data

# --- APP ROUTER FIREWALL ---
if not st.session_state["authenticated"]:
    from views.login import render_login
    render_login()
    st.stop()

# --- RUN ACTIVE DASHBOARD DASHBOARD ENV ---
from views.dashboard import render_dashboard
render_dashboard()
