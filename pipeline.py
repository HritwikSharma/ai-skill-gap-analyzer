import json
import re
import time
import requests
import psycopg2
from psycopg2.extras import Json
import streamlit as st

# Secure credentials fetched from secrets management container
DB_HOST     = st.secrets["database"]["host"]
DB_USER     = st.secrets["database"]["user"]
DB_NAME     = st.secrets["database"]["database"]
DB_PASSWORD = st.secrets["database"]["password"]

# API Credentials safely abstracted
ADZUNA_APP_ID  = st.secrets["adzuna"]["app_id"]
ADZUNA_APP_KEY = st.secrets["adzuna"]["app_key"]

# Core target sectors to prevent junk data from diluting the index
TARGET_KEYWORDS = ["Data Analyst", "Data Scientist", "Business Analyst", "Data Engineer", "Machine Learning"]

def load_skills_dictionaries(cursor):
    """Fetches O*NET dictionary tables from AWS to perform processing entirely in local memory."""
    try:
        cursor.execute("SELECT DISTINCT LOWER(skill_name) FROM lookup_tech_skills;")
        tech_skills = [row[0] for row in cursor.fetchall() if row[0]]
        
        cursor.execute("SELECT DISTINCT LOWER(skill_name) FROM lookup_soft_skills;")
        soft_skills = [row[0] for row in cursor.fetchall() if row[0]]
        
        return tech_skills, soft_skills
    except Exception as e:
        print(f"Extraction Error: Failed to fetch lookup reference tables: {e}")
        return [], []

def preprocess_and_parse_skills(description_text, tech_dict, soft_dict):
    """Sanitizes raw text descriptions and parses them using standard word-boundary regex maps."""
    if not description_text:
        return [], []
    
    # Strip special punctuation marks and cast to lowercase for perfect matching
    clean_text = re.sub(r'[^\w\s]', ' ', description_text.lower())
    
    # Extract string matching tokens based on exact O*NET boundary sets (\b)
    tech_matches = [skill.title() for skill in tech_dict if re.search(r'\b' + re.escape(skill) + r'\b', clean_text)]
    soft_matches = [skill.title() for skill in soft_dict if re.search(r'\b' + re.escape(skill) + r'\b', clean_text)]
    
    # Deduplicate list collections cleanly
    return list(set(tech_matches)), list(set(soft_matches))

def extract_metrics_metadata(job, description_text):
    """Extracts raw salary data, system boundaries, and experience levels into a JSON matrix."""
    desc_lower = description_text.lower() if description_text else ""
    experience_found = "Not Specified"
    
    # Regex pattern matching for standard year metrics (e.g., '2-5 years', '3+ years')
    exp_match = re.search(r"(\d+[\-+]\d*)\s*years", desc_lower)
    if exp_match:
        experience_found = exp_match.group(0)
    elif "internship" in desc_lower or "ppo" in desc_lower:
        experience_found = "Internship"
    elif "fresher" in desc_lower:
        experience_found = "Fresher"

    # Capture API structural salary variables or parse raw string definitions directly
    salary_min = job.get("salary_min")
    salary_max = job.get("salary_max")
    
    if salary_min and salary_max:
        salary_string = f"₹ {salary_min} - ₹ {salary_max}"
    elif salary_min:
        salary_string = f"₹ {salary_min}+"
    else:
        # Secondary fallback regex string lookup strategy for native character formats
        salary_match = re.search(r"(₹|\bRs\b)\s*\d+[\d,]*", description_text)
        salary_string = salary_match.group(0) if salary_match else "Not Specified"

    return {
        "experience_level": experience_found,
        "salary_extracted": salary_string,
        "company_tier_raw": job.get("company", {}).get("display_name", "Unknown"),
        "created_timestamp": job.get("created", "")
    }

def run_global_sync():
    print("=== STARTING CLOUD PREPROCESSING PIPELINE ENGINE ===")
    try:
        # Establish AWS RDS Connection Gateway
        conn = psycopg2.connect(host=DB_HOST, user=DB_USER, database=DB_NAME, password=DB_PASSWORD, port="5432")
        cursor = conn.cursor()
        
        # Load O*NET dictionaries from database tables
        tech_dict, soft_dict = load_skills_dictionaries(cursor)
        print(f"Dictionaries Synced. Technical Keywords: {len(tech_dict)} | Soft Keywords: {len(soft_dict)}")
        
        if not tech_dict and not soft_dict:
            print("Aborting Run: O*NET base schemas are missing from AWS destination database tables.")
            return

        for keyword in TARGET_KEYWORDS:
            print(f"\nProcessing Pipeline Segment: [{keyword}]")
            
            # Request and loop across 10 complete pages to aggregate 500 job slots per category query
            for page in range(1, 11):
                url = f"https://api.adzuna.com/v1/api/jobs/in/search/{page}"
                params = {
                    "app_id": ADZUNA_APP_ID,
                    "app_key": ADZUNA_APP_KEY,
                    "results_per_page": "50",
                    "what": keyword
                }
                try:
                    res = requests.get(url, params=params)
                    if res.status_code == 429:
                        print("Rate limit flag thrown. Cool down interval active...")
                        time.sleep(5)
                        continue
                    if res.status_code != 200:
                        break
                        
                    jobs = res.json().get("results", [])
                    if not jobs:
                        break
                        
                    for job in jobs:
                        job_id = f"adz_{job.get('id')}"
                        title = job.get("title", "Unknown Title")
                        company = job.get("company", {}).get("display_name", "Unknown Company")
                        location = job.get("location", {}).get("display_name", "Remote")
                        description = job.get("description", "")
                        job_url = job.get("redirect_url", "")
                        
                        # Apply computational filtering and processing layer inside server memory
                        tech_skills, soft_skills = preprocess_and_parse_skills(description, tech_dict, soft_dict)
                        extra_metadata = extract_metrics_metadata(job, description)
                        
                        cursor.execute("""
                            INSERT INTO job_listings (job_id, data_source, title, company, location, description, job_url, tech_skills_found, soft_skills_found, extra_metadata)
                            VALUES (%s, 'adzuna', %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (job_id) DO NOTHING;
                        """, (job_id, title, company, location, description, job_url, tech_skills, soft_skills, Json(extra_metadata)))
                        
                    conn.commit() # Safely commit data structures page-by-page
                except Exception as page_err:
                    print(f"Exception encountered inside pagination index: {page_err}")
                    
        print("\n=== PIPELINE SYNC SUCCESSFUL: AWS LEDGER IS COMPLETELY UPDATED ===")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Critical System Failure: {e}")

if __name__ == "__main__":
    run_global_sync()
