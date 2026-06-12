import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import psycopg2
import plotly.express as px
import plotly.graph_objects as go
import json
import re
import re as _re
import html as _html
from collections import Counter
from utils.groq_analyzer import get_ai_analysis
from utils.gemini_analyzer import get_ai_analysis

def render_dashboard():
    #st.title("TalentPulse Dashboard")
    # ─────────────────────────────────────────────
    #  DATABASE CREDENTIALS
    # ─────────────────────────────────────────────
    DB_HOST     = "job-db.clgqc6scelz7.eu-north-1.rds.amazonaws.com"
    DB_USER     = "postgres"
    DB_NAME     = "postgres"
    DB_PASSWORD = "HRITWIKSHARMA"
    
    # ─────────────────────────────────────────────
    #  PAGE CONFIG — minimal Streamlit chrome
    # ─────────────────────────────────────────────
    
    # Strip ALL Streamlit chrome — we own the full canvas
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Sora:wght@400;600;700&display=swap');
    html, body, .stApp, [data-testid="stAppViewContainer"],
    [data-testid="stMain"], .block-container,
    [data-testid="stMainBlockContainer"],
    [data-testid="stAppViewBlockContainer"] {
        background: #0d0d0d !important;
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* 1. CRITICAL: Force-collapse the header height to 0px and remove it from layout flow */
    /* 1. CRITICAL: Hide MainMenu and footer, but preserve header layer for sidebar toggles */
    #MainMenu, footer { 
        display: none !important; 
    }
    header, [data-testid="stHeader"] {
        background: transparent !important;
        pointer-events: none !important; /* Lets clicks pass through empty header space */
    }
    
    /* 2. Absolute guarantee that the main structural wrapper has zero top padding offset */
    .main .block-container, [data-testid="stAppViewBlockContainer"] { 
        padding-top: 0px !important; 
    }
    
    .block-container { padding: 0 !important; }
    [data-testid="stVerticalBlock"] > div { padding: 0 !important; }
    /* Hide Streamlit's iframe borders */
    iframe { border: none !important; }
    /* Kill default element spacing */
    div.element-container { margin: 0 !important; padding: 0 !important; }
    </style>
    """, unsafe_allow_html=True)
    
    # ─────────────────────────────────────────────
    #  PLOTLY BASE TEMPLATE
    # ─────────────────────────────────────────────
    _AXIS_STYLE = dict(
        gridcolor="#1e1e1e", linecolor="#2a2a2a",
        tickfont=dict(size=11, color="#aaa"),
        zerolinecolor="#2a2a2a"
    )
    
    PLOTLY_LAYOUT = dict(
        font=dict(family="Inter, sans-serif", color="#e0e0e0"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#141414",
        margin=dict(l=8, r=8, t=36, b=8),
        title_font=dict(size=12, color="#888", family="Inter, sans-serif"),
        xaxis=_AXIS_STYLE,
        yaxis=_AXIS_STYLE,
        colorway=["#3b82f6","#10b981","#f59e0b","#8b5cf6","#ef4444","#06b6d4"],
    )
    PLOTLY_LAYOUT_NO_AXES = {k: v for k, v in PLOTLY_LAYOUT.items() if k not in ("xaxis","yaxis","title_font")}
    
    # ─────────────────────────────────────────────
    #  DATA FETCHING
    # ─────────────────────────────────────────────
    @st.cache_data(ttl=300)
    def fetch_job_data():
        try:
            # We use the clear hardcoded variables defined right above this block
            conn = psycopg2.connect(
                host=DB_HOST,
                user=DB_USER, 
                database=DB_NAME,
                password=DB_PASSWORD, 
                port="5432"
            )
            df = pd.read_sql("""
                SELECT job_id, title, company, location,
                       tech_skills_found, soft_skills_found,
                       extra_metadata, job_url
                FROM job_listings;
            """, conn)
            conn.close()
            return df
        except Exception as e:
            st.error(f"Database connection failed: {e}")
            return pd.DataFrame()
    
    def _parse_salary_to_lpa(salary_str):
        if not salary_str or salary_str == "Not Specified":
            return None
        nums = re.findall(r"\d[\d,]*", salary_str.replace(",", ""))
        nums = [int(n) for n in nums]
        if not nums:
            return None
        mid = sum(nums) / len(nums)
        if mid > 500:
            mid = mid / 100_000
        return round(mid, 1)
    
    def extract_metadata_fields(df):
        def _get(row, key):
            try:
                m = row if isinstance(row, dict) else json.loads(row)
                return m.get(key)
            except Exception:
                return None
        df["experience_level"] = df["extra_metadata"].apply(lambda r: _get(r, "experience_level"))
        df["salary_str"]       = df["extra_metadata"].apply(lambda r: _get(r, "salary_extracted"))
        df["salary_lpa"]       = df["salary_str"].apply(_parse_salary_to_lpa)
        df["posted_date"]      = df["extra_metadata"].apply(lambda r: _get(r, "created_timestamp"))
        return df
    
    CITY_COORDS = {
        "bengaluru":(12.9716,77.5946),"bangalore":(12.9716,77.5946),
        "hyderabad":(17.3850,78.4867),"pune":(18.5204,73.8567),
        "mumbai":(19.0760,72.8777),"bombay":(19.0760,72.8777),
        "chennai":(13.0827,80.2707),"madras":(13.0827,80.2707),
        "delhi":(28.6139,77.2090),"new delhi":(28.6139,77.2090),
        "gurugram":(28.4595,77.0266),"gurgaon":(28.4595,77.0266),
        "noida":(28.5355,77.3910),"kolkata":(22.5726,88.3639),
        "ahmedabad":(23.0225,72.5714),"jaipur":(26.9124,75.7873),
        "coimbatore":(11.0168,76.9558),"kochi":(9.9312,76.2673),
        "lucknow":(26.8467,80.9462),"chandigarh":(30.7333,76.7794),
        "remote":(20.5937,78.9629),"india":(20.5937,78.9629),
    }
    EXCLUDE_MAP = {"remote","india"}
    
    def build_map_data(df):
        rows = []
        for loc in df["location"].dropna():
            loc_lower = str(loc).strip().lower()
            for city, (lat, lon) in CITY_COORDS.items():
                if city in loc_lower and city not in EXCLUDE_MAP:
                    rows.append({"city": city.title(), "lat": lat, "lon": lon})
                    break
        if not rows:
            return pd.DataFrame()
        tmp = pd.DataFrame(rows)
        return tmp.groupby(["city","lat","lon"]).size().reset_index(name="openings")
    
    def normalise_exp(val):
        if not val or str(val).strip().lower() in ("not specified","none","nan",""):
            return None
        v = str(val).strip()
        v_lower = v.lower()
        if "intern" in v_lower:
            return "Internship"
        nums = re.findall(r"\d+", v)
        if not nums:
            return None
        n = int(nums[0])
        if n == 0: return "<1 Year"
        if 1 <= n <= 5: return "1-5 Years"
        if n > 5: return ">5 Years"
        return None
    
    def clean_title(t):
        if not t: return t
        t = re.sub(r'\s*[-–(|_].*$', '', str(t).strip())
        return re.sub(r'\s+', ' ', t).strip().title()
    
    # ─────────────────────────────────────────────
    #  LOAD DATA
    # ─────────────────────────────────────────────
    df_raw = fetch_job_data()
    if df_raw.empty:
        st.error("No data. Check DB connection.")
        st.stop()
    
    df = extract_metadata_fields(df_raw.copy())
    df["experience_level"] = df["experience_level"].apply(normalise_exp)
    df["title_clean"] = df["title"].apply(clean_title)

# ____________________    
    fdf = df.copy()
    # ─────────────────────────────────────────────
    #  SESSION STATE
    # ─────────────────────────────────────────────
    if "listing_page" not in st.session_state:
        st.session_state["listing_page"] = 1
    if "active_tab" not in st.session_state:
        st.session_state["active_tab"] = "listings"
    if "filter_role" not in st.session_state:
        st.session_state["filter_role"] = "All Roles"
    if "filter_loc" not in st.session_state:
        st.session_state["filter_loc"] = "All Locations"
    if "filter_exp" not in st.session_state:
        st.session_state["filter_exp"] = "All Experience"
    
   # ─────────────────────────────────────────────
    #  NAV BAR (pure HTML component)
    # ─────────────────────────────────────────────
    # Clean injection handling for the logout event listener
    # ─────────────────────────────────────────────
    #  TAB NAV BAR (SYNCED WITH AI VIEWPORT CONTROLLER)
    # ─────────────────────────────────────────────
    # ─────────────────────────────────────────────
    #  TOP NAV BAR — TalentPulse + Sign Out
    # ─────────────────────────────────────────────
    nav_interaction = components.html("""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Sora:wght@600;700&display=swap" rel="stylesheet">
    <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body { background:#0d0d0d; }
    .nav {
        margin:0;
        width: 100%;
        background: #111;
        border-bottom: 1px solid #222;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 32px;
        height: 56px;
        position: sticky;
        top: 0;
    }
    .logo {
        font-family: 'Sora', sans-serif;
        font-size: 1.2rem;
        font-weight: 700;
        color: #3b82f6;
        letter-spacing: -0.03em;
    }
    .logo span { color: #e0e0e0; font-weight: 400; }
    .tag {
        font-size: 0.7rem;
        font-weight: 600;
        color: #555;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }
    .live-dot {
        display: inline-block;
        width: 7px; height: 7px;
        border-radius: 50%;
        background: #10b981;
        margin-right: 6px;
        animation: pulse 2s infinite;
    }
    .signout-btn {
        background: transparent;
        color: #aaa;
        border: 1px solid #2a2a2a;
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 0.75rem;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
        cursor: pointer;
        transition: all 0.15s ease;
    }
    .signout-btn:hover {
        color: #ef4444;
        border-color: #ef4444;
        background: rgba(239, 68, 68, 0.05);
    }
    @keyframes pulse {
        0%,100% { opacity:1; }
        50% { opacity:0.4; }
    }
    </style>
    <div class="nav">
        <div class="logo">TalentPulse <span>India</span></div>
        <div style="display:flex;align-items:center;gap:20px;">
            <div class="tag"><span class="live-dot"></span>Live Tech Market Intelligence</div>
            <button class="signout-btn" onclick="logout()">Sign out</button>
        </div>
    </div>
    <script>
    function logout() {
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: 'trigger_logout'
        }, '*');
    }
    </script>
    """, height=58, scrolling=False)

    if nav_interaction == "trigger_logout":
        st.logout()

    # Catch the HTML click event inside Streamlit and execute the session kill
    if nav_interaction == "trigger_logout":
        st.logout()    
    
    # Apply filters to dataframe
    fdf = df.copy()
    if st.session_state["filter_role"] != "All Roles":
        fdf = fdf[fdf["title_clean"] == st.session_state["filter_role"]]
    if st.session_state["filter_loc"] != "All Locations":
        fdf = fdf[fdf["location"] == st.session_state["filter_loc"]]
    if st.session_state["filter_exp"] != "All Experience":
        fdf = fdf[fdf["experience_level"] == st.session_state["filter_exp"]]
    
    # ─────────────────────────────────────────────
    #  KPI CARDS (pure HTML)
    # ─────────────────────────────────────────────
    total_jobs  = len(fdf)
    unique_cos  = fdf["company"].nunique()
    top_loc_val = fdf["location"].mode().iloc[0] if not fdf["location"].mode().empty else "N/A"
    sal_data    = fdf["salary_lpa"].dropna()
    avg_sal_str = f"{sal_data.mean():.1f} LPA" if not sal_data.empty else "N/A"
    sal_pct     = len(sal_data) / max(len(fdf), 1) * 100
    
    components.html(f"""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Sora:wght@700&display=swap" rel="stylesheet">
    <style>
    * {{ margin:0; padding:0; box-sizing:border-box; font-family:'Inter',sans-serif; }}
    body {{ background:#0d0d0d; padding: 24px 32px 16px; }}
    .grid {{
        display: grid;
        grid-template-columns: repeat(4,1fr);
        gap: 14px;
    }}
    .card {{
        background: #111;
        border: 1px solid #1e1e1e;
        border-radius: 12px;
        padding: 22px 22px 18px;
        transition: border-color 0.2s, transform 0.15s;
        cursor: default;
    }}
    .card:hover {{
        border-color: #3b82f6;
        transform: translateY(-2px);
    }}
    .label {{
        font-size: 0.68rem;
        font-weight: 600;
        color: #555;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 10px;
    }}
    .value {{
        font-family: 'Sora', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: #e0e0e0;
        line-height: 1;
        margin-bottom: 6px;
    }}
    .value.accent {{ color: #3b82f6; }}
    .sub {{
        font-size: 0.75rem;
        color: #555;
        margin-top: 4px;
    }}
    .bar-bg {{
        background: #1e1e1e;
        border-radius: 4px;
        height: 4px;
        margin-top: 10px;
    }}
    .bar-fill {{
        height: 4px;
        border-radius: 4px;
        background: linear-gradient(90deg, #3b82f6, #06b6d4);
    }}
    @media (max-width: 700px) {{ .grid {{ grid-template-columns: repeat(2,1fr); }} }}
    </style>
    <div class="grid">
        <div class="card">
            <div class="label">Active Listings</div>
            <div class="value accent">{total_jobs:,}</div>
            <div class="sub">Across all tracked roles</div>
            <div class="bar-bg"><div class="bar-fill" style="width:100%"></div></div>
        </div>
        <div class="card">
            <div class="label">Unique Employers</div>
            <div class="value">{unique_cos:,}</div>
            <div class="sub">Companies currently hiring</div>
            <div class="bar-bg"><div class="bar-fill" style="width:{min(unique_cos/max(total_jobs,1)*100,100):.0f}%"></div></div>
        </div>
        <div class="card">
            <div class="label">Avg. Salary</div>
            <div class="value">{avg_sal_str}</div>
            <div class="sub">{sal_pct:.0f}% listings disclose salary</div>
            <div class="bar-bg"><div class="bar-fill" style="width:{sal_pct:.0f}%"></div></div>
        </div>
        <div class="card">
            <div class="label">Top Hiring Hub</div>
            <div class="value" style="font-size:1.3rem;padding-top:6px;">{top_loc_val}</div>
            <div class="sub">Highest job concentration</div>
            <div class="bar-bg"><div class="bar-fill" style="width:75%"></div></div>
        </div>
    </div>
    """, height=164, scrolling=False)
        # ─────────────────────────────────────────────
    #  FILTER BAR (pure HTML + postMessage back to Streamlit)
    # ─────────────────────────────────────────────
    role_options = ["All Roles"] + sorted(df["title_clean"].dropna().unique().tolist())
    loc_options  = ["All Locations"] + sorted(df["location"].dropna().unique().tolist())
    exp_options  = ["All Experience", "Internship", "<1 Year", "1-5 Years", ">5 Years"]
    
    # Build HTML option lists
    def opts_html(options, selected):
        return "".join(
            f'<option value="{_html.escape(o)}" {"selected" if o == selected else ""}>{_html.escape(o)}</option>'
            for o in options
        )
    
    filter_html = f"""
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
    * {{ margin:0; padding:0; box-sizing:border-box; font-family:'Inter',sans-serif; }}
    body {{ background:#0d0d0d; padding: 12px 32px; }}
    .filter-bar {{
        display: flex;
        gap: 12px;
        align-items: center;
        background: #111;
        border: 1px solid #222;
        border-radius: 12px;
        padding: 14px 20px;
    }}
    .filter-label {{
        font-size: 0.7rem;
        font-weight: 600;
        color: #555;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        white-space: nowrap;
    }}
    select {{
        flex: 1;
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        color: #e0e0e0;
        font-size: 0.83rem;
        font-family: 'Inter', sans-serif;
        padding: 8px 12px;
        outline: none;
        cursor: pointer;
        transition: border-color 0.15s;
        appearance: none;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23666' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-position: right 10px center;
        padding-right: 30px;
    }}
    select:hover, select:focus {{ border-color: #3b82f6; }}
    select option {{ background: #1a1a1a; }}
    </style>
    
    <div class="filter-bar">
        <span class="filter-label">Filter</span>
        <select id="role" onchange="dispatchFilters()">{opts_html(role_options, st.session_state["filter_role"])}</select>
        <select id="loc" onchange="dispatchFilters()">{opts_html(loc_options, st.session_state["filter_loc"])}</select>
        <select id="exp" onchange="dispatchFilters()">{opts_html(exp_options, st.session_state["filter_exp"])}</select>
    </div>
    
    <script>
    function dispatchFilters() {{
        const role = document.getElementById('role').value;
        const loc  = document.getElementById('loc').value;
        const exp  = document.getElementById('exp').value;
        window.parent.postMessage({{
            type: 'streamlit:setComponentValue',
            value: JSON.stringify({{ role, loc, exp }})
        }}, '*');
    }}
    </script>
    """    
    # ──────────────────────────────────────────────────────────
    # NATIVE FILTER DESIGN BLOCK HERE:
    # ──────────────────────────────────────────────────────────
    # 1. Inject CSS to style native Streamlit components to match your design perfectly
    st.markdown("""
        <style>
        /* Container border box simulating your original UI */
        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stSelectbox"]) {
            background-color: #111111 !important;
            border: 1px solid #222222 !important;
            border-radius: 12px !important;
            padding: 14px 20px !important;
            display: flex !important;
            align-items: center !important;
            gap: 12px !important;
        }
        /* Custom layout adjustments for the row */
        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stSelectbox"]) > div {
            flex: 1 !important;
            min-width: 0 !important;
        }
        /* Style the 'FILTER' section label */
        div[data-testid="stSelectbox"] > label {
            font-family: 'Inter', sans-serif !important;
            font-size: 0.7rem !important;
            font-weight: 600 !important;
            color: #555555 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.08em !important;
            margin-bottom: 4px !important;
        }
        /* Dropdown field styling */
        div[data-testid="stSelectbox"] div[data-baseweb="select"] {
            background-color: #1a1a1a !important;
            border: 1px solid #2a2a2a !important;
            border-radius: 8px !important;
            color: #e0e0e0 !important;
            font-size: 0.83rem !important;
        }
        /* Hover state border highlight */
        div[data-testid="stSelectbox"] div[data-baseweb="select"]:hover {
            border-color: #3b82f6 !important;
        }
        /* Dropdown menu items overlay background color match */
        div[data-baseweb="popover"] ul {
            background-color: #1a1a1a !important;
        }
        div[data-baseweb="popover"] li {
            color: #e0e0e0 !important;
        }
        div[data-baseweb="popover"] li:hover {
            background-color: #2a2a2a !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # 2. Render native dropdowns wrapped inside structural layout columns
    f_col1, f_col2, f_col3 = st.columns(3)

    with f_col1:
        st.selectbox(
            "Filter Roles",
            options=role_options,
            key="filter_role",
            on_change=lambda: st.session_state.update({"listing_page": 1})
        )

    with f_col2:
        st.selectbox(
            "All Locations",
            options=loc_options,
            key="filter_loc",
            on_change=lambda: st.session_state.update({"listing_page": 1})
        )

    with f_col3:
        st.selectbox(
            "All Experience",
            options=exp_options,
            key="filter_exp",
            on_change=lambda: st.session_state.update({"listing_page": 1})
        )
    # ──────────────────────────────────────────────────────────
    # ─────────────────────────────────────────────
    #  TAB NAV (Native Segmented Control)
    # ─────────────────────────────────────────────
    # Use the existing session state value as the default index
    # ─────────────────────────────────────────────
    #  TAB NAV (Styled Native Segmented Control) - FIXED
    # ─────────────────────────────────────────────
    # Custom CSS to style the native segmented control to match your dark theme design
    # ─────────────────────────────────────────────
    #  SIDEBAR NAVIGATION INTERFACE
    # ─────────────────────────────────────────────
    st.markdown("""
    <style>
    header > div {
        pointer-events: auto !important; /* Re-enable pointer events for buttons only */
    }

    /* Force the 3-line menu collapse/expand buttons to be visible and float below top navbar */
    [data-testid="collapsedSidebarButton"],
    [data-testid="stSidebarCollapseButton"],
    button[aria-label="Open sidebar"],
    button[aria-label="Close sidebar"] {
        visibility: visible !important;
        display: flex !important;
        position: fixed !important;
        top: 72px !important; /* Shifts it safely below your 56px custom top navbar */
        left: 16px !important;
        background: #141416 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5) !important;
        transition: all 0.2s ease-in-out !important;
        z-index: 1000000 !important;
    }

    /* Hover effect for the menu toggle button */
    [data-testid="stSidebarCollapseButton"]:hover,
    button[aria-label="Open sidebar"]:hover {
        background: #2563eb !important;
        border-color: #3b82f6 !important;
    }

    /* Style the sidebar panel drawer background */
    [data-testid="stSidebar"] {
        background-color: #0e0e10 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
        z-index: 999998 !important;
    }
    
    /* Convert buttons inside the sidebar into clean dashboard rows */
    [data-testid="stSidebar"] div.stButton > button {
        background: transparent !important;
        border: none !important;
        color: #8e929b !important;
        text-align: left !important;
        justify-content: flex-start !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 13.5px !important;
        padding: 10px 16px !important;
        margin-bottom: 4px !important;
        transition: all 0.2s ease-in-out !important;
        width: 100% !important;
    }
    
    /* Interactive hover state for sidebar options */
    [data-testid="stSidebar"] div.stButton > button:hover {
        color: #ffffff !important;
        background: rgba(255, 255, 255, 0.04) !important;
    }
    
    /* Premium active state indicator accent line */
    [data-testid="stSidebar"] div.stButton > button[kind="primary"] {
        background: rgba(37, 99, 235, 0.12) !important;
        color: #3b82f6 !important;
        font-weight: 600 !important;
        border-left: 3px solid #3b82f6 !important;
        border-radius: 0px 8px 8px 0px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize tracking if not present
    if "custom_active_tab" not in st.session_state:
        st.session_state.custom_active_tab = "listings"

    # Render navigation options inside the sidebar canvas drawer
    with st.sidebar:
        # Spacing buffer zone to push elements below the fixed top header
        st.markdown("<div style='margin-top: 80px;'></div>", unsafe_allow_html=True)
        st.markdown("<div style='font-family:\"Sora\",sans-serif; font-size:11px; font-weight:700; color:#4b5563; letter-spacing: 1px; padding-left:16px; margin-bottom:16px;'>PLATFORM ENGINE</div>", unsafe_allow_html=True)
        
        is_active = (st.session_state.custom_active_tab == "listings")
        if st.button("📋 Job Listings", key="side_btn_listings", use_container_width=True, type="primary" if is_active else "secondary"):
            st.session_state.custom_active_tab = "listings"
            st.rerun()
            
        is_active = (st.session_state.custom_active_tab == "market")
        if st.button("📊 Market Overview", key="side_btn_market", use_container_width=True, type="primary" if is_active else "secondary"):
            st.session_state.custom_active_tab = "market"
            st.rerun()
            
        is_active = (st.session_state.custom_active_tab == "salary")
        if st.button("💰 Salary Insights", key="side_btn_salary", use_container_width=True, type="primary" if is_active else "secondary"):
            st.session_state.custom_active_tab = "salary"
            st.rerun()
            
        is_active = (st.session_state.custom_active_tab == "companies")
        if st.button("🏢 Companies", key="side_btn_companies", use_container_width=True, type="primary" if is_active else "secondary"):
            st.session_state.custom_active_tab = "companies"
            st.rerun()

        is_active = (st.session_state.custom_active_tab == "map")
        if st.button("🗺️ Heat Map", key="side_btn_map", use_container_width=True, type="primary" if is_active else "secondary"):
            st.session_state.custom_active_tab = "map"
            st.rerun()

        is_active = (st.session_state.custom_active_tab == "ai_analyzer")
        if st.button("🎯 AI Skill Analyzer", key="side_btn_ai", use_container_width=True, type="primary" if is_active else "secondary"):
            st.session_state.custom_active_tab = "ai_analyzer"
            st.rerun()

    # Pass layout selection downstream to target content layout routers
    active = st.session_state.custom_active_tab    
    # ─────────────────────────────────────────────
    #  CONTENT AREA WRAPPER (shared padding & layout)
    # ─────────────────────────────────────────────
    st.markdown("""
    <style>
    /* Absolute zero top-padding to let the navbar touch the top edge */
    [data-testid="stMainBlockContainer"] {
        padding: 0px 0px 60px 0px !important;
    }
    
    /* Re-apply 32px side indent ONLY to native Streamlit widgets so they look centered */
    div.element-container:not(:has(iframe)) {
        padding-left: 32px !important;
        padding-right: 32px !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }
    
    /* CRITICAL FIX: Aggressively target every possible tab bar layout wrapper to center elements */
    [data-testid="stTabNav"], 
    [data-testid="stTabBar"], 
    div[role="tablist"], 
    div[data-baseweb="tab-list"] {
        justify-content: center !important;
        display: flex !important;
        width: 100% !important;
        margin: 0 auto !important;
    }

    /* Force the direct child container inside the navigation element to center its buttons */
    [data-testid="stTabNav"] > div,
    div[role="tablist"] > div {
        justify-content: center !important;
        display: flex !important;
        width: 100% !important;
    }
    
    .js-plotly-plot .plotly, .plot-container { background: transparent !important; }
    </style>
    """, unsafe_allow_html=True)
    
    # ─────────────────────────────────────────────
    #  SECTION HEADER HELPER
    # ─────────────────────────────────────────────
    def section_header(title, subtitle=""):
        sub_html = f'<div style="font-size:0.78rem;color:#555;margin-top:3px;">{subtitle}</div>' if subtitle else ""
        st.markdown(f"""
        <div style="margin-bottom:18px;padding-bottom:12px;border-bottom:1px solid #1e1e1e;">
            <div style="font-family:Sora,sans-serif;font-size:1rem;font-weight:600;color:#e0e0e0;">{title}</div>
            {sub_html}
        </div>
        """, unsafe_allow_html=True)
    
    # ══════════════════════════════════════════════
    #  TAB: JOB LISTINGS
    # ══════════════════════════════════════════════
    if active == "listings":
        PAGE_SIZE   = 20
        total_pages = max(1, (len(fdf) - 1) // PAGE_SIZE + 1)
        page_num    = st.session_state["listing_page"]
        start       = (page_num - 1) * PAGE_SIZE
        page_df     = fdf.iloc[start: start + PAGE_SIZE]
    
        st.markdown(
            f'<div style="font-size:0.8rem;color:#555;margin-bottom:16px;">'
            f'Showing <strong style="color:#e0e0e0;">{len(fdf):,}</strong> listings · '
            f'Page {page_num} of {total_pages}</div>',
            unsafe_allow_html=True,
        )
    
        # Build all job cards as one HTML block
        # ──────────────────────────────────────────────────────────
        # NATIVE CARD RENDERING BLOCK HERE:
        # ──────────────────────────────────────────────────────────
        # Inject CSS rules to style our native layout stream cards
        st.markdown("""
            <style>
            .native-job-card {
                background: #111111;
                border: 1px solid transparent;
                border-radius: 12px;
                padding: 18px 20px;
                margin-bottom: 12px;
                width: 100%;
                box-sizing: border-box;
                transition: border-color 0.15s ease;
            }
            .native-job-card:hover {
                border-color: #2a4a7f;
            }
            .job-title {
                font-size: 1rem;
                font-weight: 600;
                color: #3b82f6;
                margin-bottom: 3px;
            }
            .job-title a {
                color: #3b82f6;
                text-decoration: none;
            }
            .job-title a:hover {
                text-decoration: underline;
            }
            .company {
                font-size: 0.88rem;
                font-weight: 500;
                color: #e0e0e0;
                margin-bottom: 3px;
            }
            .meta {
                font-size: 0.78rem;
                color: #555;
                margin-bottom: 10px;
            }
            .pills {
                display: flex;
                flex-wrap: wrap;
                gap: 6px;
                margin-bottom: 12px;
            }
            .skill {
                background: #1a2744;
                color: #3b82f6;
                font-size: 0.68rem;
                font-weight: 600;
                padding: 3px 9px;
                border-radius: 20px;
                letter-spacing: 0.02em;
            }
            .badge {
                font-size: 0.68rem;
                font-weight: 600;
                padding: 3px 9px;
                border-radius: 20px;
            }
            .badge.green { background:#0d2e1e; color:#10b981; }
            .badge.amber { background:#2d1e0d; color:#f59e0b; }
            .apply {
                display: inline-block;
                background: #1a2744;
                color: #3b82f6;
                font-size: 0.78rem;
                font-weight: 600;
                padding: 6px 16px;
                border-radius: 8px;
                text-decoration: none;
                transition: background 0.15s;
                border: 1px solid #2a3f6f;
            }
            .apply:hover { background: #243560; }
            </style><img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" onload="window.parent.scrollTo(0,0);" style="display:none;"/>
        """, unsafe_allow_html=True)

        # Loop and mount elements onto the main Streamlit layout canvas container
        for _, row in page_df.iterrows():
            title   = _html.escape(str(row.get("title") or "Untitled"))
            company = _html.escape(str(row.get("company") or "Unknown Company"))
            loc     = _html.escape(str(row.get("location") or ""))
            skills  = row.get("tech_skills_found") or []
            sal     = str(row.get("salary_str") or "")
            exp     = str(row.get("experience_level") or "")
            posted  = str(row.get("posted_date") or "")[:10]
            raw_url = str(row.get("job_url") or "")
          
            _m      = _re.search(r'https?://[^\s"\'<>]+', raw_url)
            safe_url = _html.escape(_m.group(0), quote=True) if _m else ""

            skills_html = "".join(f'<span class="skill">{_html.escape(str(s))}</span>' for s in (skills[:6] if isinstance(skills, list) else []))
            meta_parts = [loc, posted] if (posted and posted != "None") else [loc]
            meta_html  = " · ".join(f for f in meta_parts if f)

            badges = ""
            if sal and sal not in ("Not disclosed","Not Specified","None","nan"):
                badges += f'<span class="badge green">{_html.escape(sal)}</span>'
            if exp and exp not in ("Not specified","None","nan"):
                badges += f'<span class="badge amber">{_html.escape(exp)}</span>'

            apply_btn = f'<a class="apply" href="{safe_url}" target="_blank">View & Apply ↗</a>' if safe_url else ""
            title_linked = f'<a href="{safe_url}" target="_blank">{title}</a>' if safe_url else title

            st.markdown(f"""
            <div class="native-job-card">
                <div class="job-title">{title_linked}</div>
                <div class="company">{company}</div>
                <div class="meta">{meta_html}</div>
                <div class="pills">{badges}{skills_html}</div>
                {apply_btn}
            </div>
            """, unsafe_allow_html=True)
        # ──────────────────────────────────────────────────────────
        # ══════════════════════════════════════════════
        # PAGINATION BLOCK HERE:
        # ══════════════════════════════════════════════
        st.write("") # Spacer

        # 1. Inject custom CSS to pull native Streamlit buttons together tightly in the center
        st.markdown("""
            <style>
            /* Targets the horizontal row holding our pagination buttons */
            div[data-testid="stHorizontalBlock"]:has(button[key^="pg_"]) {
                justify-content: center !important; /* Forces buttons tightly to the center */
                gap: 6px !important;               /* Controls row item spacing */
                width: 100% !important;
            }
            /* Overrides full stretching behavior of native columns */
            div[data-testid="stHorizontalBlock"]:has(button[key^="pg_"]) > div {
                flex: 0 1 auto !important;
                min-width: unset !important;
                max-width: unset !important;
            }
            /* Clean up pagination sizes to look compact */
            div[data-testid="stHorizontalBlock"] button {
                border-radius: 8px !important;
                min-width: 38px !important;
                height: 38px !important;
                padding: 0 4px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
            }
            </style>
        """, unsafe_allow_html=True)

        # 2. Build our smart page numbers range array
        MAX_VISIBLE = 7
        half = MAX_VISIBLE // 2
        start_p = max(1, page_num - half)
        end_p   = min(total_pages, start_p + MAX_VISIBLE - 1)
        start_p = max(1, end_p - MAX_VISIBLE + 1)

        visible_pages = []
        for p in range(start_p, end_p + 1):
            visible_pages.append(p)

        # Create compact layout containers matching the count of items to render
        # We add 2 extra columns to hold our back (‹) and forward (›) arrow controls
        cols = st.columns([1] * (len(visible_pages) + 2))
        col_idx = 0

        def change_page(target_page):
            st.session_state["listing_page"] = target_page
            # Drops a temporary script onto the DOM forcing window.parent viewport reset
            components.html("<script>window.parent.scrollTo({top: 0, behavior: 'auto'});</script>", height=0)

        # Back Arrow Button
        with cols[col_idx]:
            if st.button("‹", key="pg_prev", disabled=(page_num == 1)):
                st.session_state["listing_page"] = max(1, page_num - 1)
                # Force browser view to reload view context to the top via query param mutation
                st.query_params["p"] = str(st.session_state["listing_page"])
                st.rerun()
        col_idx += 1

        # Numerical Buttons Loop
        for p in visible_pages:
            with cols[col_idx]:
                if st.button(
                    str(p), 
                    key=f"pg_{p}", 
                    type="primary" if p == page_num else "secondary"
                ):
                    st.session_state["listing_page"] = p
                    # Force browser view to reload view context to the top via query param mutation
                    st.query_params["p"] = str(p)
                    st.rerun()
            col_idx += 1

        # Forward Arrow Button
        with cols[col_idx]:
            if st.button("›", key="pg_next", disabled=(page_num == total_pages)):
                st.session_state["listing_page"] = min(total_pages, page_num + 1)
                # Force browser view to reload view context to the top via query param mutation
                st.query_params["p"] = str(st.session_state["listing_page"])
                st.rerun()
    # ══════════════════════════════════════════════
    #  TAB: MARKET OVERVIEW
    # ══════════════════════════════════════════════
    elif active == "market":
        c1, c2 = st.columns([3, 2])
    
        with c1:
            section_header("Top 15 In-Demand Technical Skills", "Frequency across all active listings")
            all_tech = []
            for sl in fdf["tech_skills_found"].dropna():
                if isinstance(sl, list):
                    all_tech.extend(sl)
            if all_tech:
                skill_counts = Counter(all_tech)
                skills_df = pd.DataFrame(skill_counts.most_common(15), columns=["Skill","Mentions"])
                n = len(skills_df)
                colors = [f"hsl({220 + i*4},{70 - i*2}%,{45 + i*2}%)" for i in range(n)]
                fig = go.Figure(go.Bar(
                    x=skills_df["Mentions"], y=skills_df["Skill"],
                    orientation="h",
                    marker=dict(color=colors, line=dict(width=0)),
                ))
                fig.update_layout(
                    **PLOTLY_LAYOUT_NO_AXES, height=460,
                    yaxis=dict(categoryorder="total ascending", **_AXIS_STYLE),
                    xaxis=_AXIS_STYLE,
                )
                st.plotly_chart(fig, use_container_width=True)
    
        with c2:
            section_header("Experience Level Distribution")
            exp_counts = (
                fdf["experience_level"].dropna()
                .value_counts()
                .reindex(["Internship","<1 Year","1-5 Years",">5 Years"])
                .dropna().reset_index()
            )
            exp_counts.columns = ["Level","Count"]
            if not exp_counts.empty:
                fig = go.Figure(go.Pie(
                    labels=exp_counts["Level"], values=exp_counts["Count"],
                    hole=0.52,
                    marker=dict(colors=["#3b82f6","#10b981","#f59e0b","#8b5cf6"],
                                line=dict(color="#0d0d0d", width=3)),
                    textinfo="label+percent", textposition="inside",
                    textfont=dict(size=11, color="#fff"),
                ))
                fig.update_layout(
                    **PLOTLY_LAYOUT_NO_AXES, height=460, showlegend=False,
                    annotations=[dict(
                        text=f"<b>{len(fdf)}</b><br><span style='font-size:11px'>listings</span>",
                        x=0.5, y=0.5, showarrow=False,
                        font=dict(size=16, family="Sora,sans-serif", color="#e0e0e0"),
                    )],
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # ══════════════════════════════════════════════
    #  TAB: SALARY INSIGHTS
    # ══════════════════════════════════════════════
    elif active == "salary":
        sal_fdf = fdf[fdf["salary_lpa"].notna()]
        if sal_fdf.empty:
            st.info("Not enough salary data for this filter.")
        else:
            section_header("Salary Distribution (LPA)", "Concentration of disclosed salary offers")
            fig = go.Figure(go.Histogram(
                x=sal_fdf["salary_lpa"], nbinsx=20,
                marker=dict(
                    color=sal_fdf["salary_lpa"],
                    colorscale=[[0,"#1a2744"],[0.5,"#3b82f6"],[1,"#60a5fa"]],
                    line=dict(color="#0d0d0d", width=1),
                ),
                hovertemplate="<b>%{x} LPA</b><br>Count: %{y}<extra></extra>",
            ))
            fig.update_layout(
                **PLOTLY_LAYOUT_NO_AXES, height=440, bargap=0.05,
                yaxis=_AXIS_STYLE, xaxis=_AXIS_STYLE,
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # ══════════════════════════════════════════════
    #  TAB: COMPANY INTELLIGENCE
    # ══════════════════════════════════════════════
    elif active == "companies":
        section_header("Top 20 Hiring Companies", "By volume of active postings")
        co_counts = fdf["company"].value_counts().head(20).reset_index()
        co_counts.columns = ["Company","Postings"]
        fig = go.Figure(go.Bar(
            x=co_counts["Postings"], y=co_counts["Company"],
            orientation="h",
            marker=dict(
                color=co_counts["Postings"],
                colorscale=[[0,"#1a2744"],[1,"#3b82f6"]],
                line=dict(width=0),
            ),
        ))
        fig.update_layout(
            **PLOTLY_LAYOUT_NO_AXES, height=520,
            yaxis=dict(categoryorder="total ascending", **_AXIS_STYLE),
            xaxis=_AXIS_STYLE,
        )
        st.plotly_chart(fig, use_container_width=True)
    
        section_header("Role Demand — Proportional View", "Top 15 roles by open positions")
        role_demand = fdf["title"].value_counts().head(15).reset_index()
        role_demand.columns = ["Role","Listings"]
        fig2 = px.treemap(
            role_demand, path=["Role"], values="Listings",
            color="Listings",
            color_continuous_scale=["#1a2744","#3b82f6"],
        )
        fig2.update_traces(textfont=dict(family="Inter,sans-serif", size=12, color="#fff"))
        fig2.update_layout(**PLOTLY_LAYOUT_NO_AXES, height=380)
        st.plotly_chart(fig2, use_container_width=True)
    
    # ══════════════════════════════════════════════
    #  TAB: GEOGRAPHIC HEAT MAP
    # ══════════════════════════════════════════════
    elif active == "map":
        map_df = build_map_data(fdf)
        if map_df.empty:
            st.info("No recognisable city names for this filter.")
        else:
            section_header("Geographic Distribution of Tech Hiring — India")
            fig = px.scatter_mapbox(
                map_df, lat="lat", lon="lon",
                size="openings", color="openings",
                
                # FIX: Clean, non-neon professional blue gradient scale
                color_continuous_scale=[
                    [0.0, "#94a3b8"],  # Low: Soft Slate Grey
                    [0.3, "#3b82f6"],  # Med-Low: Professional Blue
                    [0.7, "#1d4ed8"],  # Med-High: Deep Royal Blue
                    [1.0, "#1e3a8a"]   # High: Midnight Navy
                ],
                
                size_max=40, zoom=4.1, 
                center={"lat": 21.5937, "lon": 78.9629}, 
                mapbox_style="carto-positron", # Keeps the white map with city names active
                hover_name="city",
                hover_data={"openings":True,"lat":False,"lon":False},
                labels={"openings":"Open Positions"},
            )
            
            fig.update_layout(
                template="plotly_white", # Adapts fonts and layout parameters to look crisp on a light canvas
                paper_bgcolor="rgba(0,0,0,0)",
                margin={"r":0,"t":0,"l":0,"b":0}, height=580,
                coloraxis_colorbar=dict(
                    title="Listings", thickness=14, len=0.6,
                    tickfont=dict(size=11, family="Inter,sans-serif", color="#333"), # Dark gray text for visibility
                    title_font=dict(color="#333"),
                ),
            )
            st.plotly_chart(fig, use_container_width=True)
    # ══════════════════════════════════════════════
    #  TAB: AI SKILL GAP ANALYZER
    # ══════════════════════════════════════════════
    elif active == "ai_analyzer":
        section_header("🎯 AI Career Strategist & Persistent Skill Gap Analyzer")
        user_email = st.session_state.get("user_info", {}).get("email")
        
        # ─────────────────────────────────────────────────────────
        # 1. DATABASE INITIALIZATION LAYER (AUTO-FETCH ON LOAD)
        # ─────────────────────────────────────────────────────────
        if "profile_data" not in st.session_state or st.session_state["profile_data"] is None:
            try:
                with psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME) as conn:
                    with conn.cursor() as cur:
                        # Attempt to auto-restore profile parameters from AWS RDS
                        cur.execute("""
                            SELECT target_role, employment_preference, experience_level, salary_target, 
                                   work_history, education, skills, tools_and_infra, certifications, languages 
                            FROM user_profiles WHERE email = %s;
                        """, (user_email,))
                        prof_row = cur.fetchone()
                        
                        if prof_row:
                            st.session_state["profile_data"] = {
                                "role": prof_row[0], "employment_preference": prof_row[1],
                                "experience_level": prof_row[2], "salary_target": float(prof_row[3]),
                                "work_history": prof_row[4], "education": prof_row[5],
                                "skills": prof_row[6], "tools_and_infra": prof_row[7],
                                "certifications": prof_row[8], "languages": prof_row[9]
                            }
                            st.session_state["user_profile_saved"] = True
                            
                        # Attempt to auto-restore cached structured AI responses
                        cur.execute("SELECT raw_ai_json FROM ai_cached_strategies WHERE email = %s;", (user_email,))
                        ai_row = cur.fetchone()
                        if ai_row:
                            st.session_state["ai_analysis"] = ai_row[0]
            except Exception as db_init_err:
                st.error(f"Failed to query database cache profiles: {db_init_err}")

        if "user_profile_saved" not in st.session_state:
            st.session_state["user_profile_saved"] = False

        # ─────────────────────────────────────────────────────────
        # 2. ONBOARDING PROFILE FORM VIEW
        # ─────────────────────────────────────────────────────────
        if not st.session_state["user_profile_saved"]:
            st.markdown("""
                <div class='metric-card' style='margin-bottom: 25px;'>
                    <h3 style='color: #67e8f9; margin-top:0;'>Configure Global Intelligence Profile</h3>
                    <p style='color: #94a3b8; font-size: 0.9rem;'>
                        Complete your career objectives. Your profile variables will be securely synchronized to your cloud warehouse.
                    </p>
                </div>
            """, unsafe_allow_html=True)

            available_roles = sorted(list(set(str(r).strip() for r in fdf["title"].dropna() if str(r).strip())))
            options = ["Select from Market Roles..."] + available_roles + ["✨ Add Custom Role..."]

            with st.form("persistent_onboarding_form"):
                selected_role = st.selectbox("🎯 Target Career Objective", options=options)
                target_role = selected_role if selected_role != "Select from Market Roles..." else ""
                
                job_pref = st.selectbox("💼 Employment Preference", ["Full-time", "Remote / Freelance", "Internship"])
                exp_level = st.selectbox("Experience Level", ["Student / Fresher", "Entry-Level (1-2 Years)", "Mid-Level (3-5 Years)", "Senior (5+ Years)"])
                expected_salary = st.number_input("💰 Expected Annual Salary (INR)", min_value=0, step=50000)
                work_history = st.text_input("🏢 Past Job Roles (or N/A)")
                
                education = st.multiselect("🎓 Educational Qualifications", ["B.E. / B.Tech", "M.Tech / M.S.", "BCA", "MCA", "BSc / MSc", "Other"])
                skills_input = st.text_input("💻 Core Languages & Frameworks (comma separated)")
                tools_input = st.text_input("🛠️ Cloud & Infrastructure (comma separated)")
                certs_input = st.text_input("📜 Certifications (comma separated)")
                languages = st.multiselect("🗣️ Languages Spoken", ["English", "Hindi", "Other"])
                
                submit = st.form_submit_button("🚀 Compile and Synchronize Profile", use_container_width=True)
                
                if submit:
                    if not target_role or not skills_input or not tools_input or not education:
                        st.error("Please fill in mandatory fields.")
                    else:
                        skills_arr = [s.strip() for s in skills_input.split(",") if s.strip()]
                        tools_arr = [t.strip() for t in tools_input.split(",") if t.strip()]
                        certs_arr = [c.strip() for c in certs_input.split(",") if c.strip()]
                        
                        st.session_state["profile_data"] = {
                            "role": target_role, "employment_preference": job_pref, "experience_level": exp_level,
                            "salary_target": expected_salary, "work_history": work_history, "education": education,
                            "skills": skills_arr, "tools_and_infra": tools_arr, "certifications": certs_arr, "languages": languages
                        }
                        
                        # Write data variables directly into PostgreSQL DB
                        try:
                            with psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME) as conn:
                                with conn.cursor() as cur:
                                    cur.execute("""
                                        INSERT INTO user_profiles (email, target_role, employment_preference, experience_level, 
                                                                  salary_target, work_history, education, skills, tools_and_infra, certifications, languages)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                        ON CONFLICT (email) DO UPDATE SET
                                            target_role=EXCLUDED.target_role, employment_preference=EXCLUDED.employment_preference,
                                            experience_level=EXCLUDED.experience_level, salary_target=EXCLUDED.salary_target,
                                            work_history=EXCLUDED.work_history, education=EXCLUDED.education, skills=EXCLUDED.skills,
                                            tools_and_infra=EXCLUDED.tools_and_infra, certifications=EXCLUDED.certifications, languages=EXCLUDED.languages;
                                    """, (user_email, target_role, job_pref, exp_level, expected_salary, work_history, education, skills_arr, tools_arr, certs_arr, languages))
                                    conn.commit()
                            st.session_state["user_profile_saved"] = True
                            st.rerun()
                        except Exception as save_err:
                            st.error(f"Cloud write synchronization aborted: {save_err}")

        # ─────────────────────────────────────────────────────────
        # 3. STRATEGY AND METRICS RENDERING LAYER
        # ─────────────────────────────────────────────────────────
        if st.session_state["user_profile_saved"]:
            profile = st.session_state["profile_data"]
            
            if "ai_analysis" not in st.session_state:
                with st.spinner("⚡ Connecting with Gemini 3.5 Engine cluster for comprehensive blueprint..."):
                    try:
                        all_skills = fdf["tech_skills_found"].dropna().explode().unique().tolist() if "tech_skills_found" in fdf.columns else []
                        analysis_res = get_ai_analysis(profile, all_skills[:100])
                        
                        # Cache processed JSON schema directly into DB
                        with psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME) as conn:
                            with conn.cursor() as cur:
                                cur.execute("""
                                    INSERT INTO ai_cached_strategies (email, raw_ai_json) VALUES (%s, %s)
                                    ON CONFLICT (email) DO UPDATE SET raw_ai_json=EXCLUDED.raw_ai_json, generated_at=CURRENT_TIMESTAMP;
                                """, (user_email, json.dumps(analysis_res)))
                                conn.commit()
                        
                        st.session_state["ai_analysis"] = analysis_res
                    except Exception as err:
                        st.error(f"Analysis Generation Engine Failed: {err}")
                        if st.button("↩️ Return to Profile Setup"):
                            st.session_state["user_profile_saved"] = False
                            st.rerun()
                        st.stop()

            analysis = st.session_state["ai_analysis"]
            
            st.markdown(f"""
                <div style='background: #11111b; border: 1px solid #1e1e2f; border-radius: 12px; padding: 20px; margin-bottom: 25px;'>
                    <span style='background: #7c6ef5; color: white; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight:600;'>SECURE PERSISTENT REPORT</span>
                    <h2 style='margin-top: 10px; color: #fff;'>Strategic Roadmap: {profile['role']}</h2>
                    <p style='color: #6c6c8c; font-size: 13px; margin: 0;'>Cross-compiled against current live metrics from our database warehouse.</p>
                </div>
            """, unsafe_allow_html=True)

            # 📊 VISUALIZATION LAYER: TECHNICAL STRATEGY PRIORITY MATRIX
            if "skill_inventory_matrix" in analysis:
                st.write("### 📊 Market Priority Matrix")
                try:
                    matrix_df = pd.DataFrame(analysis["skill_inventory_matrix"])
                    
                    fig = px.bar(
                        matrix_df,
                        x="skill",
                        y="priority_score",
                        color="difficulty_level",
                        facet_col="category",
                        title="Skill Breakdown by Category and Priority Value",
                        labels={"priority_score": "Market Demand Weight", "skill": "Technology"},
                        color_discrete_map={"Advanced": "#f43f5e", "Intermediate": "#3b82f6", "Foundational": "#10b981", "Beginner": "#10b981"},
                        hover_data=["difficulty_level"]
                    )
                    
                    fig.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font_family="Inter",
                        xaxis={"categoryorder": "total descending"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as chart_err:
                    st.info(f"Visual Matrix rendering paused: {chart_err}")

            # ─── SKILL GAP & DETAILED ROADMAP GRID ───
            col_gap, col_road = st.columns([1, 2.1], gap="medium")
            
            with col_gap:
                st.markdown("### 🛠️ Key Technical Gaps")
                for gap in analysis.get('skill_gap', []):
                    st.markdown(f"""
                        <div style='background: #1a1118; border-left: 4px solid #f43f5e; padding: 12px; border-radius: 0 8px 8px 0; margin-bottom: 10px;'>
                            <p style='color: #fca5a5; font-size: 13px; font-weight: 500; margin: 0;'>{gap}</p>
                        </div>
                    """, unsafe_allow_html=True)

            with col_road:
                st.markdown("### 🗺️ Comprehensive Milestone Roadmap")
                for phase in analysis.get('structured_roadmap', []):
                    with st.expander(f"📌 Phase {phase.get('phase')}: {phase.get('phase_name')} ({phase.get('timeframe')})"):
                        st.markdown(f"**Objective:** {phase.get('core_objective')}")
                        st.markdown("**Detailed Action Deliverables:**")
                        for item in phase.get('action_items', []):
                            st.markdown(f"- {item}")
                        
                        st.markdown(f"""
                            <div style='background: #111827; border: 1px dashed #3b82f6; padding: 12px; border-radius: 6px; margin-top: 10px;'>
                                <span style='color: #60a5fa; font-size: 11px; font-weight: 600; text-transform: uppercase;'>PORTFOLIO CAPSTONE PROJECT</span>
                                <p style='color: #e5e7eb; font-size: 13px; margin: 4px 0 0 0;'>{phase.get('capstone_project')}</p>
                                <span style='color: #9ca3af; font-size: 11px;'>⏱️ Estimated Dedication: {phase.get('estimated_hours_required')} Hours</span>
                            </div>
                        """, unsafe_allow_html=True)

            # ─── HARD DATA FLUSH (RESET SYSTEM) ───
            st.markdown("<br><hr style='border-color: #252538;'>", unsafe_allow_html=True)
            if st.button("🔄 Purge Strategy Cache and Reset Profile", use_container_width=True):
                try:
                    with psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME) as conn:
                        with conn.cursor() as cur:
                            cur.execute("DELETE FROM ai_cached_strategies WHERE email = %s;", (user_email,))
                            cur.execute("DELETE FROM user_profiles WHERE email = %s;", (user_email,))
                            conn.commit()
                    
                    if "profile_data" in st.session_state: del st.session_state["profile_data"]
                    if "ai_analysis" in st.session_state: del st.session_state["ai_analysis"]
                    st.session_state["user_profile_saved"] = False
                    st.success("Cloud profiles successfully cleared from AWS database storage cells.")
                    st.rerun()
                except Exception as purge_err:
                    st.error(f"Purge request rejected by warehouse: {purge_err}")





    
