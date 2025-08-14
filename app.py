# main.py - Main application file

import streamlit as st
from modules.auth import check_authentication, initialize_auth_state, handle_login, handle_register, handle_logout
from modules.chat import initialize_chat_state, handle_chat, create_new_chat, get_chat_messages, get_user_chats, save_message
from modules.db import get_db_connections, handle_database_connection, save_db_connection, get_db_connection_by_id
from modules.query import get_chat_queries, save_query
from modules.nav import get_query_params, set_query_params, navigate_to
from modules.db_setup import create_tables
import os

# Enhanced UI Configuration - Must be the first Streamlit command
st.set_page_config(
    page_title="Database Chat Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply CSS styling
def apply_styling():
    st.markdown("""
        <style>
        .main .block-container {
            padding-top: 2rem;
        }
        .stButton>button {
            width: 100%;
        }
        .css-1d391kg {
            padding-top: 1rem;
        }
        .auth-form {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .chat-container {
            height: 600px;
            overflow-y: auto;
            border: 1px solid #f0f0f0;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .db-card {
            background-color: #f0f4f8;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
            border-left: 3px solid #2196F3;
        }
        .sql-code {
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            white-space: pre-wrap;
        }
        </style>
    """, unsafe_allow_html=True)

def main():
    # Set up the database tables
    try:
        create_tables()
    except Exception as e:
        st.error(f"Failed to create tables: {str(e)}")
    
    # Initialize session state
    initialize_auth_state()
    initialize_chat_state()
    
    # Apply CSS styling
    apply_styling()
    
    # Check authentication using session cookie or URL token
    check_authentication()
    
    # Sidebar navigation
    render_sidebar()
    
    # Handle routing
    handle_routing()

def render_sidebar():
    with st.sidebar:
        st.title("Navigation")
        
        if st.session_state.is_authenticated:
            st.success(f"🔐 Logged in as: {st.session_state.username}")
            
            if st.button("💬 Chat Dashboard"):
                navigate_to("chat")
                
            if st.button("🗄️ Databases"):
                navigate_to("databases")
                
            if st.button("📊 History"):
                navigate_to("history")
                
            if st.button("📤 Logout"):
                handle_logout()
        else:
            st.warning("⚠ Not logged in")
            
            if st.button("🔑 Login"):
                navigate_to("login")
                
            if st.button("📝 Register"):
                navigate_to("register")

def handle_routing():
    # Enforce authentication for protected routes
    protected_routes = ["chat", "databases", "history"]
    if st.session_state.page in protected_routes and not st.session_state.is_authenticated:
        st.warning("⚠️ You need to log in to access this page")
        navigate_to("login")
        return

    # Route to the appropriate page
    if st.session_state.page == "login":
        render_login_page()
    elif st.session_state.page == "register":
        render_register_page()
    elif st.session_state.page == "chat":
        render_chat_page()
    elif st.session_state.page == "databases":
        render_databases_page()
    elif st.session_state.page == "history":
        render_history_page()

def render_login_page():
    st.title("🔑 Login")
    
    # Login form UI
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_submit = st.form_submit_button("Login")
        
        if login_submit:
            success = handle_login(username, password)
            if success:
                st.success("✅ Login successful!")
                st.rerun()
    
    # Navigation link
    st.write("Don't have an account?")
    if st.button("Register Now", key="goto_register"):
        navigate_to("register")

def render_register_page():
    st.title("📝 Register")
    
    # Registration form UI
    with st.form("register_form"):
        new_username = st.text_input("Username")
        new_email = st.text_input("Email")
        new_password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        register_submit = st.form_submit_button("Register")
        
        if register_submit:
            success = handle_register(new_username, new_email, new_password, confirm_password)
            if success:
                st.success("✅ Registration successful! You are now logged in.")
                st.rerun()
    
    # Navigation link
    st.write("Already have an account?")
    if st.button("Go to Login", key="goto_login"):
        navigate_to("login")

def render_chat_page():
    st.title("🔍 Database Chat Assistant")
    
    # Get user's chats
    chats = get_user_chats(st.session_state.user_id)
    
    # Sidebar for chat selection and settings
    with st.sidebar:
        st.markdown("### 💬 Your Chats")
        
        # New chat button
        if st.button("➕ New Chat"):
            st.session_state.current_chat_id = create_new_chat(st.session_state.user_id)
            st.session_state.active_db_id = None
            st.rerun()
        
        st.markdown("---")
        
        # List of existing chats
        for chat in chats:
            chat_title = chat['first_message']
            if len(chat_title) > 30:
                chat_title = chat_title[:30] + "..."
                
            created_date = chat['created_at'].strftime("%Y-%m-%d")
            if st.button(f"{chat_title} - {created_date}", key=f"chat_{chat['chat_id']}"):
                st.session_state.current_chat_id = chat['chat_id']
                st.rerun()
        
        st.markdown("---")
        
        # Database source selector
        render_source_selectors()
    
    # Main chat area
    if st.session_state.current_chat_id:
        # Get chat messages
        messages = get_chat_messages(st.session_state.current_chat_id)
        
        # Chat interface
        chat_container = st.container()
        with chat_container:
            for message in messages:
                # Fix: Check message type using isinstance with proper class
                from langchain_core.messages import AIMessage, HumanMessage
                if isinstance(message, AIMessage):
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(message.content)
                elif isinstance(message, HumanMessage):
                    with st.chat_message("user", avatar="👤"):
                        st.markdown(message.content)
        
        # Source indicator
        render_source_indicator()
        
        # Input area
        handle_chat()
    else:
        st.warning("⚠ No chat selected. Please create a new chat or select an existing one.")

def render_source_selectors():
    # Database connection selector
    st.markdown("### 🗄️ Database Source")
    
    # Get all saved database connections
    db_connections = get_db_connections()
    
    # Add "None" option
    db_options = ["None"] + [db['db_name'] for db in db_connections]
    
    # Get currently active db id
    active_db_name = "None"
    if st.session_state.active_db_id:
        for db in db_connections:
            if db['db_id'] == st.session_state.active_db_id:
                active_db_name = db['db_name']
    
    # Database selector
    selected_db = st.selectbox(
        "Select Database",
        db_options,
        index=db_options.index(active_db_name)
    )
    
    # Update active database
    if selected_db != active_db_name:
        if selected_db == "None":
            st.session_state.active_db_id = None
        else:
            for db in db_connections:
                if db['db_name'] == selected_db:
                    st.session_state.active_db_id = db['db_id']
                    break
        st.rerun()

def render_source_indicator():
    source_info = ""
    if st.session_state.active_db_id:
        db = get_db_connection_by_id(st.session_state.active_db_id)
        source_info = f"🗄️ Connected to database: **{db['db_name']}**"
    else:
        source_info = "⚠️ No database selected. Please select a database from the sidebar."
    
    st.markdown(source_info)

def render_databases_page():
    st.title("🗄️ Database Management")
    
    # Get all saved database connections
    db_connections = get_db_connections()
    
    # Database connections list
    st.markdown("### Saved Connections")
    
    if db_connections:
        for db in db_connections:
            with st.container():
                st.markdown(f"""
                <div class="db-card">
                    <h4>{db['db_name']}</h4>
                    <p>Type: {db['db_type']}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No database connections saved yet.")
    
    # Add new database connection form
    handle_database_connection()

def render_history_page():
    st.title("📊 Query History")
    
    # Get user's chats
    chats = get_user_chats(st.session_state.user_id)
    
    # Select chat
    chat_options = [(chat['chat_id'], f"Chat {chat['chat_id']} - {chat['created_at'].strftime('%Y-%m-%d')}") for chat in chats]
    
    selected_chat_id = None
    if chat_options:
        selected_chat = st.selectbox(
            "Select Chat",
            options=[option[1] for option in chat_options],
            index=0
        )
        
        # Get selected chat ID
        for option in chat_options:
            if option[1] == selected_chat:
                selected_chat_id = option[0]
                break
    
    if selected_chat_id:
        # Get queries for the selected chat
        queries = get_chat_queries(selected_chat_id)
        
        if queries:
            st.markdown("### Chat Queries")
            
            for query in queries:
                with st.expander(f"Query: {query['natural_language_query'][:50]}..."):
                    st.markdown(f"**User Query:** {query['natural_language_query']}")
                    st.markdown(f"**Timestamp:** {query['timestamp']}")
                    st.markdown(f"**Source:** Database - {query['db_name'] or 'None'}")
                    st.markdown("**Generated SQL:**")
                    st.code(query['generated_sql'], language="sql")
                    st.markdown("**Result:**")
                    st.markdown(query['result'])
        else:
            st.info("No queries found for this chat.")
    else:
        st.warning("No chats found. Start a conversation to see query history.")

if __name__ == "__main__":
    main()