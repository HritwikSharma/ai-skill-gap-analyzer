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

    /* ── Base reset ── */
    html, body, .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"] {
        background-color: #0d0d14 !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }
    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="stVerticalBlock"] { gap: 0 !important; }

    /* ── Column gutters ── */
    div[data-testid="stColumn"] {
        background-color: #0d0d14;
        padding: 0 24px;
    }

    /* ── Brand header ── */
    .tp-logo {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 20px;
        font-weight: 600;
        color: #ffffff;
        letter-spacing: -0.02em;
        text-align: center;
        margin-bottom: 4px;
    }
    .tp-logo span { color: #7c6ef5; }
    .tp-tagline {
        font-size: 12px;
        color: #6b6b80;
        text-align: center;
        margin-bottom: 36px;
        letter-spacing: 0.02em;
    }

    /* ── Tab row (radio disguised) ── */
    div[data-testid="stRadio"] > label { display: none !important; }

    div[data-testid="stRadio"] > div {
        flex-direction: row !important;
        background: #16161f !important;
        border-radius: 10px !important;
        padding: 4px !important;
        gap: 4px !important;
        margin-bottom: 28px !important;
        border: none !important;
    }

    /* hide the actual radio circle */
    div[data-testid="stRadio"] input[type="radio"] { display: none !important; }

    /* each option pill */
    div[data-testid="stRadio"] div[data-viewport="true"] label {
        flex: 1 !important;
        padding: 8px 0 !important;
        background: transparent !important;
        border: none !important;
        border-radius: 7px !important;
        color: #6b6b80 !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        text-align: center !important;
        cursor: pointer !important;
        transition: background 0.2s ease, color 0.2s ease !important;
        margin: 0 !important;
    }

    /* active pill */
    div[data-testid="stRadio"] div[data-viewport="true"] label:has(input:checked) {
        background: #1e1e2d !important;
        color: #ffffff !important;
    }

    div[data-testid="stRadio"] div[data-viewport="true"] label:hover {
        color: #aaaabb !important;
    }

    /* ── Feature hint box ── */
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
        color: #6b6b80;
        padding: 4px 0;
    }
    .tp-hint-dot {
        width: 5px;
        height: 5px;
        background: #7c6ef5;
        border-radius: 50%;
        flex-shrink: 0;
    }

    /* ── Text inputs ── */
    div[data-testid="stTextInput"] label {
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 11.5px !important;
        font-weight: 500 !important;
        color: #6b6b80 !important;
        letter-spacing: 0.06em !important;
        text-transform: uppercase !important;
        margin-bottom: 4px !important;
    }

    div[data-testid="stTextInput"] input {
        background: #16161f !important;
        border: 1px solid #252535 !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 14px !important;
        padding: 10px 14px !important;
        transition: border-color 0.2s ease, background 0.2s ease !important;
    }

    div[data-testid="stTextInput"] input::placeholder {
        color: #3a3a50 !important;
        font-size: 13px !important;
    }

    div[data-testid="stTextInput"] input:hover {
        border-color: #333348 !important;
    }

    div[data-testid="stTextInput"] input:focus {
        border-color: #7c6ef5 !important;
        background: #111120 !important;
        box-shadow: 0 0 0 3px rgba(124, 110, 245, 0.12) !important;
    }

    /* ── Primary button ── */
    div[data-testid="stButton"] > button {
        background: #7c6ef5 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 13.5px !important;
        font-weight: 600 !important;
        letter-spacing: 0.01em !important;
        padding: 10px 0 !important;
        transition: background 0.2s ease, transform 0.15s ease !important;
        width: 100% !important;
    }

    div[data-testid="stButton"] > button:hover {
        background: #8f83f7 !important;
        transform: translateY(-1px) !important;
    }

    div[data-testid="stButton"] > button:active {
        background: #6a5de0 !important;
        transform: scale(0.985) !important;
    }

    /* ── Alerts ── */
    div[data-testid="stNotification"],
    div[data-testid="stAlert"] {
        background: #16161f !important;
        border: 1px solid #252535 !important;
        border-radius: 8px !important;
    }
    div[data-testid="stNotification"] p,
    div[data-testid="stAlert"] p {
        color: #aaaabb !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 13px !important;
    }

    /* success alert accent */
    div[data-testid="stAlert"][data-baseweb="notification"] {
        border-left: 3px solid #7c6ef5 !important;
    }

    /* ── Toast ── */
    div[data-testid="stToast"] {
        background: #1e1e2d !important;
        border: 1px solid #252535 !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Layout ──
    _, center, _ = st.columns([1, 1.1, 1])

    with center:
        # Brand
        st.markdown(
            '<div class="tp-logo">Talent<span>Pulse</span></div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="tp-tagline">India Tech Market Intelligence</div>',
            unsafe_allow_html=True
        )

        # Pill tab switcher
        mode = st.radio(
            "mode",
            ["Sign In", "Create Account"],
            horizontal=True,
            label_visibility="collapsed"
        )

        # Contextual hints
        if mode == "Sign In":
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
        email = st.text_input("Email Address", placeholder="name@company.com").strip().lower()
        password = st.text_input("Password", type="password", placeholder="••••••••")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # Actions
        if mode == "Sign In":
            if st.button("Sign in →", use_container_width=True):
                if not email or not password:
                    st.error("Please fill in all fields.")
                else:
                    try:
                        with get_db_connection() as conn:
                            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                                cur.execute(
                                    "SELECT password FROM app_users WHERE email = %s;",
                                    (email,)
                                )
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
            if st.button("Create free account →", use_container_width=True):
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
                                cur.execute(
                                    "SELECT email FROM app_users WHERE email = %s;",
                                    (email,)
                                )
                                if cur.fetchone():
                                    st.error("This email is already registered.")
                                else:
                                    cur.execute(
                                        "INSERT INTO app_users (email, password) VALUES (%s, %s);",
                                        (email, password)
                                    )
                                    conn.commit()
                                    st.success("Account created — switch to Sign In above to continue.")
                    except Exception as e:
                        st.error(f"Registration failed: {e}")
