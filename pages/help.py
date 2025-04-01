import streamlit as st
import pandas as pd

def show_help():
    """
    Display the help and documentation page with support options.
    """
    st.title("Help & Support")

    # Create tabs for different help sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Getting Started", "Features Guide", "Data Sources", "FAQs", "Contact Support"])

    with tab1:
        st.header("Welcome to AlphaEdge.ai")
        st.write("""
        AlphaEdge.ai is a comprehensive stock analysis and portfolio management platform designed to help 
        investors make informed decisions based on technical, fundamental, and behavioral analysis.

        ## Quick Start

        1. **Stock Analysis**: Search for any stock and get detailed technical, fundamental, and behavioral analysis
        2. **Portfolio Management**: Create and manage your investment portfolios
        3. **Recommendations**: Get personalized recommendations based on your portfolio and investment goals
        4. **Dashboard**: View your overall portfolio performance and key metrics
        """)

        st.subheader("Platform Navigation")
        platform_guide = {
            "Page": ["Stock Analysis", "Portfolio Management", "Portfolio Dashboard", "Recommendations", "Profile", "Help & Support"],
            "Description": [
                "Search and analyze any stock with comprehensive technical, fundamental, and behavioral indicators",
                "Create, edit, and manage your investment portfolios",
                "View your portfolio performance, sector allocation, and key metrics",
                "Get personalized stock recommendations based on your investment goals",
                "Manage your account settings and preferences",
                "Access documentation, FAQs, and support options"
            ]
        }
        st.table(pd.DataFrame(platform_guide))

    with tab2:
        st.header("Features Guide")

        st.subheader("Stock Analysis")
        st.write("""
        The Stock Analysis page provides comprehensive analysis across multiple dimensions:

        1. **Overview**: General stock information and key metrics
        2. **Technical Analysis**: Price movements, trends, and technical indicators
        3. **Fundamental Analysis**: Financial health, valuation metrics, and business fundamentals
        4. **Behavioral Analysis**: Market sentiment, news impact, and social media trends
        5. **Price Charts**: Interactive price charts with various technical indicators
        """)

        st.subheader("Technical Indicators")
        tech_indicators = {
            "Indicator": ["Moving Averages", "RSI", "MACD", "Bollinger Bands", "ADX"],
            "Description": [
                "Track price trends using 20, 50, and 200-day moving averages",
                "Relative Strength Index measures momentum and overbought/oversold conditions",
                "Moving Average Convergence Divergence shows trend direction and momentum",
                "Volatility bands around the price showing potential support/resistance levels",
                "Average Directional Index measures trend strength"
            ]
        }
        st.table(pd.DataFrame(tech_indicators))

        st.subheader("Investment Time Horizons")
        st.write("""
        AlphaEdge.ai provides recommendations based on different investment time horizons:

        - **Short-term**: 0-3 months trading opportunities
        - **Medium-term**: 3-12 months investment perspective
        - **Long-term**: 1+ year strategic investments

        Each horizon uses different weights for technical, fundamental, and behavioral factors.
        """)

    with tab3:
        st.header("Data Sources & Methodology")

        st.subheader("Data Sources")
        st.write("""
        AlphaEdge.ai uses the following data sources to provide comprehensive stock analysis:
        """)

        data_sources = {
            "Data Type": ["Stock Price Data", "Historical Market Data", "Fundamental Data", "Financial Statements", "News & Social Media", "Analyst Estimates"],
            "Source": ["Yahoo Finance API", "NSE/BSE Official APIs", "Company Filings", "Quarterly/Annual Reports", "News APIs & Social Listening", "Analyst Consensus Data"],
            "Update Frequency": ["Real-time/15-min delayed", "End of day", "Quarterly", "Quarterly/Annual", "Near real-time", "As released"]
        }
        st.table(pd.DataFrame(data_sources))

    with tab4:
        st.header("Frequently Asked Questions")

        with st.expander("How accurate are the stock recommendations?"):
            st.write("""
            AlphaEdge.ai uses a combination of technical, fundamental, and behavioral analysis to generate 
            recommendations. The accuracy varies based on market conditions and other factors. Our 
            recommendations should be used as one input for your investment decisions, not as the sole determining factor.
            """)

        with st.expander("How often is stock data updated?"):
            st.write("""
            Technical price data is updated daily after market close. Fundamental data is updated 
            quarterly when companies release their financial reports. News and behavioral data 
            are updated in near real-time throughout the trading day.
            """)

        with st.expander("Can I import my existing portfolio?"):
            st.write("""
            Yes! You can import your existing portfolio from major brokers and platforms. Go to 
            Portfolio Management → Import Portfolio, then select your broker from the dropdown menu 
            and follow the prompts to connect securely.
            """)

    with tab5:
        st.header("Contact Support")

        st.write("""
        For assistance, you can reach our support team through:

        - Email: support@alphaedge.ai
        - Business Hours: Monday-Friday, 9am-6pm ET
        """)

        feedback = st.text_area("Share your feedback or feature requests:", height=150)
        email = st.text_input("Your email (optional):")

        if st.button("Submit Feedback"):
            if feedback:
                st.success("Thank you for your feedback! Our team will review it.")
            else:
                st.error("Please enter your feedback before submitting.")

def show_help_page():
    """
    Main function to display the help page.
    """
    show_help()

if __name__ == "__main__":
    show_help_page()