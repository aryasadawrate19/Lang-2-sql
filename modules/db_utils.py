# modules/db_utils.py
import os
from dotenv import load_dotenv
# Only import mysql.connector inside the function
# to avoid circular imports

# Load environment variables
load_dotenv()

def get_db_connection():
    """Get connection to the lang2sql database"""
    import mysql.connector  # Import here to avoid circular import
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        port=os.getenv("DB_PORT", "3306"),
        database=os.getenv("DB_NAME", "lang2sql")
    )