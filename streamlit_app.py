import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import plotly.graph_objects as go
import json
import re
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
    padding     : 28px 24px 60px;
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
.filter-bar {
    background    : var(--surface);
    border        : 1px solid var(--border);
    border-radius : var(--radius);
    padding       : 14px 20px;
    margin-bottom : 22px;
    box-shadow    : var(--shadow-sm);
    display       : flex;
    gap           : 16px;
    align-items   : center;
    flex-wrap     : wrap;
}
.filter-label {
    font-size  : 0.8rem;
    font-weight: 600;
    color      : var(--text-secondary);
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

/* ── Number input ── */
input[type="number"],
[data-testid="stNumberInput"] input {
    background   : var(--surface) !important;
    color        : var(--text-primary) !important;
    border-color : var(--border) !important;
    border-radius: var(--radius) !important;
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
#  NOTE: xaxis / yaxis are defined here ONCE.
#  Do NOT pass xaxis= or yaxis= again in update_layout(**PLOTLY_LAYOUT, ...)
#  Use PLOTLY_LAYOUT_NO_AXES for charts that need custom axes.
# ─────────────────────────────────────────────
_AXIS_STYLE = dict(gridcolor="#EEEDE9", linecolor="#E0DFDC", tickfont=dict(size=11))

PLOTLY_LAYOUT = dict(
    font         = dict(family="Inter, sans-serif", color="#191919"),
    paper_bgcolor= "rgba(0,0,0,0)",
    plot_bgcolor = "#FFFFFF",
    margin       = dict(l=8, r=8, t=36, b=8),
    title_font   = dict(size=13, color="#666666", family="Inter, sans-serif"),
    xaxis        = _AXIS_STYLE,
    yaxis        = _AXIS_STYLE,
    hoverlabel   = dict(bgcolor="#FFFFFF", font_size=12, font_family="Inter, sans-serif",
                        bordercolor="#E0DFDC"),
    colorway     = ["#0A66C2","#057642","#B24020","#7B5EA7","#D48806","#0891B2"],
)

# Layout variant without pre-set axes (use when you need custom xaxis/yaxis params)
PLOTLY_LAYOUT_NO_AXES = {k: v for k, v in PLOTLY_LAYOUT.items() if k not in ("xaxis", "yaxis")}

BLUE_SEQ = ["#EBF3FB","#BAD7F5","#7BB8ED","#3D92D9","#0A66C2","#004182"]

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

def build_map_data(df):
    rows = []
    for loc in df["location"].dropna():
        loc_lower = str(loc).strip().lower()
        for city, (lat, lon) in CITY_COORDS.items():
            if city in loc_lower:
                rows.append({"city": city.title(), "lat": lat, "lon": lon})
                break
    if not rows:
        return pd.DataFrame()
    tmp = pd.DataFrame(rows)
    return tmp.groupby(["city","lat","lon"]).size().reset_index(name="openings")


# ─────────────────────────────────────────────
#  NAV BAR
# ─────────────────────────────────────────────
st.markdown("""
<div class="nav-bar">
    <div class="nav-logo">TalentPulse <span>India</span></div>
    <div class="nav-tag">Tech Market Intelligence</div>
</div>
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

# ─────────────────────────────────────────────
#  FILTER ROW
# ─────────────────────────────────────────────
st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
    fc1, fc2, fc3 = st.columns([2, 2, 1])
    with fc1:
        role_options = ["All Roles"] + sorted(df["title"].dropna().unique().tolist())
        selected_role = st.selectbox("Role", role_options, label_visibility="collapsed")
    with fc2:
        loc_options = ["All Locations"] + sorted(df["location"].dropna().unique().tolist())
        selected_loc = st.selectbox("Location", loc_options, label_visibility="collapsed")
    with fc3:
        exp_options = ["All Experience"] + sorted(df["experience_level"].dropna().unique().tolist())
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
tab_market, tab_salary, tab_companies, tab_map, tab_listings = st.tabs([
    "📊  Market Overview",
    "💰  Salary Insights",
    "🏢  Company Intelligence",
    "🗺️  Geographic Heat Map",
    "📋  Job Listings",
])

# ══════════════════════════════════════════════
#  TAB 1 — MARKET OVERVIEW
# ══════════════════════════════════════════════
with tab_market:
    c1, c2 = st.columns([3, 2])

    # ── Chart 1: Top 15 Technical Skills ──
    with c1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Top 15 In-Demand Technical Skills</div>', unsafe_allow_html=True)

        all_tech = []
        for sl in fdf["tech_skills_found"].dropna():
            if isinstance(sl, list):
                all_tech.extend(sl)

        if all_tech:
            skill_counts = Counter(all_tech)
            skills_df = pd.DataFrame(skill_counts.most_common(15), columns=["Skill", "Mentions"])

            fig_skills = go.Figure(go.Bar(
                x=skills_df["Mentions"],
                y=skills_df["Skill"],
                orientation="h",
                marker=dict(
                    color=skills_df["Mentions"],
                    colorscale=[[0,"#BAD7F5"],[1,"#0A66C2"]],
                    line=dict(width=0),
                ),
                hovertemplate="<b>%{y}</b><br>%{x} postings<extra></extra>",
            ))
            # Use PLOTLY_LAYOUT_NO_AXES and define custom axes separately to avoid duplicate key error
            fig_skills.update_layout(
                **PLOTLY_LAYOUT_NO_AXES,
                height=460,
                title="Frequency across all active listings",
                yaxis=dict(categoryorder="total ascending", tickfont=dict(size=11),
                           gridcolor="#EEEDE9", linecolor="#E0DFDC"),
                xaxis=dict(gridcolor="#EEEDE9", linecolor="#E0DFDC", tickfont=dict(size=11)),
            )
            st.plotly_chart(fig_skills, use_container_width=True)
        else:
            st.info("No skill data available for this filter set.")

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Chart 2: Experience Level Donut ──
    with c2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Experience Level Distribution</div>', unsafe_allow_html=True)

        exp_counts = fdf["experience_level"].dropna().value_counts().reset_index()
        exp_counts.columns = ["Level", "Count"]

        if not exp_counts.empty:
            fig_exp = go.Figure(go.Pie(
                labels=exp_counts["Level"],
                values=exp_counts["Count"],
                hole=0.58,
                marker=dict(colors=["#0A66C2","#057642","#B24020","#7B5EA7","#D48806","#0891B2"],
                            line=dict(color="#FFFFFF", width=2)),
                textinfo="label+percent",
                textfont=dict(size=11, family="Inter, sans-serif"),
                hovertemplate="<b>%{label}</b><br>%{value} jobs (%{percent})<extra></extra>",
            ))
            fig_exp.update_layout(
                **PLOTLY_LAYOUT,
                height=460,
                showlegend=True,
                legend=dict(orientation="v", x=1.02, y=0.5, font=dict(size=11)),
                annotations=[dict(text=f"<b>{len(fdf)}</b><br><span style='font-size:10px'>listings</span>",
                                  x=0.5, y=0.5, font_size=15, showarrow=False)],
            )
            st.plotly_chart(fig_exp, use_container_width=True)
        else:
            st.info("No experience data available.")

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Chart 3: Soft Skills ──
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Top Soft Skills Mentioned</div>', unsafe_allow_html=True)

    all_soft = []
    for sl in fdf["soft_skills_found"].dropna():
        if isinstance(sl, list):
            all_soft.extend(sl)

    if all_soft:
        soft_counts = Counter(all_soft)
        soft_df = pd.DataFrame(soft_counts.most_common(10), columns=["Skill", "Mentions"])

        fig_soft = go.Figure(go.Bar(
            x=soft_df["Skill"],
            y=soft_df["Mentions"],
            marker=dict(
                color=soft_df["Mentions"],
                colorscale=[[0,"#B8E6C8"],[1,"#057642"]],
                line=dict(width=0),
            ),
            hovertemplate="<b>%{x}</b><br>%{y} postings<extra></extra>",
        ))
        fig_soft.update_layout(
            **PLOTLY_LAYOUT,
            height=300,
            title="Frequency across all active listings",
        )
        st.plotly_chart(fig_soft, use_container_width=True)
    else:
        st.info("No soft skill data available.")

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  TAB 2 — SALARY INSIGHTS
# ══════════════════════════════════════════════
with tab_salary:
    sal_fdf = fdf[fdf["salary_lpa"].notna()]

    if sal_fdf.empty:
        st.info("Salary data is not disclosed in enough listings for this filter.")
    else:
        r1, r2 = st.columns(2)

        # ── Box plot: Salary by Role ──
        with r1:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">Salary Range by Job Role (LPA)</div>', unsafe_allow_html=True)

            role_sal = sal_fdf.groupby("title")["salary_lpa"].apply(list).reset_index()
            role_sal = role_sal[role_sal["salary_lpa"].apply(len) >= 2]

            if not role_sal.empty:
                fig_box = go.Figure()
                colors = ["#0A66C2","#057642","#B24020","#7B5EA7","#D48806","#0891B2"]
                for i, row in role_sal.iterrows():
                    fig_box.add_trace(go.Box(
                        y=row["salary_lpa"],
                        name=row["title"][:25],
                        marker_color=colors[i % len(colors)],
                        boxpoints="outliers",
                        hovertemplate="%{y} LPA<extra></extra>",
                        line=dict(width=1.5),
                    ))
                fig_box.update_layout(
                    **PLOTLY_LAYOUT,
                    height=420,
                    showlegend=False,
                    title="Distribution of disclosed salaries",
                )
                st.plotly_chart(fig_box, use_container_width=True)
            else:
                st.info("Insufficient data for box plot.")

            st.markdown('</div>', unsafe_allow_html=True)

        # ── Histogram: Salary distribution ──
        with r2:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">Overall Salary Distribution (LPA)</div>', unsafe_allow_html=True)

            fig_hist = go.Figure(go.Histogram(
                x=sal_fdf["salary_lpa"],
                nbinsx=20,
                marker=dict(color="#0A66C2", line=dict(color="#FFFFFF", width=1)),
                hovertemplate="Range: %{x} LPA<br>Count: %{y}<extra></extra>",
            ))
            fig_hist.update_layout(
                **PLOTLY_LAYOUT,
                height=420,
                title="Concentration of salary offers",
                bargap=0.05,
            )
            st.plotly_chart(fig_hist, use_container_width=True)

            st.markdown('</div>', unsafe_allow_html=True)

        # ── Average salary by experience ──
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Average Salary by Experience Level (LPA)</div>', unsafe_allow_html=True)

        avg_exp_sal = (
            sal_fdf[sal_fdf["experience_level"].notna()]
            .groupby("experience_level")["salary_lpa"]
            .mean()
            .sort_values(ascending=False)
            .reset_index()
        )
        avg_exp_sal.columns = ["Level", "Avg LPA"]

        if not avg_exp_sal.empty:
            fig_avgs = go.Figure(go.Bar(
                x=avg_exp_sal["Level"],
                y=avg_exp_sal["Avg LPA"],
                text=avg_exp_sal["Avg LPA"].apply(lambda v: f"{v:.1f}"),
                textposition="outside",
                marker=dict(color="#0A66C2", line=dict(width=0)),
                hovertemplate="<b>%{x}</b><br>Avg: %{y:.1f} LPA<extra></extra>",
            ))
            fig_avgs.update_layout(**PLOTLY_LAYOUT, height=320,
                                   title="Mean salary across experience brackets")
            st.plotly_chart(fig_avgs, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  TAB 3 — COMPANY INTELLIGENCE
# ══════════════════════════════════════════════
with tab_companies:
    g1, g2 = st.columns(2)

    # ── Top 20 companies by posting volume ──
    with g1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Top 20 Hiring Companies</div>', unsafe_allow_html=True)

        co_counts = fdf["company"].value_counts().head(20).reset_index()
        co_counts.columns = ["Company", "Postings"]

        fig_co = go.Figure(go.Bar(
            x=co_counts["Postings"],
            y=co_counts["Company"],
            orientation="h",
            marker=dict(
                color=co_counts["Postings"],
                colorscale=[[0,"#BAD7F5"],[1,"#0A66C2"]],
                line=dict(width=0),
            ),
            hovertemplate="<b>%{y}</b><br>%{x} listings<extra></extra>",
        ))
        fig_co.update_layout(
            **PLOTLY_LAYOUT_NO_AXES,
            height=520,
            title="Volume of active job postings",
            yaxis=dict(categoryorder="total ascending", tickfont=dict(size=11),
                       gridcolor="#EEEDE9", linecolor="#E0DFDC"),
            xaxis=dict(gridcolor="#EEEDE9", linecolor="#E0DFDC", tickfont=dict(size=11)),
        )
        st.plotly_chart(fig_co, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Roles distribution per company (top 10) ──
    with g2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Role Diversity — Top 10 Employers</div>', unsafe_allow_html=True)

        top10_cos = fdf["company"].value_counts().head(10).index.tolist()
        role_div = (
            fdf[fdf["company"].isin(top10_cos)]
            .groupby(["company","title"])
            .size()
            .reset_index(name="count")
        )

        if not role_div.empty:
            fig_div = px.bar(
                role_div, x="count", y="company", color="title",
                orientation="h",
                color_discrete_sequence=["#0A66C2","#057642","#B24020","#7B5EA7","#D48806","#0891B2","#BE185D","#0E7490","#92400E","#166534"],
                labels={"count":"Listings", "company":"", "title":"Role"},
            )
            fig_div.update_layout(
                **PLOTLY_LAYOUT_NO_AXES,
                height=520,
                title="How each employer distributes hiring across roles",
                yaxis=dict(categoryorder="total ascending", tickfont=dict(size=11),
                           gridcolor="#EEEDE9", linecolor="#E0DFDC"),
                xaxis=dict(gridcolor="#EEEDE9", linecolor="#E0DFDC", tickfont=dict(size=11)),
                legend=dict(font=dict(size=10), orientation="h", y=-0.18),
                barmode="stack",
            )
            st.plotly_chart(fig_div, use_container_width=True)
        else:
            st.info("Insufficient role data for breakdown.")

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Role demand treemap ──
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Role Demand — Proportional View</div>', unsafe_allow_html=True)

    role_demand = fdf["title"].value_counts().reset_index()
    role_demand.columns = ["Role", "Listings"]

    fig_tree = px.treemap(
        role_demand, path=["Role"], values="Listings",
        color="Listings",
        color_continuous_scale=["#EBF3FB","#0A66C2"],
    )
    fig_tree.update_traces(textfont=dict(family="Inter, sans-serif", size=12))
    fig_tree.update_layout(**PLOTLY_LAYOUT, height=350,
                           title="Relative size reflects number of open positions")
    st.plotly_chart(fig_tree, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  TAB 4 — GEOGRAPHIC HEAT MAP
# ══════════════════════════════════════════════
with tab_map:
    map_df = build_map_data(fdf)

    if map_df.empty:
        st.info("No recognisable Indian city names found in the location field for this filter set.")
    else:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Geographic Distribution of Tech Hiring — India</div>',
                    unsafe_allow_html=True)

        fig_map = px.scatter_mapbox(
            map_df,
            lat="lat", lon="lon",
            size="openings",
            color="openings",
            color_continuous_scale=["#BAD7F5","#0A66C2","#004182"],
            size_max=55,
            zoom=4.0,
            center={"lat": 20.5937, "lon": 78.9629},
            mapbox_style="carto-positron",
            hover_name="city",
            hover_data={"openings": True, "lat": False, "lon": False},
            labels={"openings":"Open Positions"},
        )
        fig_map.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            margin={"r":0,"t":0,"l":0,"b":0},
            height=560,
            coloraxis_colorbar=dict(
                title="Listings",
                thickness=14,
                len=0.6,
                tickfont=dict(size=11, family="Inter, sans-serif"),
            ),
        )
        st.plotly_chart(fig_map, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # City leaderboard below the map
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">City Hiring Leaderboard</div>', unsafe_allow_html=True)

        city_rank = map_df.sort_values("openings", ascending=False).reset_index(drop=True)
        city_rank.index += 1
        city_rank.columns = ["City","Latitude","Longitude","Open Positions"]

        fig_city = go.Figure(go.Bar(
            x=city_rank["City"],
            y=city_rank["Open Positions"],
            marker=dict(
                color=city_rank["Open Positions"],
                colorscale=[[0,"#BAD7F5"],[1,"#0A66C2"]],
                line=dict(width=0),
            ),
            hovertemplate="<b>%{x}</b><br>%{y} open positions<extra></extra>",
        ))
        fig_city.update_layout(**PLOTLY_LAYOUT, height=320,
                               title="Absolute listing counts per city")
        st.plotly_chart(fig_city, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  TAB 5 — JOB LISTINGS
# ══════════════════════════════════════════════
with tab_listings:
    st.markdown(
        f'<div style="font-size:0.82rem;color:#666;margin-bottom:16px;">'
        f'Showing <strong>{len(fdf)}</strong> listings matching your filters</div>',
        unsafe_allow_html=True,
    )

    # Pagination
    PAGE_SIZE = 20
    total_pages = max(1, (len(fdf) - 1) // PAGE_SIZE + 1)
    page_num = st.number_input("Page", min_value=1, max_value=total_pages,
                               value=1, step=1, label_visibility="collapsed")
    start = (page_num - 1) * PAGE_SIZE
    page_df = fdf.iloc[start : start + PAGE_SIZE]

    st.markdown(
        f'<div style="font-size:0.78rem;color:#999;margin-bottom:14px;">'
        f'Page {page_num} of {total_pages}</div>',
        unsafe_allow_html=True,
    )

    for _, row in page_df.iterrows():
        title   = row.get("title") or "Untitled"
        company = row.get("company") or "Unknown Company"
        loc     = row.get("location") or "Location not specified"
        skills  = row.get("tech_skills_found") or []
        sal     = row.get("salary_str") or "Not disclosed"
        exp     = row.get("experience_level") or "Not specified"
        url     = row.get("job_url") or "#"
        posted  = str(row.get("posted_date") or "")[:10]

        skills_html = "".join(
            f'<span class="skill-pill">{s}</span>'
            for s in (skills[:6] if isinstance(skills, list) else [])
        )

        sal_badge = f'<span class="salary-badge">{sal}</span>' if sal != "Not disclosed" else ""
        exp_badge = f'<span class="exp-badge">{exp}</span>' if exp != "Not specified" else ""
        posted_str = f'<span class="job-meta-item">{posted}</span>' if posted and posted != "None" else ""

        st.markdown(f"""
        <div class="job-card">
            <div class="job-title"><a href="{url}" target="_blank">{title}</a></div>
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
            <a class="apply-btn" href="{url}" target="_blank">View &amp; Apply</a>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # close .page-wrap
