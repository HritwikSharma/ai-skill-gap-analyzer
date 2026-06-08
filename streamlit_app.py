import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import re
from collections import Counter

# ─────────────────────────────────────────────
#  PAGE CONFIG — must be first Streamlit call
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="TalentPulse — India Tech Market Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  GLOBAL DESIGN SYSTEM
# ─────────────────────────────────────────────
PALETTE = {
    "bg":           "#0A0F1E",
    "surface":      "#111827",
    "card":         "#151E2D",
    "border":       "#1E2D42",
    "accent":       "#0A66C2",        # LinkedIn blue
    "accent_light": "#378FE9",
    "accent_glow":  "rgba(10,102,194,0.15)",
    "green":        "#19B97C",
    "amber":        "#E9A027",
    "red":          "#E05C5C",
    "text_primary": "#F0F4FF",
    "text_secondary":"#8B9BB4",
    "text_muted":   "#4A5568",
}

PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="'DM Sans', sans-serif", color=PALETTE["text_secondary"], size=12),
    title_font=dict(family="'DM Sans', sans-serif", color=PALETTE["text_primary"], size=15),
    colorway=[PALETTE["accent"], PALETTE["green"], PALETTE["amber"], "#7C5CFC", "#E05C5C"],
    hoverlabel=dict(
        bgcolor=PALETTE["card"],
        bordercolor=PALETTE["border"],
        font_color=PALETTE["text_primary"],
    ),
    xaxis=dict(
        gridcolor=PALETTE["border"],
        linecolor=PALETTE["border"],
        tickcolor=PALETTE["text_muted"],
        zerolinecolor=PALETTE["border"],
    ),
    yaxis=dict(
        gridcolor=PALETTE["border"],
        linecolor=PALETTE["border"],
        tickcolor=PALETTE["text_muted"],
        zerolinecolor=PALETTE["border"],
    ),
    margin=dict(l=16, r=16, t=44, b=16),
)

