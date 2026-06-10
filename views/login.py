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

    if "login_mode" not in st.session_state:
        st.session_state["login_mode"] = "signin"

    mode = st.session_state["login_mode"]

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
    [data-testid="stVerticalBlock"] > div { gap: 0 !important; }
    div[data-testid="stColumn"] { background: #0d0d14 !important; padding: 0 !important !important; }
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

    /* ALL buttons reset first */
    div[data-testid="stButton"] > button {
        font-family: 'Space Grotesk', sans-serif !important;
        border-radius: 8px !important;
        font-size: 13.5px !important;
        font-weight: 500 !important;
        width: 100% !important;
        transition: background 0.18s, color 0.18s, transform 0.12s !important;
        border: none !important;
    }

    /* Tab buttons — identified by key prefix via aria-label isn't reliable,
       so we use nth-of-type on the tab row columns */
    .tab-col div[data-testid="stButton"] > button {
        background: transparent !important;
        color: #555570 !important;
        padding: 10px 0 !important;
        border-radius: 7px !important;
        margin: 0 !important;
    }
    .tab-col div[data-testid="stButton"] > button:hover {
        background: #1a1a28 !important;
        color: #aaaacc !important;
        transform: none !important;
    }

    /* Active tab */
    .tab-active div[data-testid="stButton"] > button {
        background: #1e1e2d !important;
        color: #ffffff !important;
        padding: 10px 0 !important;
        border-radius: 7px !important;
        margin: 0 !important;
    }

    /* Action button (sign in / register) */
    .action-btn div[data-testid="stButton"] > button {
        background: #7c6ef5 !important;
        color: #fff !important;
        padding: 12px 0 !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        margin-top: 6px !important;
    }
    .action-btn div[data-testid="stButton"] > button:hover {
        background: #9080f7 !important;
        transform: translateY(-1px) !important;
    }
    .action-btn div[data-testid="stButton"] > button:active {
        background: #6355d4 !important;
        transform: scale(0.985) !important;
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

    _, col, _ = st.columns([1, 1.1, 1])

    with col:
        # Brand
        st.markdown("""
        <div style="font-family:'Space Grotesk',sans-serif;font-size:32px;font-weight:600;
                    color:#fff;text-align:center;letter-spacing:-0.03em;margin-bottom:6px;">
            Talent<span style="color:#7c6ef5;">Pulse</span>
        </div>
        <div style="font-family:'Space Grotesk',sans-serif;font-size:15px;color:#555570;
                    text-align:center;margin-bottom:28px;">
            India Tech Market Intelligence
        </div>

        <!-- Tab tray background -->
        <div style="background:#16161f;border-radius:10px;padding:4px;margin-bottom:2px;display:flex;" id="tab-tray">
        </div>
        """, unsafe_allow_html=True)

        # Tab tray — two columns inside a styled wrapper
        st.markdown('<div style="background:#16161f;border-radius:10px;padding:4px;display:flex;gap:0;">', unsafe_allow_html=True)
        tab_l, tab_r = st.columns([1, 1], gap="small")

        with tab_l:
            cls = "tab-active" if mode == "signin" else "tab-col"
            st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
            if st.button("Sign In", key="tab_si", use_container_width=True):
                st.session_state["login_mode"] = "signin"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with tab_r:
            cls = "tab-active" if mode == "register" else "tab-col"
            st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
            if st.button("Create Account", key="tab_reg", use_container_width=True):
                st.session_state["login_mode"] = "register"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Underline indicator
        left_ul  = "2px solid #7c6ef5" if mode == "signin"   else "2px solid transparent"
        right_ul = "2px solid #7c6ef5" if mode == "register" else "2px solid transparent"
        st.markdown(f"""
        <div style="display:flex;margin-top:-10px;margin-bottom:20px;">
            <div style="flex:1;border-bottom:{left_ul};"></div>
            <div style="flex:1;border-bottom:{right_ul};"></div>
        </div>
        """, unsafe_allow_html=True)

        # Hints
        if mode == "signin":
            hints = [
                "Live job market analytics across India",
                "Real-time salary benchmarks by role &amp; city",
                "Hiring trends across 50+ tech companies",
                "Skill demand shifts updated weekly",
            ]
        else:
            hints = [
                "Full dashboard access from day one",
                "AI-powered skill gap analysis",
                "Personalised market reports for your role",
                "Free forever — no credit card needed",
            ]

        hints_html = "".join(
            f'<div style="display:flex;align-items:center;gap:10px;font-family:Space Grotesk,sans-serif;'
            f'font-size:13px;color:#555570;padding:4px 0;">'
            f'<span style="width:5px;height:5px;min-width:5px;background:#7c6ef5;border-radius:50%;display:inline-block;"></span>'
            f'{h}</div>'
            for h in hints
        )
        st.markdown(f"""
        <div style="background:#16161f;border:1px solid #1e1e2d;border-radius:10px;
                    padding:14px 18px;margin-bottom:20px;">
            {hints_html}
        </div>
        """, unsafe_allow_html=True)

        # Inputs
        email    = st.text_input("Email Address", placeholder="name@company.com", key="tp_email").strip().lower()
        password = st.text_input("Password", type="password", placeholder="••••••••", key="tp_pw")

        # Action button
        st.markdown('<div class="action-btn">', unsafe_allow_html=True)

        if mode == "signin":
            if st.button("Sign in →", use_container_width=True, key="tp_action"):
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
            if st.button("Create free account →", use_container_width=True, key="tp_action"):
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

        st.markdown('</div>', unsafe_allow_html=True)
