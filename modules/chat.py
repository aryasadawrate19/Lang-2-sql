# mod/chat.py - Chat management functions

import streamlit as st
from modules.db_utils import get_db_connection
from langchain_core.messages import AIMessage, HumanMessage
from modules.db import get_db_connection_by_id, init_query_db
import json
import os
import google.generativeai as genai

# Initialize Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def initialize_chat_state():
    """Initialize chat-related session state variables"""
    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = None
        
    if "active_db_id" not in st.session_state:
        st.session_state.active_db_id = None
        
    if "last_query_result" not in st.session_state:
        st.session_state.last_query_result = None

def create_new_chat(user_id):
    """Create a new chat for the user and return the chat ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO chat (user_id) VALUES (%s)",
        (user_id,)
    )
    
    chat_id = cursor.lastrowid
    
    # Add welcome message
    cursor.execute(
        """
        INSERT INTO message (chat_id, content, is_system)
        VALUES (%s, %s, %s)
        """,
        (chat_id, "Hello! I am a SQL Assistant. Ask me anything about your database.", True)
    )
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return chat_id

def get_user_chats(user_id):
    """Get all chats for a user"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute(
        """
        SELECT c.chat_id, c.created_at, 
               (SELECT content FROM message 
                WHERE chat_id = c.chat_id 
                ORDER BY timestamp ASC 
                LIMIT 1) as first_message
        FROM chat c
        WHERE c.user_id = %s
        ORDER BY c.created_at DESC
        """,
        (user_id,)
    )
    
    chats = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return chats

def get_chat_messages(chat_id):
    """Get all messages for a chat"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute(
        """
        SELECT * FROM message
        WHERE chat_id = %s
        ORDER BY timestamp ASC
        """,
        (chat_id,)
    )
    
    messages = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Convert to langchain message format
    langchain_messages = []
    for msg in messages:
        if msg['is_system']:
            langchain_messages.append(AIMessage(content=msg['content']))
        else:
            langchain_messages.append(HumanMessage(content=msg['content']))
    
    return langchain_messages

def save_message(chat_id, content, is_system=False):
    """Save a message to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        INSERT INTO message (chat_id, content, is_system)
        VALUES (%s, %s, %s)
        """,
        (chat_id, content, is_system)
    )
    
    message_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    
    return message_id

def get_sqlchain(db):
    template = """
    You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database. You can modify the database (i.e. CREATE, UPDATE, DELETE, DROP) tables if needed.
    Based on the table schema below, write a SQL query that would answer the user's question. Take the conversation history into account.

    <SCHEMA>{schema}</SCHEMA>

    Conversation History: {chat_history}

    Write only the SQL query and nothing else. Do not wrap the SQL query in any other text, not even backticks.

    For example:
    Question: Which 3 artists have the most tracks?
    SQL Query: SELECT Artist, COUNT(*) as track_count FROM Track GROUP BY Artist ORDER BY track_count DESC LIMIT 3;

    Question: Show me all tables
    SQL Query: SHOW TABLES;

    Question: List tables
    SQL Query: SHOW TABLES;

    Question: What tables are in this database?
    SQL Query: SHOW TABLES;

    Question: What is the database schema?
    SQL Query: SHOW TABLES;

    Question: Name 10 artists
    SQL Query: SELECT Name FROM Artist LIMIT 10;

    Your turn:
    Question: {question}
    SQL Query:
    """
    
    def get_schema(_):
        return db.get_table_info()
    
    def query_gemini(inputs):
        # Format the prompt with the inputs
        schema = get_schema(None)
        
        # Convert chat history to string format
        chat_history_str = ""
        for message in inputs["chat_history"]:
            if isinstance(message, AIMessage):
                chat_history_str += f"AI: {message.content}\n"
            elif isinstance(message, HumanMessage):
                chat_history_str += f"Human: {message.content}\n"
        
        formatted_prompt = template.format(
            schema=schema,
            chat_history=chat_history_str,
            question=inputs["question"]
        )
        
        # Call Gemini directly with GenerativeModel
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(formatted_prompt)
        
        # Clean the response
        query = response.text.strip()
        return query.replace("sql", "").replace("```", "").strip()
    
    return query_gemini

def get_response(user_query, db, chat_history):
    """Generate AI response for database queries"""
    sql_chain = get_sqlchain(db)
    
    # Get the SQL query
    query = sql_chain({"question": user_query, "chat_history": chat_history})
    
    # Run the query
    try:
        sql_response = db.run(query)
    except Exception as e:
        return f"Error executing SQL query: {str(e)}\n\nThe query was: {query}", query, str(e)
    
    # Format the prompt for the response
    template = """
    You are a data analyst at a company. You are interacting with a user who is asking questions about the company's database.
    Based on the table schema below, question, sql query, and sql response, write a natural language response.
    <SCHEMA>{schema}</SCHEMA>

    Conversation History: {chat_history}
    SQL Query: <SQL>{query}</SQL>
    User Question: {question}
    SQL Response: {response}
    """
    
    # Convert chat history to string format
    chat_history_str = ""
    for message in chat_history:
        if isinstance(message, AIMessage):
            chat_history_str += f"AI: {message.content}\n"
        elif isinstance(message, HumanMessage):
            chat_history_str += f"Human: {message.content}\n"
    
    # Format the prompt with all the information
    formatted_prompt = template.format(
        schema=db.get_table_info(),
        chat_history=chat_history_str,
        query=query,
        question=user_query,
        response=sql_response
    )
    
    # Call Gemini directly for the response
    model = genai.GenerativeModel("gemini-2.0-flash-lite")
    response = model.generate_content(formatted_prompt)
    
    return response.text, query, sql_response

def handle_chat():
    """Handle user input in chat interface"""
    # Input area with placeholder
    user_query = st.chat_input("Ask me about your data...", key="user_input")
    
    if user_query is not None and user_query.strip() != "":
        # Save user message
        save_message(st.session_state.current_chat_id, user_query, is_system=False)
        
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_query)
        
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🤔 Thinking..."):
                if st.session_state.active_db_id:
                    # Get database connection info
                    db_info = get_db_connection_by_id(st.session_state.active_db_id)
                    connection_info = json.loads(db_info['connection_info'])
                    
                    # Initialize database connection
                    db = init_query_db(connection_info)
                    
                    # Get response
                    response, sql_query, sql_result = get_response(
                        user_query, 
                        db, 
                        get_chat_messages(st.session_state.current_chat_id)
                    )
                    
                    # Save query to database
                    from modules.query import save_query
                    save_query(
                        st.session_state.current_chat_id,
                        user_query,
                        sql_query,
                        sql_result,
                        st.session_state.active_db_id
                    )
                    
                    # Display response
                    st.markdown(response)
                    
                    # Save AI message
                    save_message(st.session_state.current_chat_id, response, is_system=True)
                    
                else:
                    response = "⚠️ No database selected. Please select a database from the sidebar."
                    st.markdown(response)
                    save_message(st.session_state.current_chat_id, response, is_system=True)
                    
        # Rerun to refresh chat history
        st.rerun()