st.markdown(f"""
<style>
  /* ── Fonts ── */
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

  /* ── Root reset ── */
  html, body, [class*="css"] {{
      font-family: 'DM Sans', sans-serif;
      background-color: {PALETTE['bg']};
      color: {PALETTE['text_primary']};
  }}

  /* ── Streamlit chrome wipeout ── */
  #MainMenu, footer, header {{ visibility: hidden; }}
  .block-container {{
      padding: 0 !important;
      max-width: 100% !important;
  }}
  section[data-testid="stSidebar"] {{ display: none; }}

  /* ── App shell ── */
  .app-wrapper {{
      min-height: 100vh;
      background: {PALETTE['bg']};
      padding: 0 0 60px 0;
  }}

  /* ── Top navigation bar ── */
  .navbar {{
      background: {PALETTE['surface']};
      border-bottom: 1px solid {PALETTE['border']};
      padding: 0 40px;
      height: 64px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: sticky;
      top: 0;
      z-index: 999;
      backdrop-filter: blur(12px);
  }}
  .navbar-brand {{
      display: flex;
      align-items: center;
      gap: 10px;
  }}
  .navbar-logo {{
      width: 32px; height: 32px;
      background: linear-gradient(135deg, {PALETTE['accent']}, {PALETTE['accent_light']});
      border-radius: 8px;
      display: flex; align-items: center; justify-content: center;
      font-size: 16px;
  }}
  .navbar-title {{
      font-size: 17px;
      font-weight: 700;
      color: {PALETTE['text_primary']};
      letter-spacing: -0.3px;
  }}
  .navbar-subtitle {{
      font-size: 11px;
      color: {PALETTE['text_muted']};
      font-weight: 400;
      letter-spacing: 0.5px;
      text-transform: uppercase;
  }}
  .navbar-badge {{
      background: {PALETTE['accent_glow']};
      border: 1px solid {PALETTE['accent']};
      color: {PALETTE['accent_light']};
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.3px;
  }}

  /* ── Page inner padding ── */
  .page-body {{
      padding: 32px 40px;
  }}

  /* ── Section heading ── */
  .section-heading {{
      font-size: 13px;
      font-weight: 600;
      letter-spacing: 1.4px;
      text-transform: uppercase;
      color: {PALETTE['text_muted']};
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 8px;
  }}
  .section-heading::after {{
      content: '';
      flex: 1;
      height: 1px;
      background: {PALETTE['border']};
  }}

  /* ── KPI Cards ── */
  .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
      margin-bottom: 32px;
  }}
  .kpi-card {{
      background: {PALETTE['card']};
      border: 1px solid {PALETTE['border']};
      border-radius: 12px;
      padding: 24px;
      position: relative;
      overflow: hidden;
      transition: border-color 0.2s;
  }}
  .kpi-card:hover {{
      border-color: {PALETTE['accent']};
  }}
  .kpi-card::before {{
      content: '';
      position: absolute;
      inset: 0;
      background: linear-gradient(135deg, {PALETTE['accent_glow']} 0%, transparent 60%);
      pointer-events: none;
  }}
  .kpi-label {{
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 1px;
      text-transform: uppercase;
      color: {PALETTE['text_muted']};
      margin-bottom: 10px;
  }}
  .kpi-value {{
      font-size: 32px;
      font-weight: 700;
      color: {PALETTE['text_primary']};
      letter-spacing: -1px;
      line-height: 1;
      margin-bottom: 6px;
  }}
  .kpi-sub {{
      font-size: 12px;
      color: {PALETTE['text_secondary']};
  }}
  .kpi-icon {{
      position: absolute;
      top: 20px; right: 20px;
      width: 36px; height: 36px;
      border-radius: 8px;
      display: flex; align-items: center; justify-content: center;
      font-size: 18px;
  }}
  .kpi-icon-blue  {{ background: rgba(10,102,194,0.15); }}
  .kpi-icon-green {{ background: rgba(25,185,124,0.15); }}
  .kpi-icon-amber {{ background: rgba(233,160,39,0.15); }}

  /* ── Chart card ── */
  .chart-card {{
      background: {PALETTE['card']};
      border: 1px solid {PALETTE['border']};
      border-radius: 12px;
      padding: 24px 20px 12px 20px;
      margin-bottom: 20px;
      transition: border-color 0.2s;
  }}
  .chart-card:hover {{ border-color: {PALETTE['accent']}44; }}
  .chart-title {{
      font-size: 14px;
      font-weight: 600;
      color: {PALETTE['text_primary']};
      margin-bottom: 4px;
  }}
  .chart-subtitle {{
      font-size: 12px;
      color: {PALETTE['text_muted']};
      margin-bottom: 16px;
  }}

  /* ── Tab bar ── */
  .tab-bar {{
      display: flex;
      gap: 4px;
      background: {PALETTE['surface']};
      border: 1px solid {PALETTE['border']};
      border-radius: 10px;
      padding: 4px;
      margin-bottom: 28px;
      width: fit-content;
  }}

  /* Override Streamlit's default tab styling */
  .stTabs [data-baseweb="tab-list"] {{
      background: {PALETTE['surface']};
      border: 1px solid {PALETTE['border']};
      border-radius: 10px;
      padding: 4px;
      gap: 2px;
  }}
  .stTabs [data-baseweb="tab"] {{
      background: transparent;
      color: {PALETTE['text_secondary']};
      border-radius: 7px;
      font-size: 13px;
      font-weight: 500;
      padding: 8px 20px;
      border: none;
      transition: all 0.15s;
  }}
  .stTabs [aria-selected="true"] {{
      background: {PALETTE['accent']} !important;
      color: white !important;
      font-weight: 600;
  }}
  .stTabs [data-baseweb="tab-highlight"] {{ display: none; }}
  .stTabs [data-baseweb="tab-border"] {{ display: none; }}

  /* ── Job listing card ── */
  .job-card {{
      background: {PALETTE['card']};
      border: 1px solid {PALETTE['border']};
      border-radius: 12px;
      padding: 20px 22px;
      margin-bottom: 12px;
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 12px;
      align-items: start;
      transition: all 0.15s;
      cursor: pointer;
  }}
  .job-card:hover {{
      border-color: {PALETTE['accent']};
      background: {PALETTE['surface']};
      transform: translateY(-1px);
  }}
  .job-card-title {{
      font-size: 15px;
      font-weight: 600;
      color: {PALETTE['text_primary']};
      margin-bottom: 4px;
  }}
  .job-card-company {{
      font-size: 13px;
      color: {PALETTE['accent_light']};
      font-weight: 500;
      margin-bottom: 6px;
  }}
  .job-card-meta {{
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
  }}
  .job-meta-pill {{
      background: {PALETTE['surface']};
      border: 1px solid {PALETTE['border']};
      color: {PALETTE['text_secondary']};
      padding: 3px 10px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 500;
  }}
  .job-skill-pill {{
      background: rgba(10,102,194,0.12);
      border: 1px solid rgba(10,102,194,0.3);
      color: {PALETTE['accent_light']};
      padding: 3px 10px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 500;
  }}
  .salary-badge {{
      background: rgba(25,185,124,0.12);
      border: 1px solid rgba(25,185,124,0.3);
      color: {PALETTE['green']};
      padding: 5px 12px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 600;
      white-space: nowrap;
  }}
  .experience-badge {{
      background: rgba(233,160,39,0.12);
      border: 1px solid rgba(233,160,39,0.3);
      color: {PALETTE['amber']};
      padding: 5px 12px;
      border-radius: 8px;
      font-size: 11px;
      font-weight: 600;
      text-align: center;
  }}

  /* ── Filter bar ── */
  .filter-bar {{
      background: {PALETTE['card']};
      border: 1px solid {PALETTE['border']};
      border-radius: 12px;
      padding: 16px 20px;
      margin-bottom: 24px;
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
  }}

  /* ── Streamlit widget overrides ── */
  .stSelectbox > div > div,
  .stMultiSelect > div > div {{
      background: {PALETTE['surface']} !important;
      border: 1px solid {PALETTE['border']} !important;
      border-radius: 8px !important;
      color: {PALETTE['text_primary']} !important;
  }}
  .stTextInput > div > div > input {{
      background: {PALETTE['surface']} !important;
      border: 1px solid {PALETTE['border']} !important;
      border-radius: 8px !important;
      color: {PALETTE['text_primary']} !important;
  }}
  div[data-testid="stMetric"] {{
      display: none;
  }}

  /* ── Divider ── */
  .divider {{
      height: 1px;
      background: {PALETTE['border']};
      margin: 28px 0;
  }}

  /* ── India map container ── */
  .map-note {{
      font-size: 11px;
      color: {PALETTE['text_muted']};
      margin-top: 8px;
      text-align: center;
  }}

  /* ── Scrollbar ── */
  ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
  ::-webkit-scrollbar-track {{ background: {PALETTE['bg']}; }}
  ::-webkit-scrollbar-thumb {{ background: {PALETTE['border']}; border-radius: 3px; }}
  ::-webkit-scrollbar-thumb:hover {{ background: {PALETTE['text_muted']}; }}

  /* ── Plotly chart container fix ── */
  .js-plotly-plot .plotly {{
      background: transparent !important;
  }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  DATABASE LAYER
# ─────────────────────────────────────────────
DB_HOST = "job-db.clgqc6scelz7.eu-north-1.rds.amazonaws.com"
DB_USER = "postgres"
DB_NAME = "postgres"
DB_PASSWORD = "HRITWIKSHARMA"


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
        st.error(f"Database connection error: {e}")
        return pd.DataFrame()


# ─────────────────────────────────────────────
#  DATA PROCESSING HELPERS
# ─────────────────────────────────────────────
CITY_COORDS = {
    'bengaluru': (12.9716, 77.5946), 'bangalore': (12.9716, 77.5946),
    'hyderabad': (17.3850, 78.4867), 'pune': (18.5204, 73.8567),
    'mumbai': (19.0760, 72.8777),    'chennai': (13.0827, 80.2707),
    'delhi': (28.6139, 77.2090),     'new delhi': (28.6139, 77.2090),
    'gurgaon': (28.4595, 77.0266),   'gurugram': (28.4595, 77.0266),
    'noida': (28.5355, 77.3910),     'kolkata': (22.5726, 88.3639),
    'ahmedabad': (23.0225, 72.5714), 'jaipur': (26.9124, 75.7873),
    'coimbatore': (11.0168, 76.9558),'kochi': (9.9312, 76.2673),
    'cochin': (9.9312, 76.2673),     'thiruvananthapuram': (8.5241, 76.9366),
    'trivandrum': (8.5241, 76.9366), 'indore': (22.7196, 75.8577),
    'bhopal': (23.2599, 77.4126),    'chandigarh': (30.7333, 76.7794),
    'nagpur': (21.1458, 79.0882),    'vizag': (17.6868, 83.2185),
    'visakhapatnam': (17.6868, 83.2185), 'surat': (21.1702, 72.8311),
    'lucknow': (26.8467, 80.9462),   'bhubaneswar': (20.2961, 85.8245),
    'remote': (22.5937, 78.9629),
}


def parse_extra_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """Explodes the extra_metadata JSONB column into typed columns."""
    def _safe_parse(val):
        if isinstance(val, dict):
            return val
        if isinstance(val, str):
            try:
                return json.loads(val)
            except Exception:
                return {}
        return {}

    meta = df['extra_metadata'].apply(_safe_parse).apply(pd.Series)
    df = df.copy()
    df['experience_level'] = meta.get('experience_level', pd.Series(['Not Specified'] * len(df)))
    df['salary_raw']       = meta.get('salary_extracted', pd.Series(['Not Specified'] * len(df)))
    df['salary_min_num']   = meta.get('salary_min', pd.Series([None] * len(df)))
    df['salary_max_num']   = meta.get('salary_max', pd.Series([None] * len(df)))
    return df


def parse_salary_range(s: str):
    """Returns (min, max) floats from a salary string like '₹ 30000 - ₹ 60000'."""
    if not isinstance(s, str) or s == 'Not Specified':
        return None, None
    nums = re.findall(r'[\d,]+', s.replace(',', ''))
    nums = [float(n) for n in nums if n]
    if len(nums) >= 2:
        return nums[0], nums[1]
    if len(nums) == 1:
        return nums[0], nums[0]
    return None, None


def get_skill_counts(df: pd.DataFrame, col='tech_skills_found') -> pd.DataFrame:
    all_skills = []
    for val in df[col].dropna():
        if isinstance(val, list):
            all_skills.extend(val)
        elif isinstance(val, str):
            try:
                parsed = json.loads(val)
                if isinstance(parsed, list):
                    all_skills.extend(parsed)
            except Exception:
                pass
    counts = Counter(all_skills)
    return pd.DataFrame(counts.most_common(15), columns=['Skill', 'Count'])


def build_map_data(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for loc in df['location'].dropna():
        loc_l = str(loc).strip().lower()
        for city, (lat, lon) in CITY_COORDS.items():
            if city in loc_l:
                rows.append({'City': city.title(), 'lat': lat, 'lon': lon})
                break
    if not rows:
        return pd.DataFrame()
    mdf = pd.DataFrame(rows)
    return mdf.groupby(['City', 'lat', 'lon']).size().reset_index(name='Jobs')


def clean_experience(val: str) -> str:
    if not isinstance(val, str):
        return 'Not Specified'
    v = val.strip().lower()
    if v in ('not specified', '', 'nan'):
        return 'Not Specified'
    if 'intern' in v:
        return 'Internship'
    if 'fresher' in v:
        return 'Fresher / 0 yrs'
    if re.search(r'0[\-–]1|0 ?[\-–] ?1', v):
        return '0 – 1 yr'
    if re.search(r'1[\-–]2|1 ?[\-–] ?2', v):
        return '1 – 2 yrs'
    if re.search(r'2[\-–]3', v):
        return '2 – 3 yrs'
    if re.search(r'[3-4][\-–+]', v):
        return '3 – 5 yrs'
    if re.search(r'5[\-–+]', v):
        return '5 + yrs'
    if re.search(r'\d', v):
        return v.title()
    return 'Not Specified'


# ─────────────────────────────────────────────
#  PLOTLY CHART BUILDERS
# ─────────────────────────────────────────────
def _apply_theme(fig):
    fig.update_layout(**PLOTLY_THEME)
    return fig


def chart_top_skills(df_skills: pd.DataFrame) -> go.Figure:
    df_skills = df_skills.sort_values('Count')
    fig = go.Figure(go.Bar(
        x=df_skills['Count'],
        y=df_skills['Skill'],
        orientation='h',
        marker=dict(
            color=df_skills['Count'],
            colorscale=[[0, '#1A3A5C'], [0.5, PALETTE['accent']], [1, PALETTE['accent_light']]],
            showscale=False,
            line=dict(width=0),
        ),
        text=df_skills['Count'],
        textposition='outside',
        textfont=dict(color=PALETTE['text_secondary'], size=11),
        hovertemplate='<b>%{y}</b><br>Mentions: %{x}<extra></extra>',
    ))
    _apply_theme(fig)
    fig.update_layout(
        height=480,
        yaxis=dict(gridcolor='transparent', linecolor='transparent'),
        xaxis=dict(gridcolor=PALETTE['border']),
        bargap=0.35,
    )
    return fig


def chart_salary_by_role(df: pd.DataFrame) -> go.Figure:
    records = []
    for _, row in df.iterrows():
        title = str(row.get('title', 'Unknown'))
        s = str(row.get('salary_raw', ''))
        mn, mx = parse_salary_range(s)
        if mn is not None and mn > 0:
            records.append({'Role': title[:35], 'SalaryMin': mn / 1000, 'SalaryMax': (mx or mn) / 1000})

    if not records:
        fig = go.Figure()
        fig.add_annotation(text="Salary data not available for this filter",
                           xref="paper", yref="paper", x=0.5, y=0.5,
                           font=dict(color=PALETTE['text_muted'], size=14), showarrow=False)
        _apply_theme(fig)
        return fig

    sal_df = pd.DataFrame(records)
    role_stats = sal_df.groupby('Role').agg(
        Min=('SalaryMin', 'min'),
        Median=('SalaryMin', 'median'),
        Max=('SalaryMax', 'max'),
        Count=('SalaryMin', 'count')
    ).reset_index().sort_values('Median', ascending=False).head(12)

    fig = go.Figure()
    for _, r in role_stats.iterrows():
        fig.add_trace(go.Bar(
            name=r['Role'], x=[r['Role']],
            y=[r['Max'] - r['Min']],
            base=[r['Min']],
            marker_color=PALETTE['accent'],
            marker_opacity=0.7,
            width=0.5,
            hovertemplate=(f"<b>{r['Role']}</b><br>"
                           f"Min: ₹{r['Min']:.0f}K<br>"
                           f"Median: ₹{r['Median']:.0f}K<br>"
                           f"Max: ₹{r['Max']:.0f}K<br>"
                           f"Listings: {r['Count']}<extra></extra>"),
        ))
        fig.add_trace(go.Scatter(
            x=[r['Role']], y=[r['Median']],
            mode='markers',
            marker=dict(symbol='line-ew', size=20,
                        color=PALETTE['accent_light'],
                        line=dict(width=3, color=PALETTE['accent_light'])),
            showlegend=False,
            hoverinfo='skip',
        ))

    _apply_theme(fig)
    fig.update_layout(
        height=420,
        showlegend=False,
        xaxis=dict(tickangle=-25, gridcolor='transparent'),
        yaxis=dict(title='Salary (₹ Thousands)', gridcolor=PALETTE['border']),
        barmode='overlay',
    )
    return fig


def chart_experience_donut(df: pd.DataFrame) -> go.Figure:
    df = df.copy()
    df['exp_clean'] = df['experience_level'].apply(clean_experience)
    counts = df['exp_clean'].value_counts()
    counts = counts[counts.index != 'Not Specified']

    colors = [PALETTE['accent'], PALETTE['green'], PALETTE['amber'],
              '#7C5CFC', PALETTE['red'], PALETTE['accent_light'], '#E05C5C', '#4ADEDE']

    fig = go.Figure(go.Pie(
        labels=counts.index,
        values=counts.values,
        hole=0.62,
        marker=dict(colors=colors[:len(counts)], line=dict(color=PALETTE['bg'], width=3)),
        textinfo='label+percent',
        textfont=dict(size=11, color=PALETTE['text_primary']),
        hovertemplate='<b>%{label}</b><br>Jobs: %{value}<br>Share: %{percent}<extra></extra>',
        rotation=90,
    ))
    fig.add_annotation(
        text=f"<b>{counts.sum():,}</b><br><span style='font-size:11px'>listings</span>",
        x=0.5, y=0.5, showarrow=False, align='center',
        font=dict(size=18, color=PALETTE['text_primary']),
    )
    _apply_theme(fig)
    fig.update_layout(
        height=420,
        showlegend=True,
        legend=dict(
            orientation='v', x=1.05, y=0.5,
            font=dict(color=PALETTE['text_secondary'], size=11),
        ),
    )
    return fig


def chart_company_leaderboard(df: pd.DataFrame) -> go.Figure:
    top = df['company'].value_counts().head(15).reset_index()
    top.columns = ['Company', 'Openings']
    top = top.sort_values('Openings', ascending=True)

    fig = go.Figure(go.Bar(
        x=top['Openings'],
        y=top['Company'],
        orientation='h',
        marker=dict(
            color=top['Openings'],
            colorscale=[[0, '#1A2D3C'], [1, PALETTE['green']]],
            showscale=False,
            line=dict(width=0),
        ),
        text=top['Openings'],
        textposition='outside',
        textfont=dict(color=PALETTE['text_secondary'], size=11),
        hovertemplate='<b>%{y}</b><br>Open positions: %{x}<extra></extra>',
    ))
    _apply_theme(fig)
    fig.update_layout(
        height=480,
        bargap=0.3,
        yaxis=dict(gridcolor='transparent', linecolor='transparent'),
        xaxis=dict(gridcolor=PALETTE['border']),
    )
    return fig


def chart_india_map(map_df: pd.DataFrame) -> go.Figure:
    if map_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No location data matched for current filter",
            xref="paper", yref="paper", x=0.5, y=0.5,
            font=dict(color=PALETTE['text_muted'], size=14), showarrow=False,
        )
        _apply_theme(fig)
        return fig

    fig = px.scatter_mapbox(
        map_df, lat="lat", lon="lon",
        size="Jobs", color="Jobs",
        color_continuous_scale=[
            [0, '#0A2540'], [0.3, PALETTE['accent']],
            [0.7, PALETTE['accent_light']], [1, '#FFFFFF']
        ],
        size_max=50, zoom=4.0,
        center={"lat": 20.5937, "lon": 78.9629},
        mapbox_style="carto-darkmatter",
        hover_name="City",
        hover_data={"Jobs": True, "lat": False, "lon": False},
        labels={"Jobs": "Open Roles"},
    )
    fig.update_traces(
        hovertemplate='<b>%{hovertext}</b><br>Open Roles: %{marker.size}<extra></extra>'
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=520,
        coloraxis_showscale=False,
    )
    return fig


def chart_skills_heatmap(df: pd.DataFrame) -> go.Figure:
    """Skills by role heatmap — which skills appear most per job category."""
    top_skills_df = get_skill_counts(df)
    top_skills = top_skills_df['Skill'].tolist()[:12]

    roles = df['title'].value_counts().head(8).index.tolist()
    matrix = []
    for role in roles:
        sub = df[df['title'] == role]
        row = []
        for skill in top_skills:
            count = sum(
                1 for v in sub['tech_skills_found'].dropna()
                if (isinstance(v, list) and skill in v) or
                   (isinstance(v, str) and skill in v)
            )
            row.append(count)
        matrix.append(row)

    fig = go.Figure(go.Heatmap(
        z=matrix,
        x=top_skills,
        y=[r[:28] for r in roles],
        colorscale=[[0, PALETTE['bg']], [0.3, '#0A2540'],
                    [0.7, PALETTE['accent']], [1, PALETTE['accent_light']]],
        showscale=True,
        hovertemplate='<b>%{y}</b> × <b>%{x}</b><br>Listings: %{z}<extra></extra>',
        xgap=3, ygap=3,
        colorbar=dict(
            tickfont=dict(color=PALETTE['text_secondary']),
            bgcolor='rgba(0,0,0,0)',
            outlinecolor=PALETTE['border'],
        ),
    ))
    _apply_theme(fig)
    fig.update_layout(
        height=420,
        xaxis=dict(tickangle=-30, gridcolor='transparent'),
        yaxis=dict(gridcolor='transparent'),
    )
    return fig


def chart_location_distribution(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar of top locations."""
    loc_counts = df['location'].dropna().apply(lambda x: str(x).strip().title()).value_counts().head(12)
    loc_df = pd.DataFrame({'Location': loc_counts.index, 'Jobs': loc_counts.values}).sort_values('Jobs')
    fig = go.Figure(go.Bar(
        x=loc_df['Jobs'], y=loc_df['Location'],
        orientation='h',
        marker=dict(
            color=loc_df['Jobs'],
            colorscale=[[0, '#1A2D3C'], [1, PALETTE['amber']]],
            showscale=False,
            line=dict(width=0),
        ),
        text=loc_df['Jobs'],
        textposition='outside',
        textfont=dict(color=PALETTE['text_secondary'], size=11),
        hovertemplate='<b>%{y}</b><br>Listings: %{x}<extra></extra>',
    ))
    _apply_theme(fig)
    fig.update_layout(
        height=420,
        bargap=0.3,
        yaxis=dict(gridcolor='transparent', linecolor='transparent'),
        xaxis=dict(gridcolor=PALETTE['border']),
    )
    return fig


def chart_soft_skills(df: pd.DataFrame) -> go.Figure:
    soft_df = get_skill_counts(df, col='soft_skills_found')
    if soft_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No soft skill data available",
                           xref="paper", yref="paper", x=0.5, y=0.5,
                           font=dict(color=PALETTE['text_muted'], size=14), showarrow=False)
        _apply_theme(fig)
        return fig

    soft_df = soft_df.head(10).sort_values('Count')
    fig = go.Figure(go.Bar(
        x=soft_df['Count'], y=soft_df['Skill'],
        orientation='h',
        marker=dict(
            color=soft_df['Count'],
            colorscale=[[0, '#1E1A3C'], [1, '#7C5CFC']],
            showscale=False, line=dict(width=0),
        ),
        text=soft_df['Count'], textposition='outside',
        textfont=dict(color=PALETTE['text_secondary'], size=11),
        hovertemplate='<b>%{y}</b><br>Mentions: %{x}<extra></extra>',
    ))
    _apply_theme(fig)
    fig.update_layout(
        height=380, bargap=0.35,
        yaxis=dict(gridcolor='transparent', linecolor='transparent'),
        xaxis=dict(gridcolor=PALETTE['border']),
    )
    return fig


