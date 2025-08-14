# mod/db.py - Database connection management

import streamlit as st
import json
from modules.db_utils import get_db_connection
from langchain_community.utilities import SQLDatabase

def get_db_connections():
    """Get all saved database connections"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM database_connection")
    
    connections = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return connections

def get_db_connection_by_id(db_id):
    """Get database connection by ID"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute(
        "SELECT * FROM database_connection WHERE db_id = %s",
        (db_id,)
    )
    
    db_connection = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return db_connection

def save_db_connection(db_name, connection_info, db_type):
    """Save database connection information"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        INSERT INTO database_connection (db_name, connection_info, db_type)
        VALUES (%s, %s, %s)
        """,
        (db_name, json.dumps(connection_info), db_type)
    )
    
    db_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    
    return db_id

def init_query_db(db_connection_info):
    """Initialize the database connection for SQL queries"""
    db_uri = f"mysql+mysqlconnector://{db_connection_info['user']}:{db_connection_info['password']}@{db_connection_info['host']}:{db_connection_info['port']}/{db_connection_info['database']}"
    return SQLDatabase.from_uri(db_uri)

def handle_database_connection():
    """Handle the database connection form"""
    st.markdown("### ➕ Add New Connection")
    
    with st.form("new_db_connection"):
        db_name = st.text_input("Connection Name")
        db_type = st.selectbox("Database Type", ["MySQL", "PostgreSQL", "SQLite"])
        
        # Connection parameters
        host = st.text_input("Host", value="localhost")
        port = st.text_input("Port", value="3306" if db_type == "MySQL" else "5432")
        user = st.text_input("Username")
        password = st.text_input("Password", type="password")
        database = st.text_input("Database Name")
        
        # Test and save buttons
        col1, col2 = st.columns(2)
        with col1:
            test_button = st.form_submit_button("Test Connection")
        with col2:
            save_button = st.form_submit_button("Save Connection")
        
        # Handle test connection
        if test_button:
            if db_name and host and port and user and database:
                try:
                    # Create connection info object
                    connection_info = {
                        "host": host,
                        "port": port,
                        "user": user,
                        "password": password,
                        "database": database
                    }
                    
                    # Try to initialize the database
                    with st.spinner("Testing connection..."):
                        db = init_query_db(connection_info)
                        # Try to get table info
                        db.get_table_info()
                        st.success("✅ Connection successful!")
                except Exception as e:
                    st.error(f"❌ Connection failed: {str(e)}")
            else:
                st.warning("Please fill in all required fields")
        
        # Handle save connection
        if save_button:
            if db_name and host and port and user and database:
                try:
                    # Create connection info object
                    connection_info = {
                        "host": host,
                        "port": port,
                        "user": user,
                        "password": password,
                        "database": database
                    }
                    
                    # Save connection
                    db_id = save_db_connection(db_name, connection_info, db_type)
                    st.success(f"✅ Connection saved with ID: {db_id}")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to save connection: {str(e)}")
            else:
                st.warning("Please fill in all required fields")