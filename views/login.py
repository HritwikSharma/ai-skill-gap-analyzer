import streamlit as st
import json
import os

DB_FILE = "users.json"

def load_users():
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users_dict):
    with open(DB_FILE, "w") as f:
        json.dump(users_dict, f, indent=4)

def render_login():
    # --- 1. DARK MINIMALIST GLOBAL STYLING ---
    st.markdown("""
    <style>
    html, body, .stApp, [data-testid="stAppViewContainer"],
    [data-testid="stMain"], .block-container {
        background: #0f0f0f !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    
    .stMainBlockContainer,
    [data-testid="stVerticalBlockBorderWrapper"],
    [data-testid="stVerticalBlock"] {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
    }
    
    /* Center the central card wrapper */
    .login-wrapper {
        width: 400px;
        margin-top: 60px;
        font-family: 'Inter', sans-serif;
    }
    .app-title {
        font-size: 26px;
        font-weight: 600;
        color: #ffffff;
        text-align: center;
        margin-bottom: 4px;
        letter-spacing: -0.03em;
    }
    .app-subtitle {
        font-size: 13px;
        color: rgba(255, 255, 255, 0.4);
        text-align: center;
        margin-bottom: 24px;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- 2. HEADER BRANDING ---
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="app-title">TalentPulse</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">India Tech Market Intelligence</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- 3. INTERACTIVE TAB SELECTOR ---
    # We use native Streamlit columns styled cleanly to behave like toggle tabs
    tab_choice = st.radio(
        "Select Action", 
        ["Sign In", "Create Account"], 
        horizontal=True, 
        label_visibility="collapsed"
    )

    # --- 4. FORM FIELDS AND INTERACTIVE LOGIC ---
    users = load_users()
    
    # Form Container Card
    with st.container():
        st.markdown("""
            <style>
            div[data-testid="stVerticalBlock"] > div:has(input) {
                width: 360px !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        email = st.text_input("Email Address", placeholder="name@company.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")

        st.markdown("<br>", unsafe_allow_html=True)

        if tab_choice == "Sign In":
            if st.button("Sign In to Dashboard", use_container_width=False):
                # Form Validation Check
                if not email or not password:
                    st.error("Please fill out all fields.")
                elif email not in users:
                    st.error("No account found with this email.")
                elif users[email] != password:
                    st.error("Incorrect password. Please try again.")
                else:
                    # Grant Access successfully!
                    st.session_state["authenticated"] = True
                    st.session_state["user_info"] = {"email": email}
                    st.success("Access Granted! Loading your dashboard...")
                    st.rerun()

        elif tab_choice == "Create Account":
            if st.button("Register Free Account", use_container_width=False):
                # Registration Validation Checks
                if not email or not password:
                    st.error("Please fill out all fields.")
                elif "@" not in email or "." not in email:
                    st.error("Please provide a valid email structure.")
                elif len(password) < 4:
                    st.error("Password must be at least 4 characters long.")
                elif email in users:
                    st.error("This email is already registered. Switch to Sign In.")
                else:
                    # Save user credentials to database dictionary
                    users[email] = password
                    save_users(users)
                    st.success("Account created successfully! You can now toggle to Sign In.")
