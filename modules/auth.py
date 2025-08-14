# mod/auth.py - Authentication functions

import streamlit as st
import hashlib
import uuid
import datetime
from modules.db_utils import get_db_connection
from modules.nav import set_query_params

def initialize_auth_state():
    """Initialize authentication-related session state variables"""
    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False

    if "user_id" not in st.session_state:
        st.session_state.user_id = None

    if "username" not in st.session_state:
        st.session_state.username = None
        
    if "page" not in st.session_state:
        st.session_state.page = "login"

    if "session_token" not in st.session_state:
        st.session_state.session_token = None

def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    return hash_password(provided_password) == stored_password

def generate_session_token():
    """Generate a unique session token"""
    return str(uuid.uuid4())

def save_session(user_id, username, session_token):
    """Save session information to database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Set expiration time (e.g., 30 days from now)
    expiry = datetime.datetime.now() + datetime.timedelta(days=30)
    expiry_str = expiry.strftime('%Y-%m-%d %H:%M:%S')
    
    # Check if a session exists for this user
    cursor.execute(
        "SELECT id FROM sessions WHERE user_id = %s",
        (user_id,)
    )
    session = cursor.fetchone()
    
    if session:
        # Update existing session
        cursor.execute(
            "UPDATE sessions SET token = %s, expires_at = %s WHERE user_id = %s",
            (session_token, expiry_str, user_id)
        )
    else:
        # Create new session
        cursor.execute(
            "INSERT INTO sessions (user_id, token, expires_at) VALUES (%s, %s, %s)",
            (user_id, session_token, expiry_str)
        )
    
    conn.commit()
    cursor.close()
    conn.close()
    
    # Store in session state
    st.session_state.session_token = session_token
    st.session_state.is_authenticated = True
    st.session_state.user_id = user_id
    st.session_state.username = username

def validate_session(session_token):
    """Validate a session token and return user information if valid"""
    if not session_token:
        return None
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get session information
    cursor.execute(
        """
        SELECT s.*, u.username
        FROM sessions s
        JOIN users u ON s.user_id = u.id
        WHERE s.token = %s AND s.expires_at > NOW()
        """,
        (session_token,)
    )
    
    session = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if session:
        return {
            'user_id': session['user_id'],
            'username': session['username']
        }
    
    return None

def validate_and_restore_session(token):
    """Validate token and restore session if valid"""
    session_info = validate_session(token)
    if session_info:
        st.session_state.is_authenticated = True
        st.session_state.user_id = session_info['user_id']
        st.session_state.username = session_info['username']
        st.session_state.session_token = token
        
        # Get user's chats
        from modules.chat import get_user_chats, create_new_chat
        chats = get_user_chats(session_info['user_id'])
        if chats:
            st.session_state.current_chat_id = chats[0]['chat_id']
        else:
            # Create a new chat if none exists
            st.session_state.current_chat_id = create_new_chat(session_info['user_id'])
        
        # Set the page to chat if coming from login/register
        if st.session_state.page in ["login", "register"]:
            st.session_state.page = "chat"
        
        return True
    return False

def check_authentication():
    """Check if user is authenticated via URL token"""
    # Already authenticated in this session
    if st.session_state.is_authenticated:
        return True
        
    # Check URL parameters for session token
    from modules.nav import get_query_params
    query_params = get_query_params()
    token_param = query_params.get("token", [None])[0]
    
    if token_param:
        # Try to authenticate with the token
        if validate_and_restore_session(token_param):
            return True
    
    return False

def end_session(session_token):
    """End a session by removing it from the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "DELETE FROM sessions WHERE token = %s",
        (session_token,)
    )
    
    conn.commit()
    cursor.close()
    conn.close()
    
    # Clear session state
    st.session_state.session_token = None
    st.session_state.is_authenticated = False
    st.session_state.user_id = None
    st.session_state.username = None

def register_user(username, password, email):
    """Register a new user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        hashed_password = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
            (username, hashed_password, email)
        )
        
        conn.commit()
        user_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        return user_id
    except Exception as err:
        if hasattr(err, 'errno') and err.errno == 1062:  # Duplicate entry error
            return None
        raise

def authenticate_user(username, password):
    """Authenticate a user"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute(
        "SELECT * FROM users WHERE username = %s",
        (username,)
    )
    
    user = cursor.fetchone()
    
    if user and verify_password(user['password'], password):
        cursor.close()
        conn.close()
        return user
    
    cursor.close()
    conn.close()
    return None

def handle_login(username, password):
    """Handle login form submission"""
    if username and password:
        user = authenticate_user(username, password)
        if user:
            # Generate and save session token
            session_token = generate_session_token()
            save_session(user['id'], user['username'], session_token)
            
            # Get or create chat
            from modules.chat import get_user_chats, create_new_chat
            chats = get_user_chats(user['id'])
            if chats:
                st.session_state.current_chat_id = chats[0]['chat_id']
            else:
                st.session_state.current_chat_id = create_new_chat(user['id'])
            
            # Update URL with token
            set_query_params(page="chat", token=session_token)
            return True
        else:
            st.error("❌ Invalid username or password")
    else:
        st.warning("Please enter both username and password")
    return False

def handle_register(username, email, password, confirm_password):
    """Handle registration form submission"""
    if username and email and password:
        if password != confirm_password:
            st.error("❌ Passwords do not match")
        else:
            user_id = register_user(username, password, email)
            if user_id:
                # Generate and save session token
                session_token = generate_session_token()
                save_session(user_id, username, session_token)
                
                # Create first chat
                from modules.chat import create_new_chat
                st.session_state.current_chat_id = create_new_chat(user_id)
                
                # Update URL with token
                set_query_params(page="chat", token=session_token)
                return True
            else:
                st.error("❌ Username or email already exists")
    else:
        st.warning("Please fill in all fields")
    return False

def handle_logout():
    """Handle logout button click"""
    if st.session_state.session_token:
        end_session(st.session_state.session_token)
    set_query_params()  # Clear URL parameters
    st.session_state.page = "login"
    st.rerun()