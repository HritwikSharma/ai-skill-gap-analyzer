import json
import re
import time
import requests
import psycopg2
from psycopg2.extras import Json

DB_HOST = "job-db.clgqc6scelz7.eu-north-1.rds.amazonaws.com"
DB_USER = "postgres"
DB_NAME = "postgres"
DB_PASSWORD = "HRITWIKSHARMA"

ADZUNA_APP_ID = "856e2554"
ADZUNA_APP_KEY = "89750d033fe565146c9e91e81966272e"
SERPAPI_KEY = "c299062e7ebc88ee2796181d4618007c009e60de9c83f8324cc32c8297422436"

def extract_database_skills(cursor, description_text):
    if not description_text:
        return [], []

    clean_text = description_text.replace("'", "''")

    cursor.execute(f"""
        SELECT skill_name FROM lookup_tech_skills 
        WHERE '{clean_text}' ILIKE '%' || skill_name || '%';
    """)
    tech_matches = [row[0] for row in cursor.fetchall()]

    cursor.execute(f"""
        SELECT skill_name FROM lookup_soft_skills 
        WHERE '{clean_text}' ILIKE '%' || skill_name || '%';
    """)
    soft_matches = [row[0] for row in cursor.fetchall()]

    return tech_matches, soft_matches

def extract_metrics(description_text, raw_job, source):
    desc_lower = description_text.lower() if description_text else ""
    experience_found = "Not Specified"
    
    exp_match = re.search(r"(\d+[\-+]\d*)\s*years", desc_lower)
    if exp_match:
        experience_found = exp_match.group(0)
    elif "internship" in desc_lower or "ppo" in desc_lower:
        experience_found = "Internship"
    elif "fresher" in desc_lower:
        experience_found = "Fresher"

    salary_found = "Not Specified"
    if source == "adzuna" and raw_job.get("salary_min"):
        salary_found = f"{raw_job.get('salary_min')} - {raw_job.get('salary_max')}"
    elif source == "serpapi" and raw_job.get("detected_extensions", {}).get("salary"):
        salary_found = raw_job.get("detected_extensions", {}).get("salary")
    else:
        salary_match = re.search(r"(₹|\bRs\b)\s*\d+[\d,]*", description_text or "")
        if salary_match:
            salary_found = salary_match.group(0)

    return {
        "experience_level": experience_found,
        "salary_extracted": salary_found
    }

def fetch_adzuna(cursor):
    print("\n--- Running Adzuna Extractor ---")
    url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": "50",
        "what": "Data Analyst"
    }
    try:
        res = requests.get(url, params=params)
        if res.status_code != 200: return
        
        jobs = res.json().get("results", [])
        for job in jobs:
            job_id = f"adz_{job.get('id')}"
            title = job.get("title", "Unknown Title")
            company = job.get("company", {}).get("display_name", "Unknown Company")
            location = job.get("location", {}).get("display_name", "Remote")
            description = job.get("description", "")
            job_url = job.get("redirect_url", "")
            
            tech_skills, soft_skills = extract_database_skills(cursor, description)
            metrics = extract_metrics(description, job, "adzuna")
            
            cursor.execute("""
                INSERT INTO job_listings (job_id, data_source, title, company, location, description, job_url, tech_skills_found, soft_skills_found, extra_metadata)
                VALUES (%s, 'adzuna', %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (job_id) DO NOTHING;
            """, (job_id, title, company, location, description, job_url, tech_skills, soft_skills, Json(metrics)))
        print(f"Stored {len(jobs)} jobs from Adzuna.")
    except Exception as e:
        print(f"Adzuna script block error: {e}")

def fetch_serpapi(cursor):
    print("\n--- Running SerpApi Extractor ---")
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_jobs",
        "q": "Data Analyst in India",
        "hl": "en",
        "api_key": SERPAPI_KEY,
        "start": "0"
    }
    try:
        res = requests.get(url, params=params)
        if res.status_code != 200: return
            
        jobs = res.json().get("jobs_results", [])
        for job in jobs:
            job_id = f"serp_{job.get('job_id')}"
            title = job.get("title", "Unknown Title")
            company = job.get("company_name", "Unknown Company")
            location = job.get("location", "Remote")
            description = job.get("description", "")
            job_url = job.get("related_links", [{}])[0].get("link", "https://google.com")
            
            tech_skills, soft_skills = extract_database_skills(cursor, description)
            metrics = extract_metrics(description, job, "serpapi")
            
            cursor.execute("""
                INSERT INTO job_listings (job_id, data_source, title, company, location, description, job_url, tech_skills_found, soft_skills_found, extra_metadata)
                VALUES (%s, 'serpapi', %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (job_id) DO NOTHING;
            """, (job_id, title, company, location, description, job_url, tech_skills, soft_skills, Json(metrics)))
        print(f"Stored {len(jobs)} jobs from SerpApi.")
    except Exception as e:
        print(f"SerpApi script block error: {e}")

def run_pipeline():
    print("=== STARTING UNIFIED DATA PIPELINE ===")
    try:
        conn = psycopg2.connect(host=DB_HOST, user=DB_USER, database=DB_NAME, password=DB_PASSWORD, port="5432")
        cursor = conn.cursor()
        
        fetch_adzuna(cursor)
        fetch_serpapi(cursor)
        
        conn.commit()
        print("\n=== PIPELINE SUCCESS: DATA RESTRUCTURE COMPLETED ===")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Pipeline run stopped: {e}")

if __name__ == "__main__":
    run_pipeline()