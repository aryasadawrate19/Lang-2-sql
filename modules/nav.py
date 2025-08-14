# mod/nav.py - Navigation and routing functions

import streamlit as st

def get_query_params():
    """Get query parameters from URL"""
    return dict(st.query_params)

def set_query_params(**kwargs):
    """Set query parameters in URL"""
    for key, value in kwargs.items():
        if value is None:
            if key in st.query_params:
                del st.query_params[key]
        else:
            st.query_params[key] = value

def navigate_to(page):
    """Navigate to a new page with token preservation"""
    st.session_state.page = page
    
    # If authenticated, include token in URL
    if st.session_state.is_authenticated and st.session_state.session_token:
        set_query_params(page=page, token=st.session_state.session_token)
    else:
        set_query_params(page=page)
    
    st.rerun()