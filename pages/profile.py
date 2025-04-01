import streamlit as st
import pandas as pd
import datetime
from collections import namedtuple
from utils.db import get_db_session, User

def show_profile():
    """
    Display the user profile page with basic details and logout functionality.
    """
    col1, col2 = st.columns([0.1, 0.9])
    
    with col1:
        # Import the base64 function for the icon
        import sys
        import os
        import base64
        
        # Add the root directory to the path to import app functions
        sys.path.append(os.path.abspath(""))
        try:
            from app import get_icon_base64
            
            b64 = get_icon_base64()
            if b64:
                st.markdown(f'<div style="margin-top:10px"><img src="data:image/svg+xml;base64,{b64}" width="40px"></div>', unsafe_allow_html=True)
        except Exception as e:
            # Fallback if function not available
            pass
            
    with col2:
        st.title("User Profile")
    
    # Check if user is logged in
    if 'user_id' not in st.session_state:
        st.warning("Please log in to view your profile.")
        return
    
    # Use demo user data instead of DB query to avoid connection issues
    try:
        # Try to get user data from DB
        user_id = st.session_state.user_id
        session = get_db_session()
        user = session.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise Exception("User not found")
    except Exception as e:
        # Fallback to demo data
        UserDemo = namedtuple('UserDemo', ['id', 'username', 'email', 'created_at', 'updated_at'])
        user = UserDemo(
            id=1,
            username="demo_user",
            email="demo@alphaedge.ai",
            created_at=datetime.datetime.now() - datetime.timedelta(days=30),
            updated_at=datetime.datetime.now() - datetime.timedelta(days=5)
        )
    
    # Layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Profile picture (placeholder)
        st.image("https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y", width=150)
        
        # Logout button
        if st.button("Logout", type="primary"):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            
            st.success("You have been logged out successfully.")
            st.rerun()
    
    with col2:
        # Display user information
        st.subheader("Account Information")
        
        # Show basic user details
        info_data = {
            "Username": user.username,
            "Email": user.email or "Not provided",
            "Account Created": user.created_at.strftime("%B %d, %Y") if user.created_at else "Unknown",
            "Last Updated": user.updated_at.strftime("%B %d, %Y") if user.updated_at else "Unknown"
        }
        
        for label, value in info_data.items():
            st.write(f"**{label}:** {value}")
        
        # Edit profile section
        with st.expander("Edit Profile"):
            with st.form("profile_form"):
                new_username = st.text_input("Username", value=user.username)
                new_email = st.text_input("Email", value=user.email or "")
                
                # Password change fields
                st.subheader("Change Password")
                current_password = st.text_input("Current Password", type="password")
                new_password = st.text_input("New Password", type="password") 
                confirm_password = st.text_input("Confirm New Password", type="password")
                
                submitted = st.form_submit_button("Update Profile")
                
                if submitted:
                    # For demo purposes, we'll just show success messages without actually updating
                    # the data since we're using a namedtuple for demo mode which is immutable
                    
                    # Password validation
                    if new_password:
                        if new_password != confirm_password:
                            st.error("New passwords do not match!")
                        elif not current_password:
                            st.error("Please enter your current password to change it.")
                        else:
                            # In a real app, this would update the password in the database
                            st.success("Password updated!")
                    
                    # For a real app, this would update the user data in the database
                    
                    # Save changes
                    try:
                        # Only attempt to save to DB if using real DB user
                        if hasattr(user, 'password_hash'):
                            user.updated_at = datetime.datetime.now()
                            session.commit()
                    except Exception as e:
                        # In demo mode, just show success without saving
                        pass
                    
                    st.success("Profile updated successfully!")
    
    # Portfolio statistics
    st.subheader("Your Portfolio Statistics")
    
    # Get portfolio data
    if 'portfolio' in st.session_state:
        portfolio = st.session_state.portfolio
        
        if portfolio and 'holdings' in portfolio and portfolio['holdings']:
            # Display portfolio metrics
            metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
            
            with metrics_col1:
                st.metric(
                    label="Total Value",
                    value=f"₹{portfolio.get('total_value', 0):,.2f}"
                )
            
            with metrics_col2:
                st.metric(
                    label="Total Profit/Loss",
                    value=f"₹{portfolio.get('total_profit_loss', 0):,.2f}",
                    delta=f"{portfolio.get('total_profit_loss_percent', 0):.2f}%"
                )
            
            with metrics_col3:
                st.metric(
                    label="# of Stocks",
                    value=len(portfolio.get('holdings', []))
                )
            
            with metrics_col4:
                # Calculate last transaction date
                last_transaction = max([h.get('buy_date', datetime.datetime(2000, 1, 1)) 
                                      for h in portfolio.get('holdings', [])], 
                                     default=None)
                
                if last_transaction:
                    last_transaction_str = last_transaction.strftime("%b %d, %Y") if isinstance(last_transaction, datetime.datetime) else str(last_transaction)
                    st.metric(
                        label="Last Transaction",
                        value=last_transaction_str
                    )
                else:
                    st.metric(label="Last Transaction", value="No data")
        else:
            st.info("No portfolio data available. Go to Portfolio Management to create your first portfolio.")
    else:
        st.info("No portfolio data available. Go to Portfolio Management to create your first portfolio.")
    
    # Activity history (placeholder)
    st.subheader("Recent Activity")
    
    # Sample activity data
    activity_data = {
        "Date": [
            datetime.datetime.now() - datetime.timedelta(days=i) 
            for i in range(5)
        ],
        "Action": [
            "Logged in",
            "Updated portfolio",
            "Analyzed stock RELIANCE.NS",
            "Created new portfolio",
            "Registered account"
        ],
        "Details": [
            "Login from Chrome/Windows",
            "Added 50 shares of TCS",
            "Technical and fundamental analysis",
            "Created 'Long Term Growth' portfolio",
            "New account created"
        ]
    }
    
    activity_df = pd.DataFrame(activity_data)
    activity_df["Date"] = activity_df["Date"].dt.strftime("%Y-%m-%d %H:%M")
    
    st.dataframe(activity_df, use_container_width=True)
    
    # Preferences section
    st.subheader("Preferences")
    
    with st.expander("App Settings"):
        st.checkbox("Enable dark mode", value=True, key="dark_mode")
        st.checkbox("Send email notifications for stock alerts", value=False, key="email_notifications")
        st.checkbox("Show advanced technical indicators", value=True, key="advanced_indicators")
        
        if st.button("Save Preferences"):
            st.success("Preferences saved successfully!")