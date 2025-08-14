# mod/query.py - Query tracking functions

from modules.db_utils import get_db_connection

def save_query(chat_id, natural_language_query, generated_sql=None, result=None, db_id=None):
    """Save a query to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Convert result to string if it's not already
    if result is not None and not isinstance(result, str):
        result = str(result)
    
    cursor.execute(
        """
        INSERT INTO query (chat_id, db_id, natural_language_query, generated_sql, result)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (chat_id, db_id, natural_language_query, generated_sql, result)
    )
    
    query_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    
    return query_id

def get_chat_queries(chat_id):
    """Get all queries for a chat"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute(
        """
        SELECT q.*, db.db_name
        FROM query q
        LEFT JOIN database_connection db ON q.db_id = db.db_id
        WHERE q.chat_id = %s
        ORDER BY q.timestamp ASC
        """,
        (chat_id,)
    )
    
    queries = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return queries