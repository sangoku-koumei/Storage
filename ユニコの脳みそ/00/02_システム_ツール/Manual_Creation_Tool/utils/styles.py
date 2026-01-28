import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
    /* Global Style */
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff;
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1e2530;
        border-radius: 4px;
        padding: 5px 20px;
        color: #ffffff;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #4CAF50;
        color: white;
    }
    
    /* Button Styling */
    .stButton > button {
        background-color: #2196F3;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        border: none;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #1976D2;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1e2530;
        color: white;
        border-radius: 4px;
    }
    
    /* Custom Info Box */
    .stAlert {
        background-color: #1e2530;
        color: #e0e0e0;
        border: 1px solid #333;
    }
    </style>
    """, unsafe_allow_html=True)