def chart_source_trend(df: pd.DataFrame) -> go.Figure:
    """Listings per date based on created_timestamp in metadata."""
    dates = []
    for val in df['extra_metadata'].dropna():
        meta = val if isinstance(val, dict) else {}
        ts = meta.get('created_timestamp', '')
        if ts:
            try:
                dates.append(pd.to_datetime(ts).date())
            except Exception:
                pass

    if not dates:
        fig = go.Figure()
        fig.add_annotation(text="Timestamp data not available",
                           xref="paper", yref="paper", x=0.5, y=0.5,
                           font=dict(color=PALETTE['text_muted'], size=14), showarrow=False)
        _apply_theme(fig)
        return fig

    date_series = pd.Series(dates).value_counts().sort_index().reset_index()
    date_series.columns = ['Date', 'Listings']

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=date_series['Date'], y=date_series['Listings'],
        fill='tozeroy',
        fillcolor=PALETTE['accent_glow'],
        line=dict(color=PALETTE['accent'], width=2),
        mode='lines',
        hovertemplate='%{x}<br>Listings: %{y}<extra></extra>',
    ))
    _apply_theme(fig)
    fig.update_layout(
        height=320,
        xaxis=dict(gridcolor=PALETTE['border']),
        yaxis=dict(gridcolor=PALETTE['border'], title='New Listings'),
    )
    return fig


