# mod/db_setup.py - Database table creation

from modules.db_utils import get_db_connection

def create_tables():
    """Create all necessary tables if they don't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create sessions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        token VARCHAR(255) UNIQUE NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    # Create chat table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat (
        chat_id INT AUTO_INCREMENT PRIMARY KEY,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        user_id INT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')
    
    # Create message table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS message (
        message_id INT AUTO_INCREMENT PRIMARY KEY,
        chat_id INT NOT NULL,
        content TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_system BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (chat_id) REFERENCES chat(chat_id)
    )
    ''')
    
    # Create database connection table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS database_connection (
        db_id INT AUTO_INCREMENT PRIMARY KEY,
        db_name VARCHAR(255) NOT NULL,
        connection_info TEXT NOT NULL,
        db_type VARCHAR(50) NOT NULL
    )
    ''')
    
    # Create query table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS query (
        query_id INT AUTO_INCREMENT PRIMARY KEY,
        chat_id INT NOT NULL,
        db_id INT,
        natural_language_query TEXT NOT NULL,
        generated_sql TEXT,
        result TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (chat_id) REFERENCES chat(chat_id),
        FOREIGN KEY (db_id) REFERENCES database_connection(db_id)
    )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()