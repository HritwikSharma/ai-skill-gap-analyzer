import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import plotly.graph_objects as go
import json
import re
import html
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
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Job Card Styles ── */
.job-card {
    background-color: #ffffff;
    border: 1px solid #eef2f6;
    border-radius: 10px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.job-card:hover {
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    transform: translateY(-2px);
}
.job-title {
    font-size: 1.25rem;
    font-family: 'Sora', sans-serif;
    font-weight: 600;
    margin-bottom: 8px;
}
.job-title a {
    color: #0A66C2;
    text-decoration: none;
}
.job-title a:hover {
    text-decoration: underline;
}
.job-company {
    font-size: 1rem;
    font-weight: 500;
    color: #333333;
    margin-bottom: 12px;
}
.job-meta {
    display: flex;
    gap: 16px;
    font-size: 0.85rem;
    color: #666666;
    margin-bottom: 16px;
}
.job-skills {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 20px;
}
.skill-pill, .salary-badge, .exp-badge {
    font-size: 0.75rem;
    padding: 4px 10px;
    border-radius: 999px;
    font-weight: 500;
}
.skill-pill { background-color: #f0f2f5; color: #333; }
.salary-badge { background-color: #e6f4ea; color: #137333; }
.exp-badge { background-color: #e8f0fe; color: #1a73e8; }

/* ── Button Fixes ── */
.apply-btn {
    display: inline-block;
    background-color: #0A66C2;
    color: #ffffff !important;
    text-decoration: none !important;
    padding: 10px 20px;
    border-radius: 6px;
    font-size: 0.9rem;
    font-weight: 600;
    text-align: center;
    transition: background-color 0.2s;
}
.apply-btn:hover {
    background-color: #004182;
}

/* ── Pagination (Number List) Fix ── */
div[data-testid="stRadio"] > div {
    display: flex;
    flex-direction: row;
    gap: 10px;
    flex-wrap: wrap;
}
div[data-testid="stRadio"] label {
    padding: 5px 15px;
    background: #f0f2f5;
    border-radius: 6px;
    cursor: pointer;
}
</style>
"""
st.markdown(THEME, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  DATA FETCHING
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_data():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME
        )
        query = "SELECT * FROM jobs" # Adjust table name if different
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Failed to connect to database: {e}")
        return pd.DataFrame()

df = fetch_data()

if df.empty:
    st.warning("No data found or database connection failed.")
    st.stop()

# ─────────────────────────────────────────────
#  DATA CLEANING & CATEGORIZATION
# ─────────────────────────────────────────────
# 1. Experience Mapping
def map_experience(exp):
    exp_str = str(exp).lower()
    if pd.isna(exp) or "none" in exp_str or "not specified" in exp_str: return "Not specified"
    if "intern" in exp_str: return "Internship"
    if any(x in exp_str for x in ["fresher", "0", "<1", "entry"]): return "<1 year"
    if any(x in exp_str for x in ["1", "2", "3", "4", "5"]): return "1-5 years"
    if any(x in exp_str for x in ["6", "7", "8", "9", ">5", "+"]): return ">5 years"
    return "Not specified"

if 'experience_level' in df.columns:
    df['mapped_exp'] = df['experience_level'].apply(map_experience)
else:
    df['mapped_exp'] = "Not specified"

# 2. Extract Skills List
if 'tech_skills_found' in df.columns:
    df['skills_list'] = df['tech_skills_found'].apply(
        lambda x: json.loads(x.replace("'", '"')) if isinstance(x, str) and '[' in x else (x if isinstance(x, list) else [])
    )
else:
    df['skills_list'] = [[] for _ in range(len(df))]

# ─────────────────────────────────────────────
#  LAYOUT: CONTINUOUS FLOW DASHBOARD
# ─────────────────────────────────────────────
tab_dashboard, tab_jobs = st.tabs(["📈 Market Analytics", "💼 Job Search"])

with tab_dashboard:
    st.title("TalentPulse Market Analytics")
    st.markdown("Explore continuous market trends without broken layout blocks.")

    # -- ROW 1: Skills & Experience --
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top 15 In-Demand Technical Skills")
        all_skills = [skill for sublist in df['skills_list'] for skill in sublist]
        top_skills = pd.DataFrame(Counter(all_skills).most_common(15), columns=['Skill', 'Count'])
        fig_skills = px.bar(top_skills, x='Count', y='Skill', orientation='h', 
                            color_discrete_sequence=['#2C3E50']) # Better Color
        fig_skills.update_layout(yaxis={'categoryorder': 'total ascending'})
        fig_skills.update_traces(hoverlabel_font_color='black') # Hover text black
        st.plotly_chart(fig_skills, use_container_width=True)

    with col2:
        st.subheader("Experience Level Distribution")
        exp_df = df[df['mapped_exp'] != "Not specified"] # Removed "Not specified"
        exp_counts = exp_df['mapped_exp'].value_counts().reset_index()
        exp_counts.columns = ['Experience', 'Count']
        
        # Only requested categories kept: Internship, <1 year, 1-5 years, >5 years
        fig_exp = px.pie(exp_counts, names='Experience', values='Count', hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        # Labels inside the circle
        fig_exp.update_traces(textposition='inside', textinfo='label+percent', 
                              hoverlabel_font_color='black')
        st.plotly_chart(fig_exp, use_container_width=True)

    st.markdown("---")

    # -- ROW 2: Salary & Demand --
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Overall Salary Distribution (LPA)")
        # Assuming salary_lpa or similar numeric column exists. Using generic fallback if not.
        salary_col = 'salary_lpa' if 'salary_lpa' in df.columns else 'salary_str' 
        fig_salary = px.histogram(df, x=salary_col, color_discrete_sequence=['#109618']) # Better Color
        fig_salary.update_traces(hoverlabel_font_color='black') # Hover text black
        st.plotly_chart(fig_salary, use_container_width=True)

    with col4:
        st.subheader("Role Demand — Proportional View (Top 15)")
        # Show ONLY top 15 jobs
        role_col = 'title' if 'title' in df.columns else 'job_title'
        top_roles = df[role_col].value_counts().nlargest(15).reset_index()
        top_roles.columns = ['Role', 'Count']
        fig_roles = px.pie(top_roles, names='Role', values='Count', 
                           color_discrete_sequence=px.colors.sequential.Teal)
        fig_roles.update_traces(textposition='inside', textinfo='percent', 
                                hoverlabel_font_color='black')
        st.plotly_chart(fig_roles, use_container_width=True)

    st.markdown("---")

    # -- ROW 3: Companies & Geography --
    col5, col6 = st.columns(2)

    with col5:
        st.subheader("Top 20 Hiring Companies")
        company_col = 'company'
        if company_col in df.columns:
            top_companies = df[company_col].value_counts().nlargest(20).reset_index()
            top_companies.columns = ['Company', 'Count']
            fig_comp = px.bar(top_companies, x='Company', y='Count', 
                              color_discrete_sequence=['#E67E22'])
            fig_comp.update_traces(hoverlabel_font_color='black') # Hover text black
            st.plotly_chart(fig_comp, use_container_width=True)

    with col6:
        st.subheader("Geographic Distribution of Tech Hiring — India")
        # Treemap used to generate a geographic heatmap visual with gradient
        if 'location' in df.columns:
            geo_counts = df['location'].value_counts().reset_index()
            geo_counts.columns = ['Location', 'Hiring Volume']
            fig_geo = px.treemap(geo_counts, path=['Location'], values='Hiring Volume',
                                 color='Hiring Volume', 
                                 color_continuous_scale='Magma') # Gradient Heatmap Intensity
            fig_geo.update_traces(hoverlabel_font_color='black')
            st.plotly_chart(fig_geo, use_container_width=True)

# ─────────────────────────────────────────────
#  LAYOUT: JOB BOARD & PAGINATION
# ─────────────────────────────────────────────
with tab_jobs:
    st.header("Latest Job Postings")
    
    # Simple pagination mapping (Number List Format)
    items_per_page = 15
    total_pages = max(1, (len(df) - 1) // items_per_page + 1)
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1

    # Show pagination as a horizontal radio list instead of +/- large box
    page_selection = st.radio(
        "Page:",
        options=range(1, total_pages + 1),
        index=st.session_state.current_page - 1,
        horizontal=True,
        label_visibility="collapsed"
    )
    st.session_state.current_page = page_selection
    
    start_idx = (st.session_state.current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    paginated_df = df.iloc[start_idx:end_idx]

    st.markdown("<br>", unsafe_allow_html=True)

    # Rendering the cards
    for idx, row in paginated_df.iterrows():
        # CRITICAL: html.escape prevents characters like `<` or `>` in text from breaking the UI elements
        title   = html.escape(str(row.get("title", row.get("job_title", "No Title"))))
        company = html.escape(str(row.get("company", "Company Unspecified")))
        loc     = html.escape(str(row.get("location", "Location Unspecified")))
        sal     = html.escape(str(row.get("salary_str", "Not disclosed")))
        exp     = html.escape(str(row.get("experience_level", "Not specified")))
        
        # Replace quotes to secure the URL attribute
        url = str(row.get("job_url", "#")).replace('"', '%22')
        posted = str(row.get("posted_date", ""))[:10]
        
        # Extract skills safely
        skills = row.get("skills_list", [])
        skills_html = "".join(
            f'<span class="skill-pill">{html.escape(str(s))}</span>'
            for s in (skills[:6] if isinstance(skills, list) else [])
        )

        sal_badge = f'<span class="salary-badge">{sal}</span>' if sal != "Not disclosed" and sal != "nan" else ""
        exp_badge = f'<span class="exp-badge">{exp}</span>' if exp != "Not specified" and exp != "nan" else ""
        posted_str = f'<span class="job-meta-item">📅 {html.escape(posted)}</span>' if posted and posted not in ["None", "nan", "NaT"] else ""

        # Using unsafe_allow_html=True
        st.markdown(f"""
        <div class="job-card">
            <div class="job-title"><a href="{url}" target="_blank">{title}</a></div>
            <div class="job-company">{company}</div>
            <div class="job-meta">
                <span class="job-meta-item">📍 {loc}</span>
                {posted_str}
            </div>
            <div class="job-skills">
                {sal_badge}
                {exp_badge}
                {skills_html}
            </div>
            <a href="{url}" target="_blank" class="apply-btn">View & Apply</a>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