# ─────────────────────────────────────────────
#  RENDER HELPERS
# ─────────────────────────────────────────────
def chart_wrapper(title: str, subtitle: str, fig, key_suffix: str = ""):
    st.markdown(f"""
    <div class="chart-card">
        <div class="chart-title">{title}</div>
        <div class="chart-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, key=f"chart_{key_suffix}")


def kpi_html(label: str, value: str, sub: str, icon: str, icon_class: str) -> str:
    return f"""
    <div class="kpi-card">
        <div class="kpi-icon {icon_class}">{icon}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """


def render_job_card(row: pd.Series):
    skills = []
    sv = row.get('tech_skills_found')
    if isinstance(sv, list):
        skills = sv[:4]
    elif isinstance(sv, str):
        try:
            skills = json.loads(sv)[:4]
        except Exception:
            pass

    skill_pills = "".join(f'<span class="job-skill-pill">{s}</span>' for s in skills)
    salary = row.get('salary_raw', 'Not Specified')
    sal_block = f'<div class="salary-badge">💰 {salary}</div>' if salary != 'Not Specified' else ''
    exp = row.get('experience_level', 'Not Specified')
    exp_block = f'<div class="experience-badge">🎯 {exp}</div>' if exp != 'Not Specified' else ''
    loc = str(row.get('location', 'N/A'))[:30]

    st.markdown(f"""
    <div class="job-card">
        <div>
            <div class="job-card-title">{row.get('title', 'Unknown Role')}</div>
            <div class="job-card-company">{row.get('company', 'Unknown Company')}</div>
            <div class="job-card-meta">
                <span class="job-meta-pill">📍 {loc}</span>
                {skill_pills}
            </div>
        </div>
        <div style="display:flex;flex-direction:column;gap:6px;align-items:flex-end;">
            {sal_block}
            {exp_block}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  MAIN APP
# ─────────────────────────────────────────────
# Navbar
st.markdown("""
<div class="app-wrapper">
<div class="navbar">
    <div class="navbar-brand">
        <div class="navbar-logo">📊</div>
        <div>
            <div class="navbar-title">TalentPulse</div>
            <div class="navbar-subtitle">India Tech Market Intelligence</div>
        </div>
    </div>
    <div class="navbar-badge">● Live Data</div>
</div>
""", unsafe_allow_html=True)

# Page body
st.markdown('<div class="page-body">', unsafe_allow_html=True)

# ── Load & process data ──
with st.spinner("Connecting to market data pipeline..."):
    raw_df = fetch_job_data()

if raw_df.empty:
    st.warning("⚠️ No data found. Check your database connection or run the pipeline first.")
    st.stop()

df = parse_extra_metadata(raw_df)

# ── Global filters ──
all_roles   = sorted(df['title'].dropna().unique().tolist())
all_locs    = sorted(df['location'].dropna().unique().tolist())

with st.container():
    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
    f1, f2, f3 = st.columns([2, 2, 1])
    with f1:
        selected_roles = st.multiselect(
            "Job Role", options=["All Roles"] + all_roles,
            default=["All Roles"], label_visibility="collapsed",
            placeholder="Filter by job role…",
        )
    with f2:
        selected_locs = st.multiselect(
            "Location", options=["All Locations"] + all_locs,
            default=["All Locations"], label_visibility="collapsed",
            placeholder="Filter by location…",
        )
    with f3:
        st.markdown("""<div style="padding-top:6px;font-size:12px;color:#4A5568;">
        Filters apply across all tabs</div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Apply filters
filtered = df.copy()
if "All Roles" not in (selected_roles or ["All Roles"]) and selected_roles:
    filtered = filtered[filtered['title'].isin(selected_roles)]
if "All Locations" not in (selected_locs or ["All Locations"]) and selected_locs:
    filtered = filtered[filtered['location'].isin(selected_locs)]

# ── KPI Row ──
st.markdown('<div class="section-heading">Overview</div>', unsafe_allow_html=True)

# Compute KPI values
total_jobs = len(filtered)
total_companies = filtered['company'].nunique()
top_loc = filtered['location'].mode().dropna()
top_location = top_loc.iloc[0][:20] if not top_loc.empty else "N/A"

# Salary average
sal_vals = []
for s in filtered['salary_raw'].dropna():
    mn, mx = parse_salary_range(str(s))
    if mn:
        sal_vals.append((mn + (mx or mn)) / 2)
avg_sal = f"₹{(sum(sal_vals)/len(sal_vals)/1000):.0f}K" if sal_vals else "N/A"
sal_sub = f"avg across {len(sal_vals):,} listings with data" if sal_vals else "Salary data limited in dataset"

st.markdown(f"""
<div class="kpi-grid">
    {kpi_html("Total Postings Analysed", f"{total_jobs:,}", f"from {total_companies:,} unique employers", "📋", "kpi-icon-blue")}
    {kpi_html("Avg. Market Salary", avg_sal, sal_sub, "💰", "kpi-icon-green")}
    {kpi_html("Top Hiring Hub", top_location, "most active location in current filter", "📍", "kpi-icon-amber")}
</div>
""", unsafe_allow_html=True)

# ── Tabs ──
st.markdown('<div class="section-heading">Analytics</div>', unsafe_allow_html=True)

tab_skills, tab_salary, tab_geo, tab_companies, tab_listings = st.tabs([
    "🔥 Skills Demand",
    "💰 Salary & Experience",
    "🗺️ Geographic Heatmap",
    "🏢 Company Leaderboard",
    "📋 Job Listings",
])

# ════════════════════════════════════
# TAB 1 — SKILLS DEMAND
# ════════════════════════════════════
with tab_skills:
    c1, c2 = st.columns([1, 1], gap="large")
    with c1:
        skills_df = get_skill_counts(filtered, 'tech_skills_found')
        st.markdown('<div class="chart-card"><div class="chart-title">Top 15 In-Demand Technical Skills</div><div class="chart-subtitle">Aggregated frequency across all matched job descriptions</div></div>', unsafe_allow_html=True)
        if not skills_df.empty:
            st.plotly_chart(chart_top_skills(skills_df), use_container_width=True, key="top_skills")
        else:
            st.info("No skill data matched for this filter.")

    with c2:
        st.markdown('<div class="chart-card"><div class="chart-title">Top Soft Skills Required</div><div class="chart-subtitle">Communication, leadership and professional competencies extracted</div></div>', unsafe_allow_html=True)
        st.plotly_chart(chart_soft_skills(filtered), use_container_width=True, key="soft_skills")

    st.markdown('<div class="chart-card"><div class="chart-title">Skill × Role Heatmap</div><div class="chart-subtitle">Which skills are most valued per job category — intensity = listing frequency</div></div>', unsafe_allow_html=True)
    st.plotly_chart(chart_skills_heatmap(filtered), use_container_width=True, key="skill_heatmap")

# ════════════════════════════════════
# TAB 2 — SALARY & EXPERIENCE
# ════════════════════════════════════
with tab_salary:
    c1, c2 = st.columns([3, 2], gap="large")
    with c1:
        st.markdown('<div class="chart-card"><div class="chart-title">Salary Range by Job Role</div><div class="chart-subtitle">Bar spans min–max; horizontal line marks median. In ₹ thousands.</div></div>', unsafe_allow_html=True)
        st.plotly_chart(chart_salary_by_role(filtered), use_container_width=True, key="salary_chart")

    with c2:
        st.markdown('<div class="chart-card"><div class="chart-title">Experience Level Breakdown</div><div class="chart-subtitle">Distribution of seniority requirements across all listings</div></div>', unsafe_allow_html=True)
        st.plotly_chart(chart_experience_donut(filtered), use_container_width=True, key="exp_donut")

    st.markdown('<div class="chart-card"><div class="chart-title">Posting Activity Over Time</div><div class="chart-subtitle">Daily new listings ingested from Adzuna feed</div></div>', unsafe_allow_html=True)
    st.plotly_chart(chart_source_trend(filtered), use_container_width=True, key="trend_chart")

# ════════════════════════════════════
# TAB 3 — GEOGRAPHIC HEATMAP
# ════════════════════════════════════
with tab_geo:
    c1, c2 = st.columns([2, 1], gap="large")
    with c1:
        st.markdown('<div class="chart-card"><div class="chart-title">India Hiring Concentration Map</div><div class="chart-subtitle">Bubble size and colour intensity scaled to open roles. Dark-mode tile layer.</div></div>', unsafe_allow_html=True)
        map_data = build_map_data(filtered)
        st.plotly_chart(chart_india_map(map_data), use_container_width=True, key="india_map")
        st.markdown('<div class="map-note">Coordinates matched from city names in location field. \'Remote\' plotted at India centroid.</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="chart-card"><div class="chart-title">Hiring by Location</div><div class="chart-subtitle">Raw listing count per location string</div></div>', unsafe_allow_html=True)
        st.plotly_chart(chart_location_distribution(filtered), use_container_width=True, key="loc_bar")

# ════════════════════════════════════
# TAB 4 — COMPANY LEADERBOARD
# ════════════════════════════════════
with tab_companies:
    c1, c2 = st.columns([3, 2], gap="large")
    with c1:
        st.markdown('<div class="chart-card"><div class="chart-title">Company Hiring Volume Leaderboard</div><div class="chart-subtitle">Top 15 employers by total active postings in current dataset</div></div>', unsafe_allow_html=True)
        st.plotly_chart(chart_company_leaderboard(filtered), use_container_width=True, key="company_bar")

    with c2:
        # Table with top companies
        top_companies = filtered['company'].value_counts().head(15).reset_index()
        top_companies.columns = ['Company', 'Open Roles']
        top_companies.index = range(1, len(top_companies) + 1)
        st.markdown('<div class="chart-card"><div class="chart-title">Rankings Table</div><div class="chart-subtitle">Sortable breakdown with role count</div></div>', unsafe_allow_html=True)
        st.dataframe(
            top_companies,
            use_container_width=True,
            height=450,
        )

# ════════════════════════════════════
# TAB 5 — JOB LISTINGS
# ════════════════════════════════════
with tab_listings:
    # Search / filter
    s1, s2, s3 = st.columns([3, 2, 1])
    with s1:
        search_q = st.text_input("", placeholder="🔍  Search by title, company, or skill…", label_visibility="collapsed")
    with s2:
        exp_filter = st.selectbox("Experience", ["All", "Fresher / 0 yrs", "Internship",
                                                  "1 – 2 yrs", "2 – 3 yrs", "3 – 5 yrs",
                                                  "5 + yrs", "Not Specified"],
                                  label_visibility="collapsed")
    with s3:
        page_size = st.selectbox("Show", [20, 50, 100], label_visibility="collapsed")

    listing_df = filtered.copy()

    if search_q:
        q = search_q.lower()
        mask = (
            listing_df['title'].str.lower().str.contains(q, na=False) |
            listing_df['company'].str.lower().str.contains(q, na=False) |
            listing_df['tech_skills_found'].apply(
                lambda v: q in str(v).lower() if v is not None else False
            )
        )
        listing_df = listing_df[mask]

    if exp_filter != "All":
        listing_df['_exp_clean'] = listing_df['experience_level'].apply(clean_experience)
        listing_df = listing_df[listing_df['_exp_clean'] == exp_filter]

    total_shown = min(page_size, len(listing_df))
    st.markdown(f'<div style="font-size:13px;color:{PALETTE["text_muted"]};margin-bottom:16px;">'
                f'Showing <b style="color:{PALETTE["text_primary"]}">{total_shown:,}</b> '
                f'of {len(listing_df):,} listings</div>', unsafe_allow_html=True)

    for _, row in listing_df.head(page_size).iterrows():
        render_job_card(row)

# Close wrappers
st.markdown('</div></div>', unsafe_allow_html=True)
