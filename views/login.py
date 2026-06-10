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

    # ── Tab switching via query params (no st.button needed for tabs) ──
    if "login_mode" not in st.session_state:
        st.session_state["login_mode"] = "signin"

    params = st.query_params
    if "tab" in params:
        st.session_state["login_mode"] = params["tab"]
        st.query_params.clear()
        st.rerun()

    mode = st.session_state["login_mode"]

    # ── ALL CSS ── 
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600&display=swap');

    html, body, .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"] {
        background-color: #0d0d14 !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }
    #MainMenu, footer, header { visibility: hidden; }

    /* Remove all default streamlit spacing */
    [data-testid="stVerticalBlock"] > div { gap: 0 !important; }
    div[data-testid="stColumn"] { background: #0d0d14 !important; padding: 0 !important; }
    [data-testid="stMainBlockContainer"] { padding-top: 60px !important; }

    /* inputs */
    div[data-testid="stTextInput"] { margin-bottom: 0 !important; }
    div[data-testid="stTextInput"] label p {
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 11px !important; font-weight: 500 !important;
        color: #555570 !important; letter-spacing: 0.09em !important;
        text-transform: uppercase !important; margin-bottom: 4px !important;
    }
    div[data-testid="stTextInput"] div[data-baseweb="base-input"] {
        background: #16161f !important;
        border: 1px solid #252538 !important;
        border-radius: 8px !important;
    }
    div[data-testid="stTextInput"] div[data-baseweb="base-input"]:focus-within {
        border-color: #7c6ef5 !important;
        box-shadow: 0 0 0 3px rgba(124,110,245,0.13) !important;
    }
    div[data-testid="stTextInput"] input {
        background: transparent !important; color: #e8e8f0 !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 14px !important; caret-color: #7c6ef5 !important;
    }
    div[data-testid="stTextInput"] input::placeholder { color: #2e2e45 !important; }

    /* action button */
    div[data-testid="stButton"] > button {
        background: #7c6ef5 !important; color: #fff !important;
        border: none !important; border-radius: 8px !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 14px !important; font-weight: 600 !important;
        padding: 11px 0 !important; width: 100% !important;
        transition: background 0.18s, transform 0.12s !important;
        margin-top: 6px !important;
    }
    div[data-testid="stButton"] > button:hover {
        background: #9080f7 !important; transform: translateY(-1px) !important;
    }
    div[data-testid="stButton"] > button:active {
        background: #6355d4 !important; transform: scale(0.985) !important;
    }

    /* alerts */
    div[data-testid="stAlert"] {
        background: #16161f !important; border: 1px solid #252538 !important;
        border-radius: 8px !important; margin-top: 10px !important;
    }
    div[data-testid="stAlert"] p {
        color: #9090aa !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 13px !important;
    }
    div[data-testid="stToast"] {
        background: #1e1e2d !important; border-radius: 8px !important;
        font-family: 'Space Grotesk', sans-serif !important; color: #fff !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Centered layout ──
    _, col, _ = st.columns([1, 1.1, 1])

    with col:
        # ── Brand + tabs + hints all in one HTML block inside the centered column ──
        signin_cls  = "tp-tab-on"  if mode == "signin"   else "tp-tab-off"
        reg_cls     = "tp-tab-on"  if mode == "register" else "tp-tab-off"

        hints = """
            <div class="tp-hint"><span class="tp-dot"></span>Live job market analytics across India</div>
            <div class="tp-hint"><span class="tp-dot"></span>Salary insights &amp; hiring trend data</div>
        """ if mode == "signin" else """
            <div class="tp-hint"><span class="tp-dot"></span>Comprehensive platform dashboard access</div>
            <div class="tp-hint"><span class="tp-dot"></span>Skill gap analysis tools powered by AI</div>
        """

        st.markdown(f"""
        <style>
        .tp-logo {{
            font-family:'Space Grotesk',sans-serif; font-size:22px; font-weight:600;
            color:#fff; text-align:center; letter-spacing:-0.02em; margin-bottom:4px;
        }}
        .tp-logo span {{ color:#7c6ef5; }}
        .tp-sub {{
            font-family:'Space Grotesk',sans-serif; font-size:12px; color:#555570;
            text-align:center; letter-spacing:0.03em; margin-bottom:28px;
        }}
        .tp-tabs {{
            display:flex; background:#16161f; border-radius:10px;
            padding:4px; gap:4px; margin-bottom:6px;
        }}
        .tp-tab-on, .tp-tab-off {{
            flex:1; padding:9px 0; border-radius:7px; border:none;
            font-family:'Space Grotesk',sans-serif; font-size:13px; font-weight:500;
            text-align:center; cursor:pointer; text-decoration:none; display:block;
            transition:background 0.2s,color 0.2s;
        }}
        .tp-tab-on  {{ background:#1e1e2d; color:#ffffff; }}
        .tp-tab-off {{ background:transparent; color:#555570; }}
        .tp-tab-off:hover {{ color:#9090aa; text-decoration:none; }}
        .tp-sep {{ height:1px; background:#1a1a28; margin-bottom:18px; }}
        .tp-hints {{
            background:#16161f; border:1px solid #1e1e2d; border-radius:10px;
            padding:12px 16px; margin-bottom:18px;
        }}
        .tp-hint {{
            display:flex; align-items:center; gap:9px;
            font-family:'Space Grotesk',sans-serif; font-size:12.5px;
            color:#555570; padding:3px 0;
        }}
        .tp-dot {{
            width:5px; height:5px; min-width:5px;
            background:#7c6ef5; border-radius:50%; display:inline-block;
        }}
        </style>

        <div class="tp-logo">Talent<span>Pulse</span></div>
        <div class="tp-sub">India Tech Market Intelligence</div>

        <div class="tp-tabs">
            <a href="?tab=signin"   class="{signin_cls}">Sign In</a>
            <a href="?tab=register" class="{reg_cls}">Create Account</a>
        </div>
        <div class="tp-sep"></div>

        <div class="tp-hints">{hints}</div>
        """, unsafe_allow_html=True)

        # ── Streamlit inputs & button ──
        email    = st.text_input("Email Address", placeholder="name@company.com", key="tp_email").strip().lower()
        password = st.text_input("Password", type="password", placeholder="••••••••", key="tp_pw")

        if mode == "signin":
            if st.button("Sign in →", use_container_width=True, key="tp_btn"):
                if not email or not password:
                    st.error("Please fill in all fields.")
                else:
                    try:
                        with get_db_connection() as conn:
                            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                                cur.execute("SELECT password FROM app_users WHERE email = %s;", (email,))
                                rec = cur.fetchone()
                        if not rec:
                            st.error("No account found with this email.")
                        elif rec["password"] != password:
                            st.error("Incorrect password. Please try again.")
                        else:
                            st.session_state["authenticated"] = True
                            st.session_state["user_info"] = {"email": email}
                            st.toast("Access verified — loading dashboard...")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Database error: {e}")
        else:
            if st.button("Create free account →", use_container_width=True, key="tp_btn"):
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
