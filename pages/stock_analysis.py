import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.analysis import perform_complete_analysis
from utils.stock_data import search_stocks, get_stock_list

def show_stock_analysis(portfolio):
    """
    Display the stock analysis page.
    
    Args:
        portfolio (dict): Portfolio data
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
        st.title("Stock Analysis")
    
    # Initialize session state for stock search
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""
    if 'filtered_stocks' not in st.session_state:
        st.session_state.filtered_stocks = []
    
    # Create tabs for different search methods
    search_tab, portfolio_tab, external_tab = st.tabs(["Search Stocks", "Portfolio Stocks", "Connect External"])
    
    with search_tab:
        # Create a cleaner search interface
        st.markdown("### Find stocks to analyze")
        
        # Create a container for the search box
        search_container = st.container()
        
        with search_container:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Dynamic search with callback on change
                search_query = st.text_input(
                    "Search by company name or ticker symbol",
                    key="stock_search",
                    value=st.session_state.search_query,
                    help="Type at least 2 characters to see suggestions",
                    placeholder="e.g. Reliance, TCS, HDFC, etc."
                )
            
            with col2:
                # Add option to filter by exchange
                exchange_filter = st.selectbox(
                    "Exchange",
                    options=["All", "NSE", "BSE"],
                    index=0
                )
        
        # Update session state for search query
        st.session_state.search_query = search_query
        
        # Get filtered stocks based on search query
        if len(search_query) >= 2:
            filtered_stocks = search_stocks(search_query)
            
            # Apply exchange filter if selected
            if exchange_filter != "All":
                filtered_stocks = [s for s in filtered_stocks if s["exchange"] == exchange_filter]
                
            st.session_state.filtered_stocks = filtered_stocks
        
        # Display search results in a more structured table format
        if st.session_state.filtered_stocks:
            st.write(f"**Found {len(st.session_state.filtered_stocks)} matching stocks**")
            
            # Create a dataframe for better display
            display_data = []
            for stock in st.session_state.filtered_stocks:
                display_data.append({
                    "Name": stock["name"],
                    "Ticker": stock["ticker"],
                    "Exchange": stock["exchange"],
                    "Select": stock["ticker"]  # We'll use this for selection
                })
            
            # Convert to dataframe
            df = pd.DataFrame(display_data)
            
            # Use an AgGrid or custom table for better interaction
            selection = None
            
            # Display stocks in a clean table with select buttons
            for i, row in df.iterrows():
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.write(f"**{row['Name']}**")
                with col2:
                    st.write(f"{row['Ticker']} ({row['Exchange']})")
                with col3:
                    if st.button("Select", key=f"select_{row['Ticker']}"):
                        selection = row['Ticker']
                st.markdown("---")
            
            # Handle selection
            if selection:
                st.session_state.selected_ticker = selection
                st.success(f"Selected stock: {selection}")
        
        elif search_query and len(search_query) >= 2:
            st.warning("No matching stocks found. Try another search term.")
            
            # Manual ticker entry
            st.markdown("### Manual Entry")
            col1, col2 = st.columns([3, 1])
            
            with col1:
                manual_ticker = st.text_input(
                    "Enter ticker manually",
                    placeholder="e.g. RELIANCE.NS, INFY.BO",
                    help="For Indian stocks, add .NS for NSE or .BO for BSE"
                )
            
            with col2:
                if st.button("Use Ticker", key="use_manual_ticker"):
                    if manual_ticker:
                        st.session_state.selected_ticker = manual_ticker
                        st.success(f"Using ticker: {manual_ticker}")
        
        # Show popular stocks for quick selection
        st.markdown("### Popular Stocks")
        popular_stocks = [
            {"name": "Reliance Industries", "ticker": "RELIANCE.NS"},
            {"name": "Tata Consultancy Services", "ticker": "TCS.NS"},
            {"name": "HDFC Bank", "ticker": "HDFCBANK.NS"},
            {"name": "Infosys", "ticker": "INFY.NS"},
            {"name": "ICICI Bank", "ticker": "ICICIBANK.NS"}
        ]
        
        col1, col2, col3, col4, col5 = st.columns(5)
        cols = [col1, col2, col3, col4, col5]
        
        for i, stock in enumerate(popular_stocks):
            with cols[i % 5]:
                if st.button(stock["name"], key=f"popular_{stock['ticker']}"):
                    st.session_state.selected_ticker = stock["ticker"]
                    st.success(f"Selected stock: {stock['ticker']}")
    
    with portfolio_tab:
        # Display portfolio stocks for selection
        if portfolio and 'holdings' in portfolio and portfolio['holdings']:
            st.markdown("### Your Portfolio Stocks")
            
            # Create a table of portfolio stocks
            for holding in portfolio['holdings']:
                if 'ticker' in holding:
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.write(f"**{holding.get('name', holding['ticker'])}**")
                    with col2:
                        st.write(f"{holding.get('quantity', 0)} shares")
                    with col3:
                        if st.button("Select", key=f"portfolio_{holding['ticker']}"):
                            st.session_state.selected_ticker = holding['ticker']
                            st.success(f"Selected: {holding['ticker']}")
                    st.markdown("---")
        else:
            st.info("No stocks in your portfolio. Add stocks in the Portfolio Management section.")
    
    with external_tab:
        # External portfolio integration
        st.markdown("### Connect External Portfolio")
        
        # Create tabs for different trading platforms
        kite_tab, groww_tab, upstox_tab = st.tabs(["Zerodha Kite", "Groww", "Upstox"])
        
        with kite_tab:
            st.markdown("#### Connect your Zerodha Kite account")
            st.markdown("""
            Connecting to Kite allows you to:
            - Import your existing portfolio
            - Sync trades automatically
            - Get real-time portfolio updates
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                kite_api_key = st.text_input("Kite API Key", type="password", 
                                             help="Get this from your Kite developer account")
            
            with col2:
                kite_api_secret = st.text_input("Kite API Secret", type="password")
            
            if st.button("Connect Kite Account", key="connect_kite"):
                if kite_api_key and kite_api_secret:
                    # This would actually implement the Kite API integration
                    st.success("Kite integration will be implemented in the next version.")
                    # In a real implementation, we would:
                    # 1. Store the API credentials securely
                    # 2. Authenticate with Kite API
                    # 3. Fetch portfolio data
                    # 4. Display a success message with the fetched data
                else:
                    st.error("Please enter both API Key and Secret")
        
        with groww_tab:
            st.markdown("#### Connect your Groww account")
            st.markdown("""
            Connecting to Groww allows you to:
            - Import your existing portfolio
            - Track performance across platforms
            - Get consolidated analysis
            """)
            
            st.info("Groww API integration will be available in the next update. Stay tuned!")
        
        with upstox_tab:
            st.markdown("#### Connect your Upstox account")
            st.markdown("""
            Connecting to Upstox allows you to:
            - Import your existing portfolio
            - Sync trades automatically
            - Get real-time portfolio updates
            """)
            
            st.info("Upstox API integration will be available in the next update. Stay tuned!")
    
    # Display the selected ticker and analysis button
    if 'selected_ticker' in st.session_state and st.session_state.selected_ticker:
        st.markdown("---")
        ticker = st.session_state.selected_ticker
        
        # Show selected stock info
        st.markdown(f"## Analysis for: {ticker}")
        
        if st.button("Run Complete Analysis", type="primary", key="run_analysis_button"):
            with st.spinner(f"Analyzing {ticker}... This may take a moment"):
                run_analysis(ticker)
    else:
        st.markdown("---")
        st.info("Select a stock to analyze from the options above.")
        
        # Show information about market indices and stocks
        st.markdown("""
        ### Major Indices for Reference
        - **NSE Nifty 50**: ^NSEI
        - **BSE Sensex**: ^BSESN
        - **Dow Jones**: ^DJI
        - **S&P 500**: ^GSPC
        - **Nasdaq**: ^IXIC
        
        ### Popular International Stocks
        - Apple Inc: AAPL
        - Microsoft: MSFT
        - Amazon: AMZN
        - Google: GOOGL
        - Tesla: TSLA
        
        **Indian Stocks (NSE):**
        - RELIANCE - Reliance Industries
        - TCS - Tata Consultancy Services
        - INFY - Infosys
        - HDFCBANK - HDFC Bank
        - TATAMOTORS - Tata Motors
        - SUNPHARMA - Sun Pharmaceutical
        - BAJFINANCE - Bajaj Finance
        - WIPRO - Wipro
        - ADANIPORTS - Adani Ports
        - AXISBANK - Axis Bank
        
        **US Stocks:**
        - AAPL - Apple Inc
        - MSFT - Microsoft
        - GOOGL - Alphabet (Google)
        - AMZN - Amazon
        - META - Meta Platforms (Facebook)
        """)


