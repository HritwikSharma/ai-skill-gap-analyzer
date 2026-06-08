import psycopg2

DB_HOST = "job-db.clgqc6scelz7.eu-north-1.rds.amazonaws.com"
DB_USER = "postgres"
DB_NAME = "postgres"
DB_PASSWORD = "HRITWIKSHARMA"

def create_unified_table():
    """
    Connects to the AWS RDS Postgres database and creates the unified job listings table.
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS job_listings (
        job_id VARCHAR(100) PRIMARY KEY,
        data_source VARCHAR(30) NOT NULL,
        title TEXT NOT NULL,
        company TEXT NOT NULL,
        location TEXT,
        description TEXT,
        job_url TEXT NOT NULL,
        extra_metadata JSONB
    );
    """
    
    try:
        print("Connecting to AWS RDS to create table...")
        conn = psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            database=DB_NAME,
            password=DB_PASSWORD,
            port="5432"
        )
        cursor = conn.cursor()
        
        cursor.execute(create_table_query)
        
        conn.commit()
        print("Success: 'job_listings' table is live and ready for data!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Database table creation failed: {e}")

if __name__ == "__main__":
    create_unified_table()