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
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600&display=swap');

    html, body, .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"] {
        background-color: #0d0d14 !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }
    #MainMenu, footer, header { visibility: hidden; }

    [data-testid="stVerticalBlock"] { gap: 0rem !important; }

    div[data-testid="stColumn"] {
        background-color: #0d0d14 !important;
        padding: 0 20px !important;
    }

    /* ── Brand ── */
    .tp-logo {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 22px;
        font-weight: 600;
        color: #ffffff;
        letter-spacing: -0.02em;
        text-align: center;
        margin-bottom: 4px;
    }
    .tp-logo span { color: #7c6ef5; }
    .tp-tagline {
        font-size: 12px;
        color: #555566;
        text-align: center;
        margin-bottom: 32px;
        letter-spacing: 0.03em;
    }

    /* ── Tab container ── */
    .tp-tabs {
        display: flex;
        background: #16161f;
        border-radius: 10px;
        padding: 4px;
        gap: 4px;
        margin-bottom: 20px;
    }
    .tp-tab {
        flex: 1;
        padding: 8px 0;
        border-radius: 7px;
        border: none;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 13px;
        font-weight: 500;
        cursor: pointer;
        transition: background 0.2s, color 0.2s;
        text-align: center;
    }
    .tp-tab-active  { background: #1e1e2d; color: #ffffff; }
    .tp-tab-inactive { background: transparent; color: #555566; }

    /* ── Hint box ── */
    .tp-hints {
        background: #16161f;
        border: 1px solid #1e1e2d;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 20px;
    }
    .tp-hint {
        display: flex;
        align-items: center;
        gap: 9px;
        font-size: 12.5px;
        color: #555566;
        padding: 3px 0;
    }
    .tp-hint-dot {
        width: 5px;
        height: 5px;
        min-width: 5px;
        background: #7c6ef5;
        border-radius: 50%;
    }

    /* ── Inputs ── */
    div[data-testid="stTextInput"] label p {
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 11px !important;
        font-weight: 500 !important;
        color: #555566 !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
    }
    div[data-testid="stTextInput"] div[data-baseweb="input"],
    div[data-testid="stTextInput"] div[data-baseweb="base-input"] {
        background: #16161f !important;
        border: 1px solid #252535 !important;
        border-radius: 8px !important;
    }
    div[data-testid="stTextInput"] input {
        background: transparent !important;
        color: #ffffff !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 14px !important;
        caret-color: #7c6ef5 !important;
    }
    div[data-testid="stTextInput"] input::placeholder {
        color: #2e2e40 !important;
    }
    div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {
        border-color: #7c6ef5 !important;
        box-shadow: 0 0 0 3px rgba(124,110,245,0.15) !important;
    }

    /* ── Primary action button ── */
    div[data-testid="stButton"] > button[kind="secondary"],
    div[data-testid="stButton"] > button {
        background: #7c6ef5 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        padding: 10px 0 !important;
        width: 100% !important;
        transition: background 0.2s ease, transform 0.15s ease !important;
        margin-top: 6px !important;
    }
    div[data-testid="stButton"] > button:hover {
        background: #8f83f7 !important;
        transform: translateY(-1px) !important;
    }
    div[data-testid="stButton"] > button:active {
        background: #6a5de0 !important;
        transform: scale(0.985) !important;
    }

    /* ── Tab toggle buttons — override purple for those ── */
    .tp-tab-btn button {
        background: transparent !important;
        border: none !important;
        padding: 6px 0 !important;
        margin: 0 !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        color: #555566 !important;
        border-radius: 7px !important;
    }

    /* ── Alerts ── */
    div[data-testid="stAlert"] {
        background: #16161f !important;
        border: 1px solid #252535 !important;
        border-radius: 8px !important;
        margin-top: 8px !important;
    }
    div[data-testid="stAlert"] p {
        color: #aaaabb !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 13px !important;
    }
    div[data-testid="stToast"] {
        background: #1e1e2d !important;
        border: 1px solid #252535 !important;
        border-radius: 8px !important;
        font-family: 'Space Grotesk', sans-serif !important;
        color: #fff !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Initialize tab state ──
    if "login_mode" not in st.session_state:
        st.session_state["login_mode"] = "signin"

    _, center, _ = st.columns([1, 1.1, 1])

    with center:
        # Brand
        st.markdown('<div class="tp-logo">Talent<span>Pulse</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="tp-tagline">India Tech Market Intelligence</div>', unsafe_allow_html=True)

        # Tab switcher using HTML + two columns
        tab_l, tab_r = st.columns(2)
        with tab_l:
            active_l = "tp-tab tp-tab-active" if st.session_state["login_mode"] == "signin" else "tp-tab tp-tab-inactive"
            if st.button("Sign In", key="tab_signin", use_container_width=True):
                st.session_state["login_mode"] = "signin"
                st.rerun()
        with tab_r:
            if st.button("Create Account", key="tab_register", use_container_width=True):
                st.session_state["login_mode"] = "register"
                st.rerun()

        # Active underline indicator
        mode = st.session_state["login_mode"]
        left_border = "2px solid #7c6ef5" if mode == "signin" else "2px solid transparent"
        right_border = "2px solid #7c6ef5" if mode == "register" else "2px solid transparent"
        st.markdown(f"""
        <div style="display:flex; margin-top:-12px; margin-bottom:20px;">
            <div style="flex:1; border-bottom:{left_border}; transition:border 0.2s;"></div>
            <div style="flex:1; border-bottom:{right_border}; transition:border 0.2s;"></div>
        </div>
        """, unsafe_allow_html=True)

        # Contextual hints
        if mode == "signin":
            st.markdown("""
            <div class="tp-hints">
                <div class="tp-hint"><span class="tp-hint-dot"></span>Live job market analytics across India</div>
                <div class="tp-hint"><span class="tp-hint-dot"></span>Salary insights &amp; hiring trend data</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="tp-hints">
                <div class="tp-hint"><span class="tp-hint-dot"></span>Comprehensive platform dashboard access</div>
                <div class="tp-hint"><span class="tp-hint-dot"></span>Skill gap analysis tools powered by AI</div>
            </div>
            """, unsafe_allow_html=True)

        # Inputs
        email = st.text_input("Email Address", placeholder="name@company.com", key="login_email").strip().lower()
        password = st.text_input("Password", type="password", placeholder="••••••••", key="login_password")

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        # Actions
        if mode == "signin":
            if st.button("Sign in →", use_container_width=True, key="btn_signin"):
                if not email or not password:
                    st.error("Please fill in all fields.")
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
                            st.toast("Access verified — loading dashboard...")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Database error: {e}")
        else:
            if st.button("Create free account →", use_container_width=True, key="btn_register"):
                if not email or not password:
                    st.error("Please fill in all fields.")
                elif "@" not in email or "." not in email:
                    st.error("Please enter a valid email address.")
                elif len(password) < 4:
                    st.error("Password must be at least 4 characters.")
                else:
                    try:
                        with get_db_connection() as conn:
                            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                                cur.execute("SELECT email FROM app_users WHERE email = %s;", (email,))
                                if cur.fetchone():
                                    st.error("This email is already registered.")
                                else:
                                    cur.execute(
                                        "INSERT INTO app_users (email, password) VALUES (%s, %s);",
                                        (email, password)
                                    )
                                    conn.commit()
                                    st.success("Account created — switch to Sign In to continue.")
                    except Exception as e:
                        st.error(f"Registration failed: {e}")
