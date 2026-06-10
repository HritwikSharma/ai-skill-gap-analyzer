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
    #MainMenu, footer, header { visibility: hidden; }
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
    if st.session_state.get("filter_role") and st.session_state["filter_role"] != "All Roles":
        fdf = fdf[fdf["title_clean"] == st.session_state["filter_role"]] # Note: Using title_clean here to match your cleaned roles
        
    if st.session_state.get("filter_loc") and st.session_state["filter_loc"] != "All Locations":
        fdf = fdf[fdf["location"] == st.session_state["filter_loc"]]
        
    if st.session_state.get("filter_exp") and st.session_state["filter_exp"] != "All Experience":
        fdf = fdf[fdf["experience_level"] == st.session_state["filter_exp"]] # Note: Using experience_level here to match your normalized data
    # ──────────────────────────────────────────────────────────
    
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
    nav_interaction = components.html(f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
        body {{ margin: 0; padding: 0; background-color: transparent; font-family: 'Inter', sans-serif; }}
        .nav-container {{
            display: flex; gap: 4px; background-color: #0b0f19;
            padding: 4px; border-radius: 10px; border: 1px solid #1e293b;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4); width: fit-content; margin: 0 auto;
        }}
        .nav-item {{
            padding: 8px 16px; color: #94a3b8; border-radius: 7px;
            font-size: 0.85rem; font-weight: 500; cursor: pointer;
            transition: all 0.2s ease; user-select: none; text-decoration: none;
        }}
        .nav-item:hover {{ color: #ffffff; background-color: rgba(255,255,255,0.03); }}
        .nav-item.active {{
            color: #3b82f6; background-color: #1e293b;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.05); font-weight: 600;
        }}
    </style>
    </head>
    <body>
    <div class="nav-container" id="navbar"></div>
    <script>
        const links = [
            {{ id: 'listings', text: '📋 Job Listings' }},
            {{ id: 'market', text: '📊 Market Overview' }},
            {{ id: 'salary', text: '💰 Salary Insights' }},
            {{ id: 'companies', text: '🏢 Companies' }},
            {{ id: 'map', text: '🗺️ Heat Map' }},
            {{ id: 'ai_analyzer', text: '🎯 AI Analyzer' }} // ✅ FIXED: Link registered in HTML frame
        ];
        const activeTab = "{st.session_state["active_tab"]}";
        const container = document.getElementById('navbar');
        
        links.forEach(link => {{
            const div = document.createElement('div');
            div.className = 'nav-item' + (link.id === activeTab ? ' active' : '');
            div.innerText = link.text;
            div.onclick = () => {{
                window.parent.postMessage({{ type: 'streamlit:tab_change', value: link.id }}, '*');
            }};
            container.appendChild(div);
        }});
    </script>
    </body>
    </html>
    """, height=58)

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
    tab_options = ["listings", "market", "salary", "companies", "map","ai_analyzer"]
    default_index = tab_options.index(st.session_state["active_tab"])
    
    # Injected absolute layout overriding rules targeting global canvas paths
    st.markdown("""
        <style>
        /* 1. Target the outermost container element for the segmented control */
        div.element-container:has(div[data-testid="stSegmentedControl"]) {
            display: grid !important;
            justify-content: center !important;
            align-items: center !important;
            width: 100% !important;
            margin: 10px auto !important; /* Forces vertical spacing and absolute center */
        }
        
        /* 2. Target the block container to stop it from sticking left */
        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stSegmentedControl"]) {
            display: grid !important;
            justify-content: center !important;
            width: 100% !important;
            margin: 0 auto !important;
        }
        
        /* 3. Collapse width constraints so it wraps cleanly around button sizes */
        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stSegmentedControl"]) > div {
            flex: 0 1 auto !important;
            min-width: unset !important;
            max-width: unset !important;
            width: auto !important;
            margin: 0 auto !important;
        }

        /* 4. Center-align internal tracking rows inside the segmented control component */
        div[data-testid="stSegmentedControl"] {
            display: flex !important;
            width: auto !important;
            margin-left: 50px !important;
        }
        div[data-testid="stSegmentedControl"] > div {
            display: flex !important;
            width: auto !important;
            margin-left: 50px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Render the native, fully-functional selector
    selected_tab = st.segmented_control(
        "Navigation",
        options=tab_options,
        default=st.session_state["active_tab"],
        format_func=lambda x: {
            "listings": "📋 Job Listings",
            "market": "📊 Market Overview",
            "salary": "💰 Salary Insights",
            "companies": "🏢 Companies",
            "map": "🗺️ Heat Map",
            "ai_analyzer": "🎯 AI Skill Analyzer"
        }[x],
        label_visibility="collapsed"
    )
    
    # React instantly to user interaction without breaking the layout
    if selected_tab and selected_tab != st.session_state["active_tab"]:
        st.session_state["active_tab"] = selected_tab
        st.rerun()
    
    # Re-assign the active pointer variable used by the downstream IF/ELIF statements
    active = st.session_state["active_tab"]
    
    # ─────────────────────────────────────────────
    #  CONTENT AREA WRAPPER (shared padding)
    # ─────────────────────────────────────────────
    st.markdown("""
    <style>
    /* Content area gets dark bg + padding from the page wrap */
    .content-wrap {
        background: #0d0d0d;
        padding: 24px 32px 60px;
    }
    /* Plotly charts: override bg */
    .js-plotly-plot .plotly, .plot-container { background: transparent !important; }
    </style>
    <div class="content-wrap">
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
                color_continuous_scale=[[0,"#1a2744"],[0.4,"#3b82f6"],[0.7,"#06b6d4"],[1,"#67e8f9"]],
                size_max=55, zoom=4.0,
                center={"lat":20.5937,"lon":78.9629},
                mapbox_style="carto-darkmatter",
                hover_name="city",
                hover_data={"openings":True,"lat":False,"lon":False},
                labels={"openings":"Open Positions"},
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                margin={"r":0,"t":0,"l":0,"b":0}, height=580,
                coloraxis_colorbar=dict(
                    title="Listings", thickness=14, len=0.6,
                    tickfont=dict(size=11, family="Inter,sans-serif", color="#aaa"),
                    title_font=dict(color="#aaa"),
                ),
            )
            st.plotly_chart(fig, use_container_width=True)
    # ══════════════════════════════════════════════
    #  TAB: AI SKILL GAP ANALYZER & ASSESSMENT
    # ══════════════════════════════════════════════
    elif active == "ai_analyzer":
        section_header("🎯 AI Career Strategist & Skill Gap Analyzer")
        
        # Initialize Profile State tracking
        if "user_profile_saved" not in st.session_state:
            st.session_state["user_profile_saved"] = False
            
        if not st.session_state["user_profile_saved"]:
            st.markdown("""
                <div class='metric-card' style='margin-bottom: 25px;'>
                    <h3 style='color: #67e8f9; margin-top:0;'>Setup Your Career Profile</h3>
                    <p style='color: #94a3b8; font-size: 0.9rem; margin-bottom: 0;'>
                        Complete your career brief below. Our Groq-powered AI matching engine will cross-reference your stack against live Indian tech sector vacancy requirements to compile target skill deltas and generate an interactive tech stack simulation interview.
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            # --- Extract Unique Sorted Roles from Database ---
            available_roles = []
            if not fdf.empty and "title" in fdf.columns:
                raw_unique_roles = set(str(r).strip() for r in fdf["title"].dropna() if str(r).strip())
                available_roles = sorted(list(raw_unique_roles))
            
            # Fallback unique foundational options 
            fallback_roles = ["Data Scientist", "Data Analyst", "Machine Learning Engineer", "Frontend Developer", "Backend Developer", "Fullstack Engineer", "DevOps Engineer"]
            for role in fallback_roles:
                if role not in available_roles:
                    available_roles.append(role)

            # Custom styled input layout grouping wrapper
            with st.container():
                st.markdown("""
                    <style>
                    div[data-testid="stVerticalBlock"] label p {
                        color: #cbd5e1 !important;
                        font-weight: 500 !important;
                        font-size: 0.9rem !important;
                    }
                    div[data-testid="stSelectbox"] > div, div[data-testid="stTextInput"] > div {
                        background-color: #0b1329 !important;
                        border: 1px solid #1e293b !important;
                    }
                    </style>
                """, unsafe_allow_html=True)
                
                # Form Initialization
                with st.form("onboarding_profile_form", clear_on_submit=False):
                    
                    col_form_left, col_form_right = st.columns(2)
                    
                    with col_form_left:
                        # 1. Profile Mode Selection (Separates Dropdown vs Manual Entry cleanly to avoid resetting)
                        role_mode = st.radio(
                            "How would you like to specify your Target Role?",
                            options=["Choose from live market jobs", "Type a custom target role"],
                            horizontal=True
                        )
                        
                        final_target_role = ""
                        
                        if role_mode == "Choose from live market jobs":
                            selected_role_option = st.selectbox(
                                "Select Target Role",
                                options=available_roles,
                                index=0,
                                help="Choose from unique live roles scraped from your database."
                            )
                            final_target_role = selected_role_option
                        else:
                            custom_role_input = st.text_input(
                                "Type your custom target role",
                                placeholder="e.g., MLOps Engineer, Cloud Architect, GenAI Specialist",
                                help="Type any custom career objective title here without interruption."
                            )
                            final_target_role = custom_role_input
                        
                        # 2. Dropdown Experience level configuration
                        exp_level = st.selectbox(
                            "Current Professional Experience Level",
                            options=[
                                "Student / Fresher (0 Experience)", 
                                "Junior / Entry-Level (1-2 Years)", 
                                "Mid-Level Professional (3-5 Years)", 
                                "Senior / Lead Architect (5+ Years)"
                            ],
                            index=0
                        )
                        
                        # 3. Preferred Employment Hub Location
                        preferred_city = st.text_input(
                            "Target Job Market / City Preference",
                            placeholder="e.g., Bengaluru, Hyderabad, Mumbai, Remote",
                            help="Helps the AI match geographic tracking deltas for skill packages unique to specific tech hubs."
                        )

                    with col_form_right:
                    
                    if submit_profile:
                        if selected_role_option == "✨ Type my own custom role..." and not final_target_role:
                            st.error("Please specify your custom career objective title.")
                        elif not skills_input or not tools_input:
                            st.error("Please enter your current Core Languages and Infrastructure Tools to unlock your profile metrics matrix.")
                        else:
                            # Standard comma delimitation cleaning parser loop 
                            user_skills = [s.strip() for s in skills_input.split(",") if s.strip()]
                            user_tools = [t.strip() for t in tools_input.split(",") if t.strip()]
                            
                            # Compile structured dictionary parameters payload onto the app session layer
                            st.session_state["profile_data"] = {
                                "role": final_target_role,
                                "experience": exp_level,
                                "city": preferred_city if preferred_city else "All India Market",
                                "skills": user_skills,
                                "tools": user_tools,
                                "education": edu_background
                            }
                            st.session_state["user_profile_saved"] = True
                            st.success("Profile parsed successfully! Running AI core strategy metrics calculation routines...")
                            st.rerun()

                        
    st.markdown('</div>', unsafe_allow_html=True)