def run_analysis(ticker):
    """
    Run analysis for a specific ticker and display results.
    
    Args:
        ticker (str): Stock ticker symbol
    """
    # Run the analysis
    results = perform_complete_analysis(ticker)
    
    if results.get('status') == 'error':
        st.error(f"Error analyzing {ticker}: {results.get('error', 'Unknown error')}")
        return
    
    # Display the results
    display_analysis_results(results)


def display_analysis_results(results):
    """
    Display the analysis results in a structured format.
    
    Args:
        results (dict): Analysis results
    """
    ticker = results.get('ticker', 'Unknown')
    name = results.get('name', ticker)
    sector = results.get('sector', 'Unknown')
    current_price = results.get('current_price')
    
    # Header with stock info
    st.header(f"{name} ({ticker})")
    st.subheader(f"Sector: {sector} | Current Price: ₹{current_price:.2f}" if current_price else f"Sector: {sector}")
    
    # Create tabs for different types of analysis
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Summary", "Technical Analysis", "Fundamental Analysis", "Behavioral Analysis", "Price Chart"])
    
    # Tab 1: Summary
    with tab1:
        # Overall scores and recommendation
        tech_score = results.get('technical', {}).get('tech_score', 0)
        fund_score = results.get('fundamental', {}).get('fund_score', 0)
        
        st.subheader("Analysis Summary")
        
        # Create three columns for the scores
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Technical Score",
                value=f"{tech_score:.1f}/10",
                delta=results.get('technical', {}).get('overall_technical', 'N/A')
            )
        
        with col2:
            st.metric(
                label="Fundamental Score",
                value=f"{fund_score:.1f}/10",
                delta=results.get('fundamental', {}).get('overall_fundamental', 'N/A')
            )
        
        with col3:
            combined_score = (tech_score * 0.6) + (fund_score * 0.4)
            recommendation = "Strong Buy" if combined_score >= 7 else "Buy" if combined_score >= 3 else "Hold" if combined_score >= -3 else "Sell" if combined_score >= -7 else "Strong Sell"
            
            st.metric(
                label="Combined Score",
                value=f"{combined_score:.1f}/10",
                delta=recommendation
            )
        
        # Key insights
        st.subheader("Key Insights")
        
        # Technical insights
        tech_analysis = results.get('technical', {})
        
        tech_insights = []
        
        # Trend
        if 'trend' in tech_analysis:
            tech_insights.append(f"- Stock is in a **{tech_analysis.get('trend')}**")
        
        # Moving averages
        price = tech_analysis.get('price', 0)
        sma_50 = tech_analysis.get('sma_50', 0)
        sma_200 = tech_analysis.get('sma_200', 0)
        
        if price and sma_50 and sma_200:
            if price > sma_50 > sma_200:
                tech_insights.append("- Price is above both 50-day and 200-day moving averages (bullish)")
            elif price < sma_50 < sma_200:
                tech_insights.append("- Price is below both 50-day and 200-day moving averages (bearish)")
            elif sma_50 > sma_200:
                tech_insights.append("- 50-day moving average is above 200-day moving average (bullish)")
            else:
                tech_insights.append("- 50-day moving average is below 200-day moving average (bearish)")
        
        # RSI
        rsi = tech_analysis.get('rsi')
        if rsi is not None:
            if rsi > 70:
                tech_insights.append(f"- RSI at **{rsi:.1f}** suggests stock is **overbought**")
            elif rsi < 30:
                tech_insights.append(f"- RSI at **{rsi:.1f}** suggests stock is **oversold**")
            else:
                tech_insights.append(f"- RSI at **{rsi:.1f}** is neutral")
        
        # MACD
        macd_crossover = tech_analysis.get('macd_crossover')
        if macd_crossover:
            tech_insights.append(f"- Recent **{macd_crossover} MACD crossover** detected")
        
        # Golden/Death cross
        if tech_analysis.get('golden_cross'):
            tech_insights.append("- Recent **Golden Cross** (bullish signal)")
        if tech_analysis.get('death_cross'):
            tech_insights.append("- Recent **Death Cross** (bearish signal)")
        
        # Display technical insights
        if tech_insights:
            st.write("**Technical Insights:**")
            for insight in tech_insights:
                st.write(insight)
        
        # Fundamental insights
        fund_analysis = results.get('fundamental', {}).get('analysis', {})
        
        fund_insights = []
        
        # Valuation
        valuation = fund_analysis.get('valuation', {})
        for metric, details in valuation.items():
            if 'analysis' in details and metric != 'market_cap':
                fund_insights.append(f"- {metric.replace('_', ' ').title()}: **{details.get('analysis')}**")
        
        # Financial health
        financial_health = fund_analysis.get('financial_health', {})
        for metric, details in financial_health.items():
            if 'analysis' in details:
                fund_insights.append(f"- {metric.replace('_', ' ').title()}: **{details.get('analysis')}**")
        
        # Display fundamental insights
        if fund_insights:
            st.write("**Fundamental Insights:**")
            for insight in fund_insights:
                st.write(insight)
    
    # Tab 2: Technical Analysis
    with tab2:
        tech_analysis = results.get('technical', {})
        
        st.subheader("Technical Indicators")
        
        # Create columns for various indicators
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Moving Averages**")
            ma_data = {
                'Indicator': ['Price', 'SMA (20)', 'SMA (50)', 'SMA (200)'],
                'Value': [
                    f"₹{tech_analysis.get('price', 0):.2f}",
                    f"₹{tech_analysis.get('sma_20', 0):.2f}",
                    f"₹{tech_analysis.get('sma_50', 0):.2f}",
                    f"₹{tech_analysis.get('sma_200', 0):.2f}"
                ]
            }
            # Convert all values to strings to avoid PyArrow errors
            df_ma = pd.DataFrame(ma_data)
            df_ma['Value'] = df_ma['Value'].astype(str)
            st.table(df_ma)
            
            st.write("**Momentum Indicators**")
            momentum_data = {
                'Indicator': ['RSI (14)', 'RSI Signal', 'MACD', 'MACD Signal', 'MACD Histogram'],
                'Value': [
                    f"{tech_analysis.get('rsi', 0):.2f}",
                    tech_analysis.get('rsi_signal', 'N/A'),
                    f"{tech_analysis.get('macd', 0):.2f}",
                    f"{tech_analysis.get('macd_signal', 0):.2f}",
                    f"{tech_analysis.get('macd_hist', 0):.2f}"
                ]
            }
            # Convert all values to strings to avoid PyArrow errors
            df_momentum = pd.DataFrame(momentum_data)
            df_momentum['Value'] = df_momentum['Value'].astype(str)
            st.table(df_momentum)
        
        with col2:
            st.write("**Trend Indicators**")
            trend_data = {
                'Indicator': ['Trend', 'ADX', 'ADX Signal', '+DI', '-DI'],
                'Value': [
                    tech_analysis.get('trend', 'N/A'),
                    f"{tech_analysis.get('adx', 0):.2f}",
                    tech_analysis.get('adx_signal', 'N/A'),
                    f"{tech_analysis.get('pdi', 0):.2f}",
                    f"{tech_analysis.get('ndi', 0):.2f}"
                ]
            }
            # Convert all values to strings to avoid PyArrow errors
            df_trend = pd.DataFrame(trend_data)
            df_trend['Value'] = df_trend['Value'].astype(str)
            st.table(df_trend)
            
            st.write("**Volatility & Volume**")
            vol_data = {
                'Indicator': ['Bollinger Upper', 'Bollinger Lower', 'BB Signal', 'Volume Signal', 'OBV Signal'],
                'Value': [
                    f"₹{tech_analysis.get('bollinger_high', 0):.2f}",
                    f"₹{tech_analysis.get('bollinger_low', 0):.2f}",
                    tech_analysis.get('bollinger_signal', 'N/A'),
                    tech_analysis.get('volume_signal', 'N/A'),
                    tech_analysis.get('obv_signal', 'N/A')
                ]
            }
            # Convert all values to strings to avoid PyArrow errors
            df_vol = pd.DataFrame(vol_data)
            df_vol['Value'] = df_vol['Value'].astype(str)
            st.table(df_vol)
        
        # Special signals
        st.write("**Technical Signals & Events**")
        signals = []
        
        if tech_analysis.get('golden_cross'):
            signals.append("🟢 Golden Cross: Recent crossing of 50-day MA above 200-day MA (bullish)")
        if tech_analysis.get('death_cross'):
            signals.append("🔴 Death Cross: Recent crossing of 50-day MA below 200-day MA (bearish)")
        if tech_analysis.get('rsi_divergence') == 'Bullish':
            signals.append("🟢 Bullish RSI Divergence: Price making lower lows while RSI making higher lows")
        if tech_analysis.get('rsi_divergence') == 'Bearish':
            signals.append("🔴 Bearish RSI Divergence: Price making higher highs while RSI making lower highs")
        if tech_analysis.get('macd_crossover') == 'Bullish':
            signals.append("🟢 Bullish MACD Crossover: MACD line crossed above signal line")
        if tech_analysis.get('macd_crossover') == 'Bearish':
            signals.append("🔴 Bearish MACD Crossover: MACD line crossed below signal line")
        
        if not signals:
            signals.append("No significant technical signals detected")
        
        for signal in signals:
            st.write(signal)
        
        # Technical score explanation
        st.write(f"**Technical Score: {tech_analysis.get('tech_score', 0):.1f}/10**")
        st.write(f"Overall Technical Analysis: **{tech_analysis.get('overall_technical', 'N/A')}**")
    
    # Tab 3: Fundamental Analysis
    with tab3:
        fund_analysis = results.get('fundamental', {}).get('analysis', {})
        
        st.subheader("Fundamental Analysis")
        
        # Create columns for different types of fundamentals
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Valuation Metrics**")
            
            valuation = fund_analysis.get('valuation', {})
            if valuation:
                val_data = {'Metric': [], 'Value': [], 'Industry Avg': [], 'Analysis': []}
                
                for metric, details in valuation.items():
                    if metric == 'market_cap':
                        val_data['Metric'].append('Market Cap')
                        val_data['Value'].append(f"₹{details.get('value', 0) / 10000000000:.2f}B")
                        val_data['Industry Avg'].append('N/A')
                        val_data['Analysis'].append(details.get('category', 'N/A'))
                    else:
                        val_data['Metric'].append(metric.replace('_', ' ').title())
                        val_data['Value'].append(f"{details.get('value', 0):.2f}")
                        val_data['Industry Avg'].append(f"{details.get('industry_avg', 'N/A')}")
                        val_data['Analysis'].append(details.get('analysis', 'N/A'))
                
                # Convert all values to strings to avoid PyArrow errors
                df_val = pd.DataFrame(val_data)
                for col in df_val.columns:
                    df_val[col] = df_val[col].astype(str)
                st.table(df_val)
            else:
                st.info("No valuation data available")
        
        with col2:
            st.write("**Financial Health**")
            
            financial_health = fund_analysis.get('financial_health', {})
            if financial_health:
                fin_data = {'Metric': [], 'Value': [], 'Industry Avg': [], 'Analysis': []}
                
                for metric, details in financial_health.items():
                    fin_data['Metric'].append(metric.replace('_', ' ').title())
                    fin_data['Value'].append(f"{details.get('value', 0):.2f}" if isinstance(details.get('value'), (int, float)) else details.get('value', 'N/A'))
                    fin_data['Industry Avg'].append(f"{details.get('industry_avg', 'N/A')}")
                    fin_data['Analysis'].append(details.get('analysis', 'N/A'))
                
                # Convert all values to strings to avoid PyArrow errors
                df_fin = pd.DataFrame(fin_data)
                for col in df_fin.columns:
                    df_fin[col] = df_fin[col].astype(str)
                st.table(df_fin)
            else:
                st.info("No financial health data available")
        
        # Dividend info
        dividend = fund_analysis.get('dividend', {})
        if dividend:
            st.write("**Dividend Information**")
            div_data = {'Metric': [], 'Value': [], 'Industry Avg': [], 'Analysis': []}
            
            for metric, details in dividend.items():
                div_data['Metric'].append(metric.replace('_', ' ').title())
                div_data['Value'].append(f"{details.get('value', 0):.2f}%")
                div_data['Industry Avg'].append(f"{details.get('industry_avg', 'N/A')}%")
                div_data['Analysis'].append(details.get('analysis', 'N/A'))
            
            # Convert all values to strings to avoid PyArrow errors
            df_div = pd.DataFrame(div_data)
            for col in df_div.columns:
                df_div[col] = df_div[col].astype(str)
            st.table(df_div)
        
        # Fundamental score explanation
        fund_score = results.get('fundamental', {}).get('fund_score', 0)
        overall_fund = results.get('fundamental', {}).get('overall_fundamental', 'N/A')
        
        st.write(f"**Fundamental Score: {fund_score:.1f}/10**")
        st.write(f"Overall Fundamental Analysis: **{overall_fund}**")
    
    # Tab 4: Behavioral Analysis
    with tab4:
        behavioral = results.get('behavioral', {})
        
        if not behavioral:
            st.info("No behavioral data available for this stock.")
            return
            
        st.subheader("Behavioral & Sentiment Analysis")
        
        # Main score
        behavioral_score = behavioral.get('behavioral_score', 5.0)
        sentiment_signal = behavioral.get('sentiment_signal', 'Neutral')
        
        # Score display with color coding
        score_color = "#1b9e77" if behavioral_score >= 7.5 else "#7fc97f" if behavioral_score >= 6.0 else \
                     "#ffff99" if behavioral_score >= 4.0 else "#fdb462" if behavioral_score >= 2.5 else "#e41a1c"
                     
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 20px;">
            <div style="background-color: {score_color}; color: {'black' if 4.0 <= behavioral_score < 7.5 else 'white'}; 
                     width: 120px; height: 120px; border-radius: 60px; display: flex; 
                     justify-content: center; align-items: center; font-size: 36px; font-weight: bold; margin-right: 20px;">
                {behavioral_score:.1f}
            </div>
            <div>
                <h3 style="margin-bottom: 5px;">Behavioral Score: {behavioral_score:.1f}/10</h3>
                <h4>Market Sentiment: <span style="color: {score_color}">{sentiment_signal}</span></h4>
                <p>Based on news sentiment, market fear/greed, and social media analysis</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Key components in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            news_sentiment = behavioral.get('news_sentiment', 0)
            sentiment_label = "Positive" if news_sentiment > 0.3 else "Negative" if news_sentiment < -0.3 else "Neutral"
            sentiment_color = "green" if news_sentiment > 0.3 else "red" if news_sentiment < -0.3 else "orange"
            
            st.metric(
                label="News Sentiment",
                value=sentiment_label,
                delta=f"{news_sentiment:.2f}"
            )
            st.caption(f"Based on {behavioral.get('news_count', 0)} news articles")
        
        with col2:
            fear_index = behavioral.get('market_fear_index', 50)
            fear_label = "Extreme Fear" if fear_index < 25 else "Fear" if fear_index < 40 else \
                        "Neutral" if fear_index < 60 else "Greed" if fear_index < 75 else "Extreme Greed"
            
            # Display fear/greed index with better formatting to prevent text truncation
            st.metric(
                label="Market Fear/Greed",
                value=f"{fear_index}/100",
                delta=fear_label
            )
        
        with col3:
            insider = behavioral.get('insider_trading', 'Neutral')
            insider_delta = 1 if insider == "Buying" else -1 if insider == "Selling" else 0
            
            st.metric(
                label="Insider Activity",
                value=insider,
                delta=insider_delta,
                delta_color="normal"
            )
        
        # Recent news
        st.subheader("Recent News Headlines")
        
        headlines = behavioral.get('headlines', [])
        if headlines:
            for headline in headlines:
                sentiment = headline.get('sentiment', 'neutral')
                color = "green" if sentiment == "positive" else "red" if sentiment == "negative" else "gray"
                
                st.markdown(f"""
                <div style="padding: 10px; margin-bottom: 10px; border-left: 4px solid {color};">
                    <div style="font-weight: bold;">{headline.get('headline')}</div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.8em; color: #666;">
                        <span>{headline.get('source')}</span>
                        <span>{headline.get('date')}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent news headlines available")
        
        # Social media analysis
        st.subheader("Social Media Analysis")
        
        social = behavioral.get('social_media', {})
        social_buzz = social.get('buzz', 0)
        social_sentiment = social.get('sentiment', 0)
        
        # Create a horizontal bar for social buzz
        st.markdown(f"""
        <div style="margin: 20px 0;">
            <div style="margin-bottom: 5px;">Social Media Buzz</div>
            <div style="width: 100%; background-color: #e0e0e0; height: 20px; border-radius: 10px;">
                <div style="width: {social_buzz}%; background-color: #3366cc; height: 20px; border-radius: 10px;">
                </div>
            </div>
            <div style="text-align: right;">{social_buzz}/100</div>
        </div>
        
        <div style="margin: 20px 0;">
            <div style="margin-bottom: 5px;">Social Sentiment</div>
            <div style="width: 100%; display: flex; align-items: center;">
                <div style="width: 33.33%; text-align: left; color: #e41a1c;">Negative</div>
                <div style="width: 33.33%; text-align: center; color: #777777;">Neutral</div>
                <div style="width: 33.33%; text-align: right; color: #1b9e77;">Positive</div>
            </div>
            <div style="width: 100%; background-color: #e0e0e0; height: 20px; border-radius: 10px; position: relative;">
                <div style="position: absolute; left: calc(50% + {social_sentiment * 50}%); 
                         transform: translateX(-50%); width: 10px; height: 30px; background-color: #333; 
                         border-radius: 5px; top: -5px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Volatility relative to market
        volatility = behavioral.get('relative_volatility', 1.0)
        
        st.markdown(f"""
        <div style="margin: 20px 0;">
            <div style="margin-bottom: 5px;">Volatility Relative to Market</div>
            <div style="display: flex; align-items: center;">
                <div style="width: 25%; text-align: left;">Low Volatility</div>
                <div style="width: 50%; text-align: center;">Market Volatility</div>
                <div style="width: 25%; text-align: right;">High Volatility</div>
            </div>
            <div style="width: 100%; background-color: #e0e0e0; height: 20px; border-radius: 10px; position: relative;">
                <div style="position: absolute; left: calc({volatility * 50}%); 
                         transform: translateX(-50%); width: 10px; height: 30px; background-color: #333; 
                         border-radius: 5px; top: -5px;"></div>
            </div>
            <div style="text-align: right;">{volatility:.1f}x Market</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Tab 5: Price Chart
    with tab5:
        st.subheader("Price Chart with Indicators")
        
        # Get the stock data
        stock_data = results.get('data')
        
        if stock_data is not None and not stock_data.empty:
            # Create subplot with 2 rows
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                               vertical_spacing=0.1, 
                               subplot_titles=('Price & Moving Averages', 'Volume'),
                               row_heights=[0.7, 0.3])
            
            # Add candlestick chart
            fig.add_trace(
                go.Candlestick(
                    x=stock_data['date'],
                    open=stock_data['open'],
                    high=stock_data['high'],
                    low=stock_data['low'],
                    close=stock_data['close'],
                    name='Price'
                ),
                row=1, col=1
            )
            
            # Add moving averages
            fig.add_trace(
                go.Scatter(
                    x=stock_data['date'],
                    y=stock_data['sma_20'],
                    line=dict(color='blue', width=1),
                    name='SMA 20'
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=stock_data['date'],
                    y=stock_data['sma_50'],
                    line=dict(color='orange', width=1),
                    name='SMA 50'
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=stock_data['date'],
                    y=stock_data['sma_200'],
                    line=dict(color='red', width=1),
                    name='SMA 200'
                ),
                row=1, col=1
            )
            
            # Add volume
            fig.add_trace(
                go.Bar(
                    x=stock_data['date'],
                    y=stock_data['volume'],
                    name='Volume',
                    marker=dict(color='rgba(0,0,250,0.3)')
                ),
                row=2, col=1
            )
            
            # Update layout
            fig.update_layout(
                title=f'{name} ({ticker}) - Price Chart',
                xaxis_title='Date',
                yaxis_title='Price (₹)',
                xaxis_rangeslider_visible=False,
                height=600,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Technical indicators charts
            st.subheader("Technical Indicators")
            
            # Create subplot with 3 rows for technical indicators
            fig2 = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                                vertical_spacing=0.1, 
                                subplot_titles=('RSI', 'MACD', 'Bollinger Bands'),
                                row_heights=[0.33, 0.33, 0.33])
            
            # Add RSI
            fig2.add_trace(
                go.Scatter(
                    x=stock_data['date'],
                    y=stock_data['rsi'],
                    line=dict(color='purple', width=1),
                    name='RSI'
                ),
                row=1, col=1
            )
            
            # Add RSI overbought/oversold lines
            fig2.add_trace(
                go.Scatter(
                    x=stock_data['date'],
                    y=[70] * len(stock_data),
                    line=dict(color='red', width=1, dash='dash'),
                    name='Overbought (70)'
                ),
                row=1, col=1
            )
            
            fig2.add_trace(
                go.Scatter(
                    x=stock_data['date'],
                    y=[30] * len(stock_data),
                    line=dict(color='green', width=1, dash='dash'),
                    name='Oversold (30)'
                ),
                row=1, col=1
            )
            
            # Add MACD
            fig2.add_trace(
                go.Scatter(
                    x=stock_data['date'],
                    y=stock_data['macd'],
                    line=dict(color='blue', width=1),
                    name='MACD'
                ),
                row=2, col=1
            )
            
            fig2.add_trace(
                go.Scatter(
                    x=stock_data['date'],
                    y=stock_data['macd_signal'],
                    line=dict(color='red', width=1),
                    name='Signal'
                ),
                row=2, col=1
            )
            
            fig2.add_trace(
                go.Bar(
                    x=stock_data['date'],
                    y=stock_data['macd_hist'],
                    name='Histogram',
                    marker=dict(
                        color=[
                            'green' if val >= 0 else 'red' 
                            for val in stock_data['macd_hist']
                        ]
                    )
                ),
                row=2, col=1
            )
            
            # Add Bollinger Bands
            fig2.add_trace(
                go.Scatter(
                    x=stock_data['date'],
                    y=stock_data['close'],
                    line=dict(color='black', width=1),
                    name='Close'
                ),
                row=3, col=1
            )
            
            fig2.add_trace(
                go.Scatter(
                    x=stock_data['date'],
                    y=stock_data['bollinger_high'],
                    line=dict(color='rgba(250,0,0,0.5)', width=1),
                    name='Upper Band'
                ),
                row=3, col=1
            )
            
            fig2.add_trace(
                go.Scatter(
                    x=stock_data['date'],
                    y=stock_data['bollinger_mid'],
                    line=dict(color='rgba(0,0,250,0.5)', width=1),
                    name='Middle Band'
                ),
                row=3, col=1
            )
            
            fig2.add_trace(
                go.Scatter(
                    x=stock_data['date'],
                    y=stock_data['bollinger_low'],
                    line=dict(color='rgba(0,250,0,0.5)', width=1),
                    name='Lower Band'
                ),
                row=3, col=1
            )
            
            # Update layout
            fig2.update_layout(
                height=800,
                showlegend=True
            )
            
            # Update y-axis labels
            fig2.update_yaxes(title_text="RSI", row=1, col=1)
            fig2.update_yaxes(title_text="MACD", row=2, col=1)
            fig2.update_yaxes(title_text="Price (₹)", row=3, col=1)
            
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("No historical price data available for charts.")