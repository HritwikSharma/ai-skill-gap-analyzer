import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor

# Direct secure connection setup to your AWS RDS instance
def get_db_connection():
    return psycopg2.connect(
        host=st.secrets["database"]["host"],
        port=st.secrets["database"]["port"],
        database=st.secrets["database"]["database"],
        user=st.secrets["database"]["user"],
        password=st.secrets["database"]["password"]
    )

def render_login():
    # --- 1. CLEAN CUSTOM CSS STYLING OVERLAY ---
    # This forces the dark theme and keeps every single element locked in the center
    st.markdown("""
    <style>
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background-color: #0f0f0f !important;
    }
    #MainMenu, footer, header { visibility: hidden; }
    
    /* Lock the center width layout column cleanly */
    div[data-testid="stColumn"] {
        background-color: #0f0f0f;
        padding: 24px;
        border-radius: 12px;
    }
    
    /* Header branding style text overrides */
    .title-text {
        font-family: 'Inter', sans-serif;
        color: #ffffff;
        font-size: 28px;
        font-weight: 600;
        text-align: center;
        margin-bottom: 2px;
        letter-spacing: -0.03em;
    }
    .subtitle-text {
        font-family: 'Inter', sans-serif;
        color: rgba(255, 255, 255, 0.4);
        font-size: 13px;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    # --- 2. PERFECT CENTERED CARD COLUMN LAYOUT ---
    # Creates three columns across the screen and puts the form inside the exact center one
    left_margin, center_card, right_margin = st.columns([1, 1.2, 1])

    with center_card:
        # Header Labels
        st.markdown('<div class="title-text">TalentPulse</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle-text">India Tech Market Intelligence</div>', unsafe_allow_html=True)

        # Standard, reliable switching tabs
        mode = st.radio("Toggle Access", ["Sign In", "Create Account"], label_visibility="collapsed", horizontal=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

        # Pure form entry input vector fields
        email = st.text_input("Email Address", placeholder="name@company.com").strip().lower()
        password = st.text_input("Password", type="password", placeholder="••••••••")

        st.markdown("<br>", unsafe_allow_html=True)

        # Execution actions
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
                            st.success("Access verified!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Database connection error: {e}")

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
                                    st.success("Account created successfully! Toggle to Sign In to enter.")
                    except Exception as e:
                        st.error(f"Database registration failed: {e}")
