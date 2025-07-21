import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

# Test connection
try:
    conn = psycopg2.connect(
        host="localhost",
        database="university_timetable",
        user="postgres",
        password="Titus7833@gmail"
    )
    print("✅ Database connection successful!")
    conn.close()
except Exception as e:
    print(f"❌ Database connection failed: {e}")