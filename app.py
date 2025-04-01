import streamlit as st
import pandas as pd
import datetime
import yfinance as yf
import os
import base64
from utils.stock_data import get_stock_data
from utils.portfolio import get_portfolio_data
from utils.db import get_portfolio_data_from_db, init_db, init_demo_data

# Set page configuration (must be the first Streamlit command)
st.set_page_config(
    page_title="AlphaEdge.ai - Smart Stock Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply custom CSS for light purple and aqua green theme
st.markdown("""
<style>
    /* Primary color: Light Purple */
    .stButton button {
        background-color: #8a6bdf;
        color: white;
    }
    .stButton button:hover {
        background-color: #7558d3;
    }
    /* Secondary color: Aqua Green */
    .stProgress > div > div {
        background-color: #4acfd9;
    }
    /* Text highlighting */
    .highlight {
        color: #4acfd9;
        font-weight: bold;
    }
    /* Custom sidebar styling */
    .sidebar .sidebar-content {
        background-image: linear-gradient(#8a6bdf, #4acfd9);
    }
    /* Section headers */
    h1, h2, h3 {
        color: #8a6bdf;
    }
</style>
""", unsafe_allow_html=True)

# Function to display logo
def display_logo():
    try:
        with open("static/logo.svg", "r") as f:
            svg_content = f.read()
        b64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
        st.sidebar.markdown(f"""
            <div style="text-align: center; margin-bottom: 20px; max-width: 100%;">
                <img src="data:image/svg+xml;base64,{b64}" style="max-width: 100%;">
            </div>
        """, unsafe_allow_html=True)
    except FileNotFoundError:
        st.sidebar.warning("Logo file not found.")
    except Exception as e:
        st.sidebar.error(f"Error displaying logo: {e}")

# Initialize session state variables
if 'db_initialized' not in st.session_state:
    st.session_state.db_initialized = False
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# Initialize database if running for the first time
if not st.session_state.db_initialized:
    try:
        init_db()
        init_demo_data()
        st.session_state.db_initialized = True
    except Exception as e:
        st.error(f"Database initialization error: {e}")

# Display logo in sidebar
display_logo()

# Sidebar navigation
st.sidebar.title("AlphaEdge.ai")
if st.session_state.authenticated:
    page = st.sidebar.radio(
        "Navigation",
        ["Portfolio Dashboard", "Portfolio Management", "Stock Analysis", "Recommendations", "Profile", "Help & Support"]
    )
else:
    page = st.sidebar.radio(
        "Navigation",
        ["Login"]
    )

# Handle navigation
if page == "Login":
    st.title("Login to AlphaEdge.ai")
    username = st.text_input("Username", value="demo_user")
    password = st.text_input("Password", type="password", value="password")
    if st.button("Login"):
        st.session_state.authenticated = True
        st.experimental_rerun()
elif page == "Portfolio Dashboard":
    st.write("Portfolio Dashboard")
# Add other page handlers here...
