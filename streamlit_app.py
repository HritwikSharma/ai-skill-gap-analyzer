import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import json
from collections import Counter

# --- AWS Database Credentials ---
DB_HOST = "job-db.clgqc6scelz7.eu-north-1.rds.amazonaws.com"
DB_USER = "postgres"
DB_NAME = "postgres"
DB_PASSWORD = "HRITWIKSHARMA"

@st.cache_data(ttl=300)  # Caches the data for 5 minutes to stay snappy
def fetch_job_data():
    """Connects to AWS RDS and fetches the processed job marketplace data."""
    try:
        conn = psycopg2.connect(host=DB_HOST, user=DB_USER, database=DB_NAME, password=DB_PASSWORD, port="5432")
        query = """
            SELECT title, company, location, tech_skills_found, extra_metadata 
            FROM job_listings;
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error connecting to AWS Database: {e}")
        return pd.DataFrame()

# --- Pre-defined Coordinates for Major Indian Job Hubs ---
# This translates text locations from Adzuna directly into Map coordinates
INDIAN_CITIES_COORDS = {
    'bengaluru': [12.9716, 77.5946], 'bangalore': [12.9716, 77.5946],
    'hyderabad': [17.3850, 78.4867],
    'pune': [18.5204, 73.8567],
    'mumbai': [19.0760, 72.8777],
    'chennai': [13.0827, 80.2707],
    'delhi': [28.6139, 77.2090], 'new delhi': [28.6139, 77.2090],
    'gurgaon': [28.4595, 77.0266], 'gurugram': [28.4595, 77.0266],
    'noida': [28.5355, 77.3910],
    'kolkata': [22.5726, 88.3639],
    'ahmedabad': [23.0225, 72.5714],
    'jaipur': [26.9124, 75.7873],
    'coimbatore': [11.0168, 76.9558],
    'thiruvananthapuram': [8.5241, 76.9366], 'trivandrum': [8.5241, 76.9366],
    'kochi': [9.9312, 76.2673], 'cochin': [9.9312, 76.2673],
    'remote': [20.5937, 78.9629] # Center of India for remote listings
}

def process_locations_for_map(dataframe):
    """Maps text locations to lat/lon coordinates and aggregates job counts."""
    map_data = []
    for loc in dataframe['location'].dropna():
        loc_clean = str(loc).strip().lower()
        
        # Check if the city exists in our Indian coordinates dictionary
        matched_city = None
        for city in INDIAN_CITIES_COORDS:
            if city in loc_clean:
                matched_city = city
                break
                
        if matched_city:
            lat, lon = INDIAN_CITIES_COORDS[matched_city]
            map_data.append({'City': matched_city.title(), 'lat': lat, 'lon': lon})
            
    if not map_data:
        return pd.DataFrame()
        
    map_df = pd.DataFrame(map_data)
    # Count how many jobs are in each city to set the map bubble sizes
    agg_df = map_df.groupby(['City', 'lat', 'lon']).size().reset_index(name='Job Openings')
    return agg_df

# --- Page UI Configuration ---
st.set_page_config(page_title="AI Skill Gap & Market Analyzer", layout="wide")
st.title("📊 Tech Market Demand & Skill Gap Analyzer")
st.markdown("Real-time data visualization layer connected directly to automated AWS data processing.")

# Load data from your database
df = fetch_job_data()

if df.empty:
    st.warning("⚠️ Waiting for data or connection failed. Make sure your GitHub Action run completed successfully and rows are visible in pgAdmin.")
else:
    # --- Sidebar Filtering Layer ---
    st.sidebar.header("🎯 Filter Market Options")
    
    # Standardize job categories based on raw titles
    raw_titles = df['title'].dropna().unique()
    # Provide a few key categories or let them choose raw titles
    selected_role = st.sidebar.selectbox("Select Target Job Role", ["All Technical Roles"] + list(raw_titles)[:15])
    
    # Filter dataset based on selection
    filtered_df = df if selected_role == "All Technical Roles" else df[df['title'] == selected_role]

    # --- Top Key Performance Metrics Row ---
    st.markdown("### 📈 Market At A Glance")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Jobs Evaluated", len(filtered_df))
    with col2:
        st.metric("Unique Employers Hiring", filtered_df['company'].nunique())
    with col3:
        # Extract location hotspot
        top_loc = filtered_df['location'].mode().dropna()
        st.metric("Top Hiring Hub", top_loc[0] if not top_loc.empty else "N/A")

    st.markdown("---")

    # --- Layout Grid: Split Dashboard into 2 Columns ---
    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.markdown("### 🔥 In-Demand Technical Skills")
        # Flatten string arrays from PostgreSQL
        all_tech_skills = []
        for skill_list in filtered_df['tech_skills_found'].dropna():
            if isinstance(skill_list, list):
                all_tech_skills.extend(skill_list)
                
        if all_tech_skills:
            skill_counts = Counter(all_tech_skills)
            top_skills_df = pd.DataFrame(skill_counts.most_common(12), columns=['Skill', 'Mentions'])
            
            fig_skills = px.bar(top_skills_df, x='Mentions', y='Skill', orientation='h',
                                color='Mentions', color_continuous_scale='teal',
                                labels={'Mentions': 'Number of Job Postings'})
            fig_skills.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, height=450)
            st.plotly_chart(fig_skills, use_container_width=True)
        else:
            st.info("No explicit O*NET skills matched in this specific category subset yet.")

    with right_col:
        st.markdown("### 🗺️ India Job Hotspot Distribution")
        map_plot_data = process_locations_for_map(filtered_df)
        
        if not map_plot_data.empty:
            # Render interactive geographic scatter plot on an actual map layout
            fig_map = px.scatter_mapbox(
                map_plot_data, lat="lat", lon="lon", size="Job Openings", color="Job Openings",
                color_continuous_scale="Viridis", size_max=40, zoom=3.8,
                center={"lat": 22.5937, "lon": 78.9629},  # Centers view precisely on India
                mapbox_style="carto-positron", hover_name="City",
                title="Geographic Hiring Concentrations"
            )
            fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, height=450)
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("Mapping location data points... Make sure fields contain recognized Indian city names.")

    # --- Full Data Inspection Layer ---
    st.markdown("---")
    st.markdown("### 🔍 Raw Market Data Records Exploratory View")
    st.dataframe(filtered_df[['title', 'company', 'location', 'tech_skills_found']], use_container_width=True)
