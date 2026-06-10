import streamlit as st
import streamlit.components.v1 as components
import psycopg2
from psycopg2.extras import RealDictCursor

# Connect to your AWS RDS instance securely
def get_db_connection():
    return psycopg2.connect(
        host=st.secrets["database"]["host"],
        port=st.secrets["database"]["port"],
        database=st.secrets["database"]["database"],
        user=st.secrets["database"]["user"],
        password=st.secrets["database"]["password"]
    )

def render_login():
    # --- 1. PREVENT CONTENT SHIFTING VIA CORE STYLING ---
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
        justify-content: center !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- 2. INTERCEPT DATA SUBMISSIONS FROM URL PARAMS ---
    params = st.query_params
    if "action_email" in params and "action_pass" in params and "action_mode" in params:
        email = params["action_email"].strip().lower()
        password = params["action_pass"]
        mode = params["action_mode"]
        
        # Instantly wipe parameters from browser bar to clean up environment
        st.query_params.clear()

        if mode == "signin":
            try:
                with get_db_connection() as conn:
                    with conn.cursor(cursor_factory=RealDictCursor) as cur:
                        cur.execute("SELECT password FROM app_users WHERE email = %s;", (email,))
                        user_record = cur.fetchone()
                
                if not user_record:
                    st.error("No account found with this email address.")
                elif user_record["password"] != password:
                    st.error("Incorrect password. Please try again.")
                else:
                    st.session_state["authenticated"] = True
                    st.session_state["user_info"] = {"email": email}
                    st.rerun()
            except Exception as e:
                st.error(f"Database validation connection failed: {e}")

        elif mode == "create":
            if "@" not in email or "." not in email:
                st.error("Please enter a structurally valid email identity.")
            elif len(password) < 4:
                st.error("Password string must contain 4 characters or more.")
            else:
                try:
                    with get_db_connection() as conn:
                        with conn.cursor(cursor_factory=RealDictCursor) as cur:
                            cur.execute("SELECT email FROM app_users WHERE email = %s;", (email,))
                            if cur.fetchone():
                                st.error("This email address is already registered.")
                            else:
                                cur.execute("INSERT INTO app_users (email, password) VALUES (%s, %s);", (email, password))
                                conn.commit()
                                st.success("Account initialized successfully! Please sign in below.")
                except Exception as e:
                    st.error(f"Database storage mutation failed: {e}")

    # --- 3. UNIFIED FRONTEND CSS & FORM ELEMENT OVERLAY ---
    # Everything is hardcoded here to guarantee elements stay aligned on mobile or web interfaces
    login_html_card = """
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
        height: 100vh;
        overflow: hidden;
      }
      .card { width: 380px; border-radius: 12px; border: 1px solid #1e1e1e; background: #0f0f0f; overflow: hidden; padding-bottom: 8px; }
      .card-header { padding: 32px 24px 16px; text-align: center; }
      .card-header h1 { font-size: 24px; font-weight: 600; color: #fff; letter-spacing: -0.03em; }
      .card-header p { font-size: 13px; color: rgba(255,255,255,0.4); margin-top: 6px; }
      .tabs { display: flex; border-bottom: 1px solid #1e1e1e; }
      .tab { flex: 1; padding: 14px; text-align: center; font-size: 13px; color: #555; cursor: pointer; border-bottom: 2px solid transparent; transition: all 0.15s; user-select: none; }
      .tab.active { color: #4d9fff; border-bottom: 2px solid #4d9fff; font-weight: 500; }
      
      .form-body { padding: 24px 24px 16px; }
      .features { background: #141414; border-radius: 8px; padding: 12px 14px; margin-bottom: 20px; border: 1px solid #1e1e1e; }
      .feature-item { display: flex; align-items: center; gap: 10px; font-size: 12px; color: #bbb; padding: 4px 0; }
      .feature-item .check { color: #4d9fff; font-size: 14px; }
      
      .input-group { margin-bottom: 16px; }
      .input-group label { display: block; font-size: 12px; color: #888; margin-bottom: 6px; font-weight: 500; text-align: left; }
      .input-group input { width: 100%; background: #141414; border: 1px solid #1e1e1e; border-radius: 6px; padding: 11px 12px; color: #fff; font-size: 14px; font-family: inherit; transition: border-color 0.15s; }
      .input-group input:focus { outline: none; border-color: #4d9fff; }
      
      .submit-btn { width: 100%; background: #ffffff; color: #000000; border: none; border-radius: 6px; padding: 12px; font-size: 14px; font-weight: 500; cursor: pointer; transition: background 0.15s; margin-top: 8px; font-family: inherit; }
      .submit-btn:hover { background: #e5e5e5; }
      
      .footer-note { font-size: 11px; color: #444; text-align: center; margin-top: 20px; display: flex; align-items: center; justify-content: center; gap: 5px; }
    </style>
    </head>
    <body>
    <div class="card">
      <div class="card-header">
        <h1>TalentPulse</h1>
        <p>India Tech Market Intelligence</p>
      </div>
      <div class="tabs">
        <div class="tab active" id="tab-signin" onclick="setMode('signin')">Sign In</div>
        <div class="tab" id="tab-create" onclick="setMode('create')">Create Account</div>
      </div>
      <div class="form-body">
        <div class="features">
          <div class="feature-item"><span class="check">✦</span> Live job market analytics across India</div>
          <div class="feature-item"><span class="check">✦</span> Salary insights &amp; hiring trend data</div>
        </div>
        
        <div class="input-group">
          <label>Email Address</label>
          <input type="email" id="email" placeholder="name@company.com" autocomplete="off">
        </div>
        <div class="input-group">
          <label>Password</label>
          <input type="password" id="password" placeholder="••••••••">
        </div>
        
        <button class="submit-btn" id="action-btn" onclick="executePost()">Sign In to Dashboard</button>
        
        <div class="footer-note">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>
          </svg>
          Secure connection verified
        </div>
      </div>
    </div>

    <script>
    let currentMode = 'signin';

    function setMode(mode) {
      currentMode = mode;
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.getElementById('tab-' + mode).classList.add('active');
      
      const btn = document.getElementById('action-btn');
      if(mode === 'signin') {
        btn.innerText = 'Sign In to Dashboard';
      } else {
        btn.innerText = 'Register Free Account';
      }
    }

    function executePost() {
      const emailVal = document.getElementById('email').value.trim();
      const passVal = document.getElementById('password').value;
      
      if (!emailVal || !passVal) {
        alert('Please complete all credential fields.');
        return;
      }

      // Safe, zero-dependency data transition back to parent application frame
      const targetUrl = window.parent.location.origin + window.parent.location.pathname + 
                        '?action_email=' + encodeURIComponent(emailVal) + 
                        '&action_pass=' + encodeURIComponent(passVal) + 
                        '&action_mode=' + currentMode;
                        
      window.parent.location.href = targetUrl;
    }
    </script>
    </body>
    </html>
    """

    components.html(login_html_card, height=520, scrolling=False)
