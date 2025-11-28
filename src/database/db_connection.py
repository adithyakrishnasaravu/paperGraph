# test file to test the database connection
import os
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def test_database_connection():
    ''' test the database connection'''
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor()

        # test query
        cursor.execute("SELECT COUNT(*) FROM node_types;")
        result = cursor.fetchone()[0]

        print("Connection successful")
        print(f"Number of node types: {result}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

if __name__ == "__main__":
    test_database_connection()