import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    return psycopg2.connect(
        host=st.secrets["database"]["host"],
        port=st.secrets["database"]["port"],
        database=st.secrets["database"]["database"],
        user=st.secrets["database"]["user"],
        password=st.secrets["database"]["password"]
    )

def render_login():
    # --- MODERN PREMIUM UI CSS ---
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    /* Global Background Fixes */
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background-color: #0f0f0f !important;
        font-family: 'Inter', sans-serif !important;
    }
    #MainMenu, footer, header { visibility: hidden; }
    
    /* Layout Column Padding */
    div[data-testid="stColumn"] {
        background-color: #0f0f0f;
        padding: 30px;
    }
    
    /* Header Typography */
    .title-text {
        color: #ffffff;
        font-size: 26px;
        font-weight: 600;
        text-align: center;
        letter-spacing: -0.03em;
        margin-bottom: 4px;
    }
    .subtitle-text {
        color: rgba(255, 255, 255, 0.4);
        font-size: 13px;
        text-align: center;
        margin-bottom: 32px;
    }
    
    /* Feature List Styling */
    .feature-box {
        background: #141414;
        border: 1px solid #1e1e1e;
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 24px;
    }
    .feature-item {
        color: #bbb;
        font-size: 12.5px;
        margin: 6px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .feature-spark {
        color: #4d9fff;
        font-weight: bold;
    }
    
    /* MAGIC TRICK: Turn st.radio into Premium Underlined Tabs */
    div[data-testid="stRadio"] > label {
        display: none !important; /* Hide default radio label */
    }
    div[data-testid="stRadio"] > div {
        flex-direction: row !important;
        justify-content: center !important;
        border-bottom: 1px solid #1e1e1e !important;
        gap: 0px !important;
        margin-bottom: 24px;
    }
    div[data-testid="stRadio"] label[data-testid="stWidgetLabel"] {
        display: none !important;
    }
    div[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {
        font-size: 14px !important;
        font-weight: 500 !important;
    }
    /* Hide the ugly circular radio buttons */
    div[data-testid="stRadio"] input[type="radio"] {
        display: none !important;
    }
    /* Style the clickable text items */
    div[data-testid="stRadio"] div[data-viewport="true"] label {
        flex: 1;
        padding: 12px 0px !important;
        background: transparent !important;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        color: #555555 !important;
        text-align: center;
        cursor: pointer;
        transition: color 0.2s ease, border-color 0.2s ease;
        margin: 0 !important;
    }
    /* Dynamic active tab tracking highlight line */
    div[data-testid="stRadio"] div[data-viewport="true"] label:has(input:checked) {
        color: #4d9fff !important;
        border-bottom: 2px solid #4d9fff !important;
    }
    div[data-testid="stRadio"] div[data-viewport="true"] label:hover {
        color: #888;
    }

    /* Premium Notification Alerts Override */
    div[data-testid="stNotification"] {
        background-color: #141414 !important;
        border: 1px solid #1e1e1e !important;
        border-radius: 8px !important;
    }
    div[data-testid="stNotification"] [data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
        font-size: 13px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- CENTERED COLUMN LAYOUT ---
    left_margin, center_card, right_margin = st.columns([1, 1.1, 1])

    with center_card:
        # Branding
        st.markdown('<div class="title-text">TalentPulse</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle-text">India Tech Market Intelligence</div>', unsafe_allow_html=True)

        # Tab Selector (Disguised Radio)
        mode = st.radio(
            "AccessMode", 
            ["Sign In", "Create Account"], 
            label_visibility="collapsed"
        )
        
        # Smooth context switching sub-text & features
        if mode == "Sign In":
            st.markdown("""
            <div class="feature-box">
                <div class="feature-item"><span class="feature-spark">✦</span> Live job market analytics across India</div>
                <div class="feature-item"><span class="feature-spark">✦</span> Salary insights & hiring trend data</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="feature-box">
                <div class="feature-item"><span class="feature-spark">✦</span> Gain comprehensive platform dashboard entry</div>
                <div class="feature-item"><span class="feature-spark">✦</span> Skill gap analysis tools powered by AI</div>
            </div>
            """, unsafe_allow_html=True)

        # Input Forms
        email = st.text_input("Email Address", placeholder="name@company.com").strip().lower()
        password = st.text_input("Password", type="password", placeholder="••••••••")

        st.markdown("<br>", unsafe_allow_html=True)

        # Action Handling
        if mode == "Sign In":
            if st.button("Sign In to Dashboard", use_container_width=True):
                if not email or not password:
                    st.error("Please fill out all fields.")
                else:
                    try:
                        with get_db_connection() as conn:
                            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                                cur.execute("SELECT password FROM app_users WHERE email = %s;", (email,))
                                user_record = cur.fetchone()
                        
                        if not user_record:
                            st.error("No account found with this email.")
                        elif user_record["password"] != password:
                            st.error("Incorrect password. Please try again.")
                        else:
                            st.session_state["authenticated"] = True
                            st.session_state["user_info"] = {"email": email}
                            st.toast("🔒 Access verified! Loading...")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Database error: {e}")

        elif mode == "Create Account":
            if st.button("Register Free Account", use_container_width=True):
                if not email or not password:
                    st.error("Please fill out all fields.")
                elif "@" not in email or "." not in email:
                    st.error("Please enter a valid email address.")
                elif len(password) < 4:
                    st.error("Password must be at least 4 characters long.")
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
                                    st.success("✨ Account created successfully! Toggle to Sign In above to enter.")
                    except Exception as e:
                        st.error(f"Database registration failed: {e}")
