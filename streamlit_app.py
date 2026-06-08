import streamlit as st
import pandas as pd
import psycopg2
import requests
from psycopg2.extras import Json

DB_HOST = "job-db.clgqc6scelz7.eu-north-1.rds.amazonaws.com"
DB_USER = "postgres"
DB_NAME = "postgres"
DB_PASSWORD = "HRITWIKSHARMA"
SERPAPI_KEY = "c299062e7ebc88ee2796181d4618007c009e60de9c83f8324cc32c8297422436"

def get_db_connection():
    return psycopg2.connect(host=DB_HOST, user=DB_USER, database=DB_NAME, password=DB_PASSWORD)

def extract_skills_live(cursor, description_text):
    if not description_text:
        return [], []
    clean_text = description_text.replace("'", "''")
    
    cursor.execute(f"SELECT skill_name FROM lookup_tech_skills WHERE '{clean_text}' ILIKE '%' || skill_name || '%';")
    tech_matches = [row[0] for row in cursor.fetchall()]
    
    cursor.execute(f"SELECT skill_name FROM lookup_soft_skills WHERE '{clean_text}' ILIKE '%' || skill_name || '%';")
    soft_matches = [row[0] for row in cursor.fetchall()]
    
    return tech_matches, soft_matches

def trigger_live_serpapi_search(search_query):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_jobs",
        "q": search_query,
        "hl": "en",
        "gl": "in",
        "api_key": SERPAPI_KEY
    }
    try:
        res = requests.get(url, params=params)
        if res.status_code == 200:
            jobs = res.json().get("jobs_results", [])
            for job in jobs:
                job_id = f"serp_{job.get('job_id')}"
                title = job.get("title", "Unknown Title")
                company = job.get("company_name", "Unknown Company")
                location = job.get("location", "India")
                description = job.get("description", "")
                job_url = job.get("related_links", [{}])[0].get("link", "https://google.com")
                
                tech_skills, soft_skills = extract_skills_live(cursor, description)
                
                cursor.execute("""
                    INSERT INTO job_listings (job_id, data_source, title, company, location, description, job_url, tech_skills_found, soft_skills_found)
                    VALUES (%s, 'serpapi_live', %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (job_id) DO NOTHING;
                """, (job_id, title, company, location, description, job_url, tech_skills, soft_skills))
            conn.commit()
    except Exception as e:
        st.error(f"Live search retrieval failed: {e}")
    finally:
        cursor.close()
        conn.close()

st.set_page_config(page_title="Indian Market Job Analytics Engine", layout="wide")
st.title("📊 Data Analytics Job Market Intelligence (India)")

st.sidebar.header("🔍 Real-Time Job Discovery")
user_query = st.sidebar.text_input("Enter target job role or specific keyword:")
run_search = st.sidebar.button("Execute Live Search Query")

if run_search and user_query:
    with st.spinner(f"Querying SerpApi for fresh listings matching '{user_query}'..."):
        trigger_live_serpapi_search(user_query)
        st.sidebar.success("Database synchronized with live search results!")

try:
    conn = get_db_connection()
    df = pd.read_sql("SELECT title, company, location, tech_skills_found, soft_skills_found FROM job_listings;", conn)
    conn.close()
    
    if not df.empty:
        st.sidebar.header("🎛️ Interactive Filters")
        
        locations = ["All"] + sorted(list(df['location'].dropna().unique()))
        selected_location = st.sidebar.selectbox("Filter by Location:", locations)
        
        titles = ["All"] + sorted(list(df['title'].dropna().unique()))
        selected_title = st.sidebar.selectbox("Filter by Job Title:", titles)
        
        filtered_df = df.copy()
        if selected_location != "All":
            filtered_df = filtered_df[filtered_df['location'] == selected_location]
        if selected_title != "All":
            filtered_df = filtered_df[filtered_df['title'] == selected_title]

        st.subheader("📈 Aggregated Market Dashboard")
        
        col1, col2 = st.columns(2)
        
        with col1:
            all_tech = [skill for sublist in filtered_df['tech_skills_found'].dropna() for skill in sublist]
            if all_tech:
                tech_counts = pd.Series(all_tech).value_counts().head(10)
                st.write("### Top Technical Skills in Demand")
                st.bar_chart(tech_counts)
            else:
                st.info("No technical skills extracted for this specific filter view.")
                
        with col2:
            all_soft = [skill for sublist in filtered_df['soft_skills_found'].dropna() for skill in sublist]
            if all_soft:
                soft_counts = pd.Series(all_soft).value_counts().head(10)
                st.write("### Top Soft Skills in Demand")
                st.bar_chart(soft_counts)
            else:
                st.info("No soft skills extracted for this specific filter view.")

        st.subheader("💼 Active Job Ledger Database View")
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.info("The AWS database is currently empty. Enter an industry search term in the sidebar menu to run your first automated scrape pipeline cycle.")

except Exception as e:
    st.error(f"Could not connect or fetch data from AWS database: {e}")