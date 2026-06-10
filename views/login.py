import streamlit as st
import json
import os

DB_FILE = "users.json"

# Helper functions to handle the local JSON credential database
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

def render_login(): # Notice: No parameters inside parentheses!
    
    # --- KEEPING YOUR EXACT DARK GRAPHIC CSS STYLING ---
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
    </style>
    """, unsafe_allow_html=True)
    
    # --- KEEPING YOUR INTERACTIVE UI HEADER AND TABS EXACTLY AS PREVIOUSLY PROVIDED ---
    st.components.v1.html("""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      body {
        font-family: 'Inter', sans-serif;
        background: #0f0f0f;
        display: flex;
        align-items: center;
        justify-content: center;
        padding-top: 0px;
      }
      .card { width: 420px; border-radius: 0; overflow: hidden; border: none; box-shadow: none; }
      .card-header { background: #0f0f0f; padding: 32px 28px 16px; text-align: center; }
      .card-header h1 { font-size: 22px; font-weight: 600; color: #fff; letter-spacing: -0.03em; }
      .card-header p { font-size: 13px; color: rgba(255,255,255,0.4); margin-top: 6px; }
      .card-body { background: #0f0f0f; }
      .tabs { display: flex; border-bottom: 1px solid #1e1e1e; }
      .tab { flex: 1; padding: 14px; text-align: center; font-size: 14px; color: #555; cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -1px; transition: color 0.15s, border-color 0.15s; user-select: none; }
      .tab.active { color: #4d9fff; border-bottom: 2px solid #4d9fff; font-weight: 500; }
      .panel { display: none; padding: 28px 28px 20px; }
      .panel.active { display: block; }
      .panel p.subtitle { font-size: 14px; color: #666; margin-bottom: 12px; line-height: 1.5; }
      .features { background: #141414; border-radius: 10px; padding: 16px 18px; margin-bottom: 16px; border: 1px solid #1e1e1e; }
      .feature-item { display: flex; align-items: center; gap: 10px; font-size: 13px; color: #bbb; padding: 5px 0; }
      .feature-item .check { color: #4d9fff; font-size: 15px; flex-shrink: 0; }
      .footer-note { font-size: 11px; color: #333; text-align: center; padding: 4px 28px 16px; display: flex; align-items: center; justify-content: center; gap: 5px; }
    </style>
    </head>
    <body>
    <div class="card">
      <div class="card-header">
        <h1>TalentPulse</h1>
        <p>India Tech Market Intelligence</p>
      </div>
      <div class="card-body">
        <div class="tabs">
          <div class="tab active" id="tab-signin" onclick="switchTab('signin')">Sign in</div>
          <div class="tab" id="tab-create" onclick="switchTab('create')">Create account</div>
        </div>
        <div class="panel active" id="panel-signin">
          <div class="features">
            <div class="feature-item"><span class="check">✦</span> Live job market analytics across India</div>
            <div class="feature-item"><span class="check">✦</span> Salary insights &amp; hiring trend data</div>
            <div class="feature-item"><span class="check">✦</span> Skill gap analysis powered by AI</div>
          </div>
          <p class="subtitle">Welcome back. Sign in to access your dashboard.</p>
        </div>
        <div class="panel" id="panel-create">
          <div class="features">
            <div class="feature-item"><span class="check">✦</span> Live job market analytics across India</div>
            <div class="feature-item"><span class="check">✦</span> Salary insights &amp; hiring trend data</div>
            <div class="feature-item"><span class="check">✦</span> Skill gap analysis powered by AI</div>
          </div>
          <p class="subtitle">Create your free account — no password needed.</p>
        </div>
      </div>
    </div>
    <script>
    function switchTab(tab) {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
      document.getElementById('tab-' + tab).classList.add('active');
      document.getElementById('panel-' + tab).classList.add('active');
    }
    </script>
    </body>
    </html>
    """, height=380, scrolling=False)

    # --- NEW LOCAL FORM PROCESSING LAYOUT ---
    users = load_users()
    
    # Render clean actions right under the card
    tab_choice = st.radio(
        "Action Selector", 
        ["Sign In", "Create Account"], 
        horizontal=True, 
        label_visibility="collapsed"
    )
    
    # Match the widths precisely to your UI panel wrapper
    st.markdown('<style>div[data-testid="stTextInput"] { width: 364px !important; }</style>', unsafe_allow_html=True)
    
    email = st.text_input("Email Address", placeholder="name@company.com")
    password = st.text_input("Password", type="password", placeholder="••••••••")

    st.markdown("<br>", unsafe_allow_html=True)

    if tab_choice == "Sign In":
        if st.button("Sign In to Dashboard", use_container_width=False):
            if not email or not password:
                st.error("Please fill out all fields.")
            elif email not in users:
                st.error("No account found with this email.")
            elif users[email] != password:
                st.error("Incorrect password. Please try again.")
            else:
                st.session_state["authenticated"] = True
                st.session_state["user_info"] = {"email": email}
                st.success("Access Granted! Loading your dashboard...")
                st.rerun()

    elif tab_choice == "Create Account":
        if st.button("Register Free Account", use_container_width=False):
            if not email or not password:
                st.error("Please fill out all fields.")
            elif "@" not in email or "." not in email:
                st.error("Please provide a valid email address.")
            elif len(password) < 4:
                st.error("Password must be at least 4 characters long.")
            elif email in users:
                st.error("This email is already registered. Switch to Sign In.")
            else:
                users[email] = password
                save_users(users)
                st.success("Account created successfully! Toggle to Sign In to enter.")
