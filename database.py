import psycopg2
import os
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """Establish and return a database connection."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )
        print("✅ Database connected successfully!")
        return conn
    except Exception as e:
        print("❌ Database connection failed:", e)
        raise e

def create_table_if_not_exists(conn):
    """Create annotations table if it doesn't exist."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS annotations (
                id SERIAL PRIMARY KEY,
                video_name TEXT,
                frame_name TEXT,
                frame_number INT,
                timestamp_sec INT,
                label TEXT
            );
        """)
        conn.commit()
        print("✅ Table 'annotations' verified/created successfully!")
    except Exception as e:
        print("❌ Error creating table:", e)
        conn.rollback()
        raise e

def init_db():
    """Initialize the database connection and ensure tables exist."""
    conn = get_connection()
    create_table_if_not_exists(conn)
    return conn
