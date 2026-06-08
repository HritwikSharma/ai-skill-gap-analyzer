import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import plotly.graph_objects as go
import json
import re
import re as _re
import html as _html
from collections import Counter

# ─────────────────────────────────────────────
#  DATABASE CREDENTIALS
# ─────────────────────────────────────────────
DB_HOST     = "job-db.clgqc6scelz7.eu-north-1.rds.amazonaws.com"
DB_USER     = "postgres"
DB_NAME     = "postgres"
DB_PASSWORD = "HRITWIKSHARMA"

# ─────────────────────────────────────────────
#  GLOBAL THEME & STYLE INJECTION
# ─────────────────────────────────────────────
st.set_page_config(
    page_title  = "TalentPulse — India Tech Market Intelligence",
    page_icon   = "📊",
    layout      = "wide",
    initial_sidebar_state = "collapsed",
)

THEME = """
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Sora:wght@400;600;700&display=swap');

/* ── Root palette ── */
:root {
    --blue-primary  : #0A66C2;
    --blue-hover    : #004182;
    --blue-light    : #EBF3FB;
    --surface       : #FFFFFF;
    --surface-2     : #F3F2EF;
    --border        : #E0DFDC;
    --text-primary  : #191919;
    --text-secondary: #666666;
    --text-muted    : #999999;
    --green         : #057642;
    --green-light   : #E9F5EE;
    --amber         : #B24020;
    --shadow-sm     : 0 1px 3px rgba(0,0,0,.08), 0 1px 2px rgba(0,0,0,.04);
    --shadow-md     : 0 4px 12px rgba(0,0,0,.10);
    --radius        : 8px;
    --font-sans     : 'Inter', sans-serif;
    --font-display  : 'Sora', sans-serif;
}

/* ── Reset & base — force white/light background ── */
html, body,
[class*="css"],
.stApp,
.main,
.block-container,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stMainBlockContainer"],
[data-testid="stMain"],
[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"] {
    font-family  : var(--font-sans) !important;
    color        : var(--text-primary) !important;
    background   : var(--surface-2) !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stMainBlockContainer"] { padding: 0 !important; }
[data-testid="stAppViewBlockContainer"] { padding: 0 !important; }
[data-testid="stMain"] { padding: 0 !important; }

/* Kill top spacing and ghost elements */
.stApp > div:first-child,
[data-testid="stAppViewContainer"] > section > div:first-child {
    padding-top: 0 !important;
}
[data-testid="stVerticalBlock"] > div:first-child,
[data-testid="stVerticalBlock"] > div:empty {
    padding: 0 !important;
    margin: 0 !important;
    min-height: 0 !important;
}
[data-testid="stMarkdownContainer"]:empty,
div.element-container:empty,
div.element-container:has(> div:empty) {
    display: none !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}
section[data-testid="stSidebar"] { display: none; }

/* ── Top navigation bar ── */
.nav-bar {
    position       : sticky;
    top             : 0;
    z-index         : 1000;
    background      : var(--surface);
    border-bottom   : 1px solid var(--border);
    display         : flex;
    align-items     : center;
    justify-content : space-between;
    padding         : 0 32px;
    height          : 52px;
    box-shadow      : var(--shadow-sm);
}
.nav-logo {
    font-family : var(--font-display);
    font-size   : 1.15rem;
    font-weight : 700;
    color       : var(--blue-primary);
    letter-spacing: -.02em;
}
.nav-logo span { color: var(--text-primary); font-weight: 400; }
.nav-tag {
    font-size   : 0.72rem;
    font-weight : 600;
    color       : var(--text-muted);
    letter-spacing: .08em;
    text-transform: uppercase;
}

/* ── Page wrapper ── */
.page-wrap {
    max-width   : 1280px;
    margin      : 0 auto;
    padding     : 0 24px 60px;
}

/* ── Section header ── */
.section-header {
    font-family : var(--font-display);
    font-size   : 1.1rem;
    font-weight : 600;
    color       : var(--text-primary);
    margin-bottom: 16px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
}

/* ── KPI cards ── */
.kpi-grid {
    display              : grid;
    grid-template-columns: repeat(4, 1fr);
    gap                  : 14px;
    margin-bottom        : 28px;
}
.kpi-card {
    background    : var(--surface);
    border        : 1px solid var(--border);
    border-radius : var(--radius);
    padding       : 20px 22px;
    box-shadow    : var(--shadow-sm);
    transition    : box-shadow .2s;
}
.kpi-card:hover { box-shadow: var(--shadow-md); }
.kpi-label {
    font-size   : 0.72rem;
    font-weight : 600;
    color       : var(--text-muted);
    letter-spacing: .06em;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.kpi-value {
    font-family : var(--font-display);
    font-size   : 1.75rem;
    font-weight : 700;
    color       : var(--text-primary);
    line-height : 1;
}
.kpi-sub {
    font-size  : 0.77rem;
    color      : var(--text-secondary);
    margin-top : 5px;
}
.kpi-accent { color: var(--blue-primary); }

/* ── Chart cards ── */
.chart-card {
    background    : var(--surface);
    border        : 1px solid var(--border);
    border-radius : var(--radius);
    padding       : 22px 22px 10px;
    box-shadow    : var(--shadow-sm);
    margin-bottom : 18px;
}
.chart-title {
    font-size    : 0.85rem;
    font-weight  : 600;
    color        : var(--text-secondary);
    letter-spacing: .04em;
    text-transform: uppercase;
    margin-bottom: 14px;
}

/* ── Filter bar ── */
/* ── Filter bar ── */
.filter-bar {
    display: none !important;
}
[data-testid="stHorizontalBlock"]:first-of-type {
    background    : var(--surface);
    border        : 1px solid var(--border);
    border-radius : var(--radius);
    padding       : 14px 20px;
    margin-bottom : 22px;
    box-shadow    : var(--shadow-sm);
    align-items   : center;
}

/* ── Job listing cards ── */
.job-card {
    background    : var(--surface);
    border        : 1px solid var(--border);
    border-radius : var(--radius);
    padding       : 18px 20px;
    margin-bottom : 10px;
    box-shadow    : var(--shadow-sm);
    transition    : box-shadow .2s, border-color .2s;
}
.job-card:hover {
    box-shadow   : var(--shadow-md);
    border-color : #b8d0e8;
}
.job-title {
    font-size   : 1rem;
    font-weight : 600;
    color       : var(--blue-primary);
    margin-bottom: 2px;
}
.job-title a {
    color          : var(--blue-primary);
    text-decoration: none;
}
.job-title a:hover { text-decoration: underline; }
.job-company {
    font-size   : 0.88rem;
    font-weight : 500;
    color       : var(--text-primary);
    margin-bottom: 3px;
}
.job-meta {
    font-size : 0.8rem;
    color     : var(--text-secondary);
    display   : flex;
    gap       : 16px;
    flex-wrap : wrap;
    margin-bottom: 10px;
}
.job-meta-item::before {
    content       : "";
    display       : inline-block;
    width         : 4px;
    height        : 4px;
    border-radius : 50%;
    background    : var(--text-muted);
    vertical-align: middle;
    margin-right  : 6px;
}
.job-meta-item:first-child::before { display: none; }
.job-skills {
    display  : flex;
    gap      : 6px;
    flex-wrap: wrap;
    margin-top: 8px;
}
.skill-pill {
    background    : var(--blue-light);
    color         : var(--blue-primary);
    font-size     : 0.72rem;
    font-weight   : 600;
    padding       : 3px 9px;
    border-radius : 20px;
    letter-spacing: .02em;
}
.salary-badge {
    background  : var(--green-light);
    color       : var(--green);
    font-size   : 0.72rem;
    font-weight : 600;
    padding     : 3px 9px;
    border-radius: 20px;
}
.exp-badge {
    background   : #FFF3E0;
    color        : #E65100;
    font-size    : 0.72rem;
    font-weight  : 600;
    padding      : 3px 9px;
    border-radius: 20px;
}
.apply-btn {
    display       : inline-block;
    margin-top    : 10px;
    background    : var(--blue-primary);
    color         : #fff !important;
    font-size     : 0.8rem;
    font-weight   : 600;
    padding       : 6px 16px;
    border-radius : 20px;
    text-decoration: none;
    transition    : background .2s;
}
.apply-btn:hover { background: var(--blue-hover); text-decoration: none; }

/* ── Pagination ── */
.pagination-wrap {
    display    : flex;
    gap        : 6px;
    flex-wrap  : wrap;
    margin     : 12px 0 18px;
    align-items: center;
}
.page-btn {
    display        : inline-block;
    min-width      : 34px;
    height         : 34px;
    line-height    : 34px;
    text-align     : center;
    border-radius  : 6px;
    border         : 1px solid var(--border);
    background     : var(--surface);
    color          : var(--text-primary);
    font-size      : 0.82rem;
    font-weight    : 500;
    cursor         : pointer;
    text-decoration: none;
    padding        : 0 10px;
    transition     : background .15s, border-color .15s;
}
.page-btn:hover { background: var(--blue-light); border-color: var(--blue-primary); text-decoration: none; }
.page-btn.active {
    background  : var(--blue-primary);
    color       : #fff;
    border-color: var(--blue-primary);
    font-weight : 700;
}

/* ── Tab styling — always visible, not just on hover ── */
[data-testid="stTabs"] {
    background   : var(--surface);
    border-radius: var(--radius) var(--radius) 0 0;
}

/* Tab list container */
[data-testid="stTabs"] > div:first-child,
div[data-baseweb="tab-list"] {
    background   : var(--surface) !important;
    border-bottom: 2px solid var(--border) !important;
    gap          : 0 !important;
    padding      : 0 8px !important;
}

/* Individual tabs — always show text in dark color */
div[data-baseweb="tab"],
button[data-baseweb="tab"],
[role="tab"] {
    font-family  : var(--font-sans) !important;
    font-size    : 0.88rem !important;
    font-weight  : 500 !important;
    color        : var(--text-secondary) !important;
    background   : transparent !important;
    padding      : 12px 20px !important;
    border-bottom: 3px solid transparent !important;
    transition   : color .15s, border-color .15s !important;
    white-space  : nowrap !important;
    opacity      : 1 !important;
}

/* Hover state */
div[data-baseweb="tab"]:hover,
button[data-baseweb="tab"]:hover,
[role="tab"]:hover {
    color        : var(--blue-primary) !important;
    border-bottom: 3px solid #BAD7F5 !important;
    background   : var(--blue-light) !important;
}

/* Active / selected tab */
div[data-baseweb="tab"][aria-selected="true"],
button[data-baseweb="tab"][aria-selected="true"],
[role="tab"][aria-selected="true"] {
    color        : var(--blue-primary) !important;
    border-bottom: 3px solid var(--blue-primary) !important;
    font-weight  : 600 !important;
    background   : transparent !important;
}

/* Tab content area */
div[data-testid="stTabContent"],
[data-baseweb="tab-panel"] {
    background   : var(--surface-2) !important;
    padding-top  : 24px !important;
}

/* ── Selectbox / multiselect ── */
div[data-baseweb="select"] > div:first-child {
    border-color  : var(--border) !important;
    border-radius : var(--radius) !important;
    font-size     : 0.85rem !important;
    min-height    : 38px !important;
    background    : var(--surface) !important;
}

/* Selectbox label text */
div[data-baseweb="select"] span,
div[data-baseweb="select"] div {
    color : var(--text-primary) !important;
}

/* ── Hide number input widget ── */
/* ── Hide number input widget ── */
[data-testid="stNumberInput"] {
    display: none !important;
}

/* ── Pagination buttons ── */
[data-testid="stHorizontalBlock"] button[kind="secondary"] {
    background    : var(--surface) !important;
    color         : var(--text-primary) !important;
    border        : 1px solid var(--border) !important;
    border-radius : 6px !important;
    font-size     : 0.82rem !important;
    font-weight   : 500 !important;
}
[data-testid="stHorizontalBlock"] button[kind="secondary"]:hover {
    background    : var(--blue-light) !important;
    border-color  : var(--blue-primary) !important;
    color         : var(--blue-primary) !important;
}
[data-testid="stHorizontalBlock"] button[kind="primary"] {
    background    : var(--blue-primary) !important;
    color         : #fff !important;
    border        : 1px solid var(--blue-primary) !important;
    border-radius : 6px !important;
    font-size     : 0.82rem !important;
    font-weight   : 700 !important;
}

/* ── Responsive ── */
@media (max-width: 900px) {
    .kpi-grid { grid-template-columns: repeat(2,1fr); }
}
@media (max-width: 560px) {
    .kpi-grid { grid-template-columns: 1fr; }
}
</style>
"""

st.markdown(THEME, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PLOTLY BASE TEMPLATE (shared across all charts)
# ─────────────────────────────────────────────
_AXIS_STYLE = dict(gridcolor="#EEEDE9", linecolor="#E0DFDC", tickfont=dict(size=11, color="#191919"))

PLOTLY_LAYOUT = dict(
    font         = dict(family="Inter, sans-serif", color="#191919"),
    paper_bgcolor= "rgba(0,0,0,0)",
    plot_bgcolor = "#FFFFFF",
    margin       = dict(l=8, r=8, t=36, b=8),
    title_font   = dict(size=13, color="#666666", family="Inter, sans-serif"),
    xaxis        = _AXIS_STYLE,
    yaxis        = _AXIS_STYLE,
    colorway     = ["#0A66C2","#057642","#B24020","#7B5EA7","#D48806","#0891B2"],
)

PLOTLY_LAYOUT_NO_AXES = {k: v for k, v in PLOTLY_LAYOUT.items() if k not in ("xaxis", "yaxis")}

# ─────────────────────────────────────────────
#  DATA FETCHING
# ─────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_job_data():
    try:
        conn = psycopg2.connect(
            host=DB_HOST, user=DB_USER, database=DB_NAME,
            password=DB_PASSWORD, port="5432"
        )
        query = """
            SELECT job_id, title, company, location,
                   tech_skills_found, soft_skills_found,
                   extra_metadata, job_url
            FROM job_listings;
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return pd.DataFrame()


# ─────────────────────────────────────────────
#  HELPER — parse salary string → numeric
# ─────────────────────────────────────────────
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


# ─────────────────────────────────────────────
#  INDIAN CITY COORDINATES
# ─────────────────────────────────────────────
CITY_COORDS = {
    "bengaluru": (12.9716, 77.5946), "bangalore": (12.9716, 77.5946),
    "hyderabad": (17.3850, 78.4867),
    "pune":      (18.5204, 73.8567),
    "mumbai":    (19.0760, 72.8777), "bombay": (19.0760, 72.8777),
    "chennai":   (13.0827, 80.2707), "madras": (13.0827, 80.2707),
    "delhi":     (28.6139, 77.2090), "new delhi": (28.6139, 77.2090),
    "gurugram":  (28.4595, 77.0266), "gurgaon": (28.4595, 77.0266),
    "noida":     (28.5355, 77.3910),
    "kolkata":   (22.5726, 88.3639), "calcutta": (22.5726, 88.3639),
    "ahmedabad": (23.0225, 72.5714),
    "jaipur":    (26.9124, 75.7873),
    "coimbatore":(11.0168, 76.9558),
    "kochi":     (9.9312, 76.2673),  "cochin": (9.9312, 76.2673),
    "thiruvananthapuram": (8.5241, 76.9366), "trivandrum": (8.5241, 76.9366),
    "lucknow":   (26.8467, 80.9462),
    "chandigarh":(30.7333, 76.7794),
    "indore":    (22.7196, 75.8577),
    "bhopal":    (23.2599, 77.4126),
    "nagpur":    (21.1458, 79.0882),
    "surat":     (21.1702, 72.8311),
    "visakhapatnam": (17.6868, 83.2185), "vizag": (17.6868, 83.2185),
    "bhubaneswar":(20.2961, 85.8245),
    "patna":     (25.5941, 85.1376),
    "vadodara":  (22.3072, 73.1812),
    "mysuru":    (12.2958, 76.6394), "mysore": (12.2958, 76.6394),
    "mangaluru": (12.9141, 74.8560), "mangalore": (12.9141, 74.8560),
    "remote":    (20.5937, 78.9629),
    "india":     (20.5937, 78.9629),
}
EXCLUDE_MAP = {"remote", "india"}

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


# ─────────────────────────────────────────────
#  EXPERIENCE LEVEL NORMALISER
# ─────────────────────────────────────────────
EXP_KEEP = {"Internship", "<1 Year", "1-5 Years", ">5 Years"}

def normalise_exp(val):
    """Map raw experience_level strings to the 4 desired buckets."""
    if not val or str(val).strip().lower() in ("not specified", "none", "nan", ""):
        return None
    v = str(val).strip()
    v_lower = v.lower()
    if "intern" in v_lower:
        return "Internship"
    nums = re.findall(r"\d+", v)
    if not nums:
        return None
    n = int(nums[0])
    if n == 0:
        return "<1 Year"
    if 1 <= n <= 5:
        return "1-5 Years"
    if n > 5:
        return ">5 Years"
    return None


# ─────────────────────────────────────────────
#  NAV BAR
# ─────────────────────────────────────────────
st.markdown("""
<div class="nav-bar">
    <div class="nav-logo">TalentPulse <span>India</span></div>
    <div class="nav-tag">Tech Market Intelligence</div>
</div>
<div class="page-wrap">
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  LOAD & ENRICH DATA
# ─────────────────────────────────────────────
df_raw = fetch_job_data()

if df_raw.empty:
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    st.warning("No data available. Verify the AWS RDS connection and pipeline run.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

df = extract_metadata_fields(df_raw.copy())

#df["job_url"] = df["job_url"].apply(clean_job_url)

# Normalise experience level
df["experience_level"] = df["experience_level"].apply(normalise_exp)

# ─────────────────────────────────────────────
#  FILTER ROW
# ─────────────────────────────────────────────
fc1, fc2, fc3 = st.columns([2, 2, 1])
with fc1:
    role_options = ["All Roles"] + sorted(df["title"].dropna().unique().tolist())
    selected_role = st.selectbox("Role", role_options, label_visibility="collapsed")
with fc2:
    loc_options = ["All Locations"] + sorted(df["location"].dropna().unique().tolist())
    selected_loc = st.selectbox("Location", loc_options, label_visibility="collapsed")
with fc3:
    exp_options = ["All Experience"] + ["Internship", "<1 Year", "1-5 Years", ">5 Years"]
    selected_exp = st.selectbox("Experience", exp_options, label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# Apply filters
fdf = df.copy()
if selected_role != "All Roles":
    fdf = fdf[fdf["title"] == selected_role]
if selected_loc != "All Locations":
    fdf = fdf[fdf["location"] == selected_loc]
if selected_exp != "All Experience":
    fdf = fdf[fdf["experience_level"] == selected_exp]

# ─────────────────────────────────────────────
#  KPI ROW
# ─────────────────────────────────────────────
total_jobs    = len(fdf)
unique_cos    = fdf["company"].nunique()
top_loc_val   = fdf["location"].mode().iloc[0] if not fdf["location"].mode().empty else "N/A"
sal_data      = fdf["salary_lpa"].dropna()
avg_sal_str   = f"{sal_data.mean():.1f} LPA" if not sal_data.empty else "N/A"

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card">
        <div class="kpi-label">Active Listings</div>
        <div class="kpi-value kpi-accent">{total_jobs:,}</div>
        <div class="kpi-sub">Across all tracked roles</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Unique Employers</div>
        <div class="kpi-value">{unique_cos:,}</div>
        <div class="kpi-sub">Companies currently hiring</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Avg. Salary</div>
        <div class="kpi-value">{avg_sal_str}</div>
        <div class="kpi-sub">Based on disclosed listings</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Top Hiring Hub</div>
        <div class="kpi-value" style="font-size:1.2rem;padding-top:6px;">{top_loc_val}</div>
        <div class="kpi-sub">Highest concentration</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────
tab_listings, tab_market, tab_salary, tab_companies, tab_map = st.tabs([
    "📋  Job Listings",
    "📊  Market Overview",
    "💰  Salary Insights",
    "🏢  Company Intelligence",
    "🗺️  Geographic Heat Map",
])

# ══════════════════════════════════════════════
#  TAB 1 — MARKET OVERVIEW
# ══════════════════════════════════════════════
with tab_market:
    c1, c2 = st.columns([3, 2])

    # ── Chart 1: Top 15 Technical Skills ──
    with c1:
        st.markdown('<div class="chart-card"><div class="chart-title">Top 15 In-Demand Technical Skills</div>', unsafe_allow_html=True)

        all_tech = []
        for sl in fdf["tech_skills_found"].dropna():
            if isinstance(sl, list):
                all_tech.extend(sl)

        if all_tech:
            skill_counts = Counter(all_tech)
            skills_df = pd.DataFrame(skill_counts.most_common(15), columns=["Skill", "Mentions"])

            # Rich teal-to-indigo gradient — distinct from the plain blue default
            SKILL_COLORS = [
                "#0D47A1","#1565C0","#1976D2","#1E88E5","#2196F3",
                "#42A5F5","#1565C0","#0277BD","#01579B","#006064",
                "#00838F","#00ACC1","#26C6DA","#4DD0E1","#80DEEA",
            ]
            # Assign colour by rank (darkest = most mentions)
            n = len(skills_df)
            bar_colors = SKILL_COLORS[:n][::-1]  # lightest at top (lowest), darkest at bottom (highest)

            fig_skills = go.Figure(go.Bar(
                x=skills_df["Mentions"],
                y=skills_df["Skill"],
                orientation="h",
                marker=dict(color=bar_colors, line=dict(width=0)),
                #hovertemplate="<b>%{y}</b><br>%{x} postings<extra></extra>",
            ))
            fig_skills.update_layout(
                **PLOTLY_LAYOUT_NO_AXES,
                height=460,
                title="Frequency across all active listings",
                hoverlabel=dict(bgcolor="#FFFFFF", font_color="#191919", font_size=12,
                                font_family="Inter, sans-serif", bordercolor="#E0DFDC"),
                yaxis=dict(categoryorder="total ascending", tickfont=dict(size=11, color="#191919"),
                           gridcolor="#EEEDE9", linecolor="#E0DFDC"),
                xaxis=dict(gridcolor="#EEEDE9", linecolor="#E0DFDC", tickfont=dict(size=11, color="#191919")),
            )
            st.plotly_chart(fig_skills, use_container_width=True)
        else:
            st.info("No skill data available for this filter set.")

    # ── Chart 2: Experience Level Donut ──
    with c2:
        st.markdown('<div class="chart-title">Experience Level Distribution</div>', unsafe_allow_html=True)

        # Only the 4 buckets; Not Specified already mapped to None above
        exp_counts = (
            fdf["experience_level"]
            .dropna()
            .value_counts()
            .reindex(["Internship", "<1 Year", "1-5 Years", ">5 Years"])
            .dropna()
            .reset_index()
        )
        exp_counts.columns = ["Level", "Count"]

        if not exp_counts.empty:
            EXP_COLORS = ["#0A66C2", "#057642", "#D48806", "#B24020"]

            fig_exp = go.Figure(go.Pie(
                labels=exp_counts["Level"],
                values=exp_counts["Count"],
                hole=0.52,
                marker=dict(
                    colors=EXP_COLORS[:len(exp_counts)],
                    line=dict(color="#FFFFFF", width=2),
                ),
                textinfo="label+percent",
                textposition="inside",
                insidetextorientation="radial",
                textfont=dict(size=11, family="Inter, sans-serif", color="#FFFFFF"),
                hovertemplate="<b>%{label}</b><br>%{value} jobs (%{percent})<extra></extra>",
            ))
            fig_exp.update_layout(
                **PLOTLY_LAYOUT_NO_AXES,
                height=460,
                showlegend=False,
                annotations=[dict(
                    text=f"<b>{len(fdf)}</b><br><span style='font-size:10px'>listings</span>",
                    x=0.5, y=0.5, font_size=15, showarrow=False,
                )],
            )
            st.plotly_chart(fig_exp, use_container_width=True)
        else:
            st.info("No experience data available.")


# ══════════════════════════════════════════════
#  TAB 2 — SALARY INSIGHTS
#  Keep: Overall Salary Distribution (LPA)
#  Remove: Salary Range by Role, Avg Salary by Experience
# ══════════════════════════════════════════════
with tab_salary:
    sal_fdf = fdf[fdf["salary_lpa"].notna()]

    if sal_fdf.empty:
        st.info("Salary data is not disclosed in enough listings for this filter.")
    else:
        st.markdown('<div class="chart-title">Overall Salary Distribution (LPA)</div>', unsafe_allow_html=True)

        fig_hist = go.Figure(go.Histogram(
            x=sal_fdf["salary_lpa"],
            nbinsx=20,
            marker=dict(
                color=sal_fdf["salary_lpa"],
                colorscale=[[0, "#A5D6F5"], [0.5, "#0A66C2"], [1, "#003070"]],
                line=dict(color="#FFFFFF", width=1),
            ),
            hovertemplate="<b>Range: %{x} LPA</b><br>Count: %{y}<extra></extra>",
            texttemplate="%{y}",
            textposition="outside",
            textfont=dict(size=11, color="#191919"),
        ))
        fig_hist.update_layout(
            **PLOTLY_LAYOUT_NO_AXES,
            height=440,
            title="Concentration of salary offers",
            bargap=0.05,
            uniformtext=dict(mode="hide", minsize=9),
            yaxis=dict(gridcolor="#EEEDE9", linecolor="#E0DFDC", tickfont=dict(size=11, color="#191919")),
            xaxis=dict(gridcolor="#EEEDE9", linecolor="#E0DFDC", tickfont=dict(size=11, color="#191919")),
        )
        st.plotly_chart(fig_hist, use_container_width=True)


# ══════════════════════════════════════════════
#  TAB 3 — COMPANY INTELLIGENCE
#  Keep: Top 20 Hiring Companies, Role Demand Treemap (top 15)
#  Remove: Role Diversity chart
# ══════════════════════════════════════════════
with tab_companies:
    # ── Top 20 companies by posting volume ──
    st.markdown('<div class="chart-title">Top 20 Hiring Companies</div>', unsafe_allow_html=True)

    co_counts = fdf["company"].value_counts().head(20).reset_index()
    co_counts.columns = ["Company", "Postings"]

    fig_co = go.Figure(go.Bar(
        x=co_counts["Postings"],
        y=co_counts["Company"],
        orientation="h",
        marker=dict(
            color=co_counts["Postings"],
            colorscale=[[0, "#BAD7F5"], [1, "#0A66C2"]],
            line=dict(width=0),
        ),
        #hovertemplate="<b>%{y}</b><br>%{x} listings<extra></extra>",
    ))
    fig_co.update_layout(
        **PLOTLY_LAYOUT_NO_AXES,
        height=520,
        title="Volume of active job postings",
        hoverlabel=dict(bgcolor="#FFFFFF", font_color="#191919", font_size=12,
                font_family="Inter, sans-serif", bordercolor="#E0DFDC"),
        yaxis=dict(categoryorder="total ascending", tickfont=dict(size=11, color="#191919"),
                   gridcolor="#EEEDE9", linecolor="#E0DFDC"),
        xaxis=dict(gridcolor="#EEEDE9", linecolor="#E0DFDC", tickfont=dict(size=11, color="#191919")),
    )
    st.plotly_chart(fig_co, use_container_width=True)

    # ── Role demand treemap — top 15 only ──
    st.markdown('<div class="chart-title">Role Demand — Proportional View</div>', unsafe_allow_html=True)

    role_demand = fdf["title"].value_counts().head(15).reset_index()
    role_demand.columns = ["Role", "Listings"]

    fig_tree = px.treemap(
        role_demand, path=["Role"], values="Listings",
        color="Listings",
        color_continuous_scale=["#EBF3FB", "#0A66C2"],
    )
    fig_tree.update_traces(
        textfont=dict(family="Inter, sans-serif", size=12),
        hovertemplate="<b>%{label}</b><br>%{value} listings<extra></extra>",
    )
    fig_tree.update_layout(
        **PLOTLY_LAYOUT_NO_AXES,
        height=380,
        title="Top 15 roles — relative size reflects open positions",
    )
    st.plotly_chart(fig_tree, use_container_width=True)


# ══════════════════════════════════════════════
#  TAB 4 — GEOGRAPHIC HEAT MAP
#  Remove: City Hiring Leaderboard
# ══════════════════════════════════════════════
with tab_map:
    map_df = build_map_data(fdf)

    if map_df.empty:
        st.info("No recognisable Indian city names found in the location field for this filter set.")
    else:
        st.markdown('<div class="chart-title">Geographic Distribution of Tech Hiring — India</div>',
                    unsafe_allow_html=True)

        fig_map = px.scatter_mapbox(
            map_df,
            lat="lat", lon="lon",
            size="openings",
            color="openings",
            # True gradient heatmap: yellow → orange → red → dark red
            color_continuous_scale=[
                [0.0,  "#FEB24C"],
                [0.25, "#FD8D3C"],
                [0.5,  "#FC4E2A"],
                [0.75, "#E31A1C"],
                [1.0,  "#67000D"],
            ],
            size_max=55,
            zoom=4.0,
            center={"lat": 20.5937, "lon": 78.9629},
            mapbox_style="carto-positron",
            hover_name="city",
            hover_data={"openings": True, "lat": False, "lon": False},
            labels={"openings": "Open Positions"},
        )
        fig_map.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            height=580,
            hoverlabel=dict(bgcolor="#FFFFFF", font_color="#191919", font_size=12,
                font_family="Inter, sans-serif", bordercolor="#E0DFDC"),
            coloraxis_colorbar=dict(
                title="Listings",
                thickness=14,
                len=0.6,
                tickfont=dict(size=11, family="Inter, sans-serif"),
            ),
        )
        st.plotly_chart(fig_map, use_container_width=True)


# ══════════════════════════════════════════════
#  TAB 5 — JOB LISTINGS
#  Numbered pagination, fixed apply button
# ══════════════════════════════════════════════
with tab_listings:
    st.markdown(
        f'<div style="font-size:0.82rem;color:#666;margin-bottom:16px;">'
        f'Showing <strong>{len(fdf)}</strong> listings matching your filters</div>',
        unsafe_allow_html=True,
    )

    PAGE_SIZE   = 20
    total_pages = max(1, (len(fdf) - 1) // PAGE_SIZE + 1)

    # Hidden number_input drives the page state; the HTML buttons below call
    # st.query_params to read the current page from URL or session_state.
    if "listing_page" not in st.session_state:
        st.session_state["listing_page"] = 1

    page_num = st.session_state["listing_page"]

    # ── Pagination buttons (top) ──
    start  = (page_num - 1) * PAGE_SIZE
    page_df = fdf.iloc[start: start + PAGE_SIZE]
    
    for _, row in page_df.iterrows():
        title   = _html.escape(str(row.get("title") or "Untitled"))
        company = _html.escape(str(row.get("company") or "Unknown Company"))
        loc     = _html.escape(str(row.get("location") or "Location not specified"))
        skills  = row.get("tech_skills_found") or []
        sal     = str(row.get("salary_str") or "Not disclosed")
        exp     = str(row.get("experience_level") or "Not specified")
        posted  = str(row.get("posted_date") or "")[:10]

        raw_url = str(row.get("job_url") or "")
        _m = _re.search(r'https?://[^\s"\'<>]+', raw_url)
        safe_url = _html.escape(_m.group(0), quote=True) if _m else ""
        
        skills_html = "".join(
            f'<span class="skill-pill">{_html.escape(str(s))}</span>'
            for s in (skills[:6] if isinstance(skills, list) else [])
        )

        sal_badge  = f'<span class="salary-badge">{_html.escape(sal)}</span>' if sal != "Not disclosed" else ""
        exp_badge  = f'<span class="exp-badge">{_html.escape(exp)}</span>'    if exp != "Not specified"  else ""
        posted_str = f'<span class="job-meta-item">{posted}</span>'           if posted and posted != "None" else ""

        if safe_url:
            apply_html = f'<a class="apply-btn" href="{safe_url}" target="_blank" rel="noopener noreferrer">View &amp; Apply</a>'
            title_html = f'<a href="{safe_url}" target="_blank" rel="noopener noreferrer">{title}</a>'
        else:
            apply_html = ""
            title_html = title

        st.html(f"""
        <div class="job-card">
            <div class="job-title">{title_html}</div>
            <div class="job-company">{company}</div>
            <div class="job-meta">
                <span class="job-meta-item">{loc}</span>
                {posted_str}
            </div>
            <div class="job-skills">
                {sal_badge}
                {exp_badge}
                {skills_html}
            </div>
            {apply_html}
        </div>
        """)
        
    # ── Pagination buttons (bottom) ──
    MAX_VISIBLE = 9
    half = MAX_VISIBLE // 2
    start_p = max(1, page_num - half)
    end_p   = min(total_pages, start_p + MAX_VISIBLE - 1)
    start_p = max(1, end_p - MAX_VISIBLE + 1)
    st.markdown(
        f'<div style="font-size:0.78rem;color:#999;margin:20px 0 8px;">'
        f'Page {page_num} of {total_pages}</div>',
        unsafe_allow_html=True,
    )
    btn_cols_b = st.columns(min(total_pages, MAX_VISIBLE) + 2)
    col_idx    = 0

    with btn_cols_b[col_idx]:
        if st.button("‹", key="prev_bot", disabled=(page_num == 1)):
            st.session_state["listing_page"] = max(1, page_num - 1)
            st.rerun()
    col_idx += 1

    for p in range(start_p, end_p + 1):
        with btn_cols_b[col_idx]:
            label    = f"**{p}**" if p == page_num else str(p)
            btn_type = "primary" if p == page_num else "secondary"
            if st.button(label, key=f"page_{p}_bot", type=btn_type):
                st.session_state["listing_page"] = p
                st.rerun()
        col_idx += 1

    with btn_cols_b[col_idx]:
        if st.button("›", key="next_bot", disabled=(page_num == total_pages)):
            st.session_state["listing_page"] = min(total_pages, page_num + 1)
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)  # close .page-wrap
