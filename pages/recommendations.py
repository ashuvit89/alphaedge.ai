import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.recommendation import generate_all_recommendations

def show_recommendations(portfolio):
    """
    Display the recommendations page.
    
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
        st.title("Stock Recommendations")
    
    if not portfolio:
        st.warning("No portfolio data available. Please log in or select a portfolio.")
        return
    
    # Recommendations generation section
    with st.container():
        # Use a more responsive layout with more columns for the description
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Generate Stock Recommendations")
            st.write("""
            This tool analyzes your portfolio stocks and provides personalized recommendations
            based on technical and fundamental analysis. Select a time horizon to customize recommendations.
            """)
            
            # Add time horizon selector below the text for better layout
            time_horizon = st.radio(
                "Time Horizon:",
                ["Short Term (1-3 months)", "Medium Term (3-9 months)", "Long Term (>12 months)"],
                index=1,  # Default to medium term
                horizontal=True
            )
            
            # Map the selection to a value that can be passed to the recommendation engine
            horizon_value = "short_term" if time_horizon.startswith("Short") else \
                            "medium_term" if time_horizon.startswith("Medium") else "long_term"
        
        with col2:
            # Add some vertical spacing to align the button better
            st.write("")
            st.write("")
            # Use more specific button text to fit in the space better
            if st.button("Generate", type="primary", use_container_width=True):
                # Show a spinner while generating recommendations
                with st.spinner("Analyzing stocks and generating recommendations..."):
                    # Generate recommendations
                    recommendations = generate_all_recommendations(portfolio, time_horizon=horizon_value)
                    
                    # Store in session state
                    st.session_state.recommendations = recommendations
                    st.session_state.selected_horizon = horizon_value
                    
                    # Show success message
                    if recommendations:
                        st.success(f"Generated {time_horizon} recommendations for {len(recommendations)} stocks!")
                    else:
                        st.warning("No recommendations could be generated. Try adding stocks to your portfolio.")
    
    # Display recommendations if available
    if 'recommendations' in st.session_state and st.session_state.recommendations:
        display_recommendations(st.session_state.recommendations)
    else:
        st.info("Click 'Generate Recommendations' to analyze your portfolio stocks.")
        
        # Sample recommendation visualization
        display_sample_recommendation()


def display_recommendations(recommendations):
    """
    Display the recommendations in a structured format.
    
    Args:
        recommendations (list): List of recommendation dictionaries
    """
    # Overview section
    st.subheader("Recommendations Overview")
    
    # Group recommendations by category
    strong_buy = [r for r in recommendations if r.get('recommendation') == 'Strong Buy']
    buy = [r for r in recommendations if r.get('recommendation') == 'Buy']
    hold = [r for r in recommendations if r.get('recommendation') == 'Hold']
    reduce = [r for r in recommendations if r.get('recommendation') == 'Reduce']
    sell = [r for r in recommendations if r.get('recommendation') == 'Sell']
    
    # Create columns for the groups
    cols = st.columns(5)
    with cols[0]:
        st.metric(label="Strong Buy", value=len(strong_buy))
    with cols[1]:
        st.metric(label="Buy", value=len(buy))
    with cols[2]:
        st.metric(label="Hold", value=len(hold))
    with cols[3]:
        st.metric(label="Reduce", value=len(reduce))
    with cols[4]:
        st.metric(label="Sell", value=len(sell))
    
    # Create a DataFrame for all recommendations
    rec_data = []
    for rec in recommendations:
        # Make sure we format numeric values properly to fix the display truncation
        current_price = rec.get('current_price', 0)
        tech_score = rec.get('technical_score', 0)
        fund_score = rec.get('fundamental_score', 0)
        comb_score = rec.get('combined_score', 0)
        
        rec_data.append({
            'Ticker': rec.get('ticker', ''),
            'Name': rec.get('name', ''),
            # Add padding to prevent truncation of price values
            'Current Price': f"₹{current_price:.2f}",
            'Technical Score': f"{tech_score:.1f}",
            'Fundamental Score': f"{fund_score:.1f}",
            'Combined Score': f"{comb_score:.1f}",
            'Recommendation': rec.get('recommendation', 'N/A')
        })
    
    # Convert everything to string type to prevent arrow conversion issues
    rec_df = pd.DataFrame(rec_data).astype(str)
    
    # Display the recommendations table with color coding
    st.write("### All Recommendations")
    
    # Map recommendations to colors
    color_map = {
        'Strong Buy': '#1b9e77',
        'Buy': '#7fc97f',
        'Hold': '#ffff99',
        'Reduce': '#fdb462',
        'Sell': '#e41a1c',
        'No Recommendation': '#999999'
    }
    
    # Convert DataFrame for visualization
    rec_plot_data = []
    for rec in recommendations:
        rec_plot_data.append({
            'Ticker': rec.get('ticker', ''),
            'Name': rec.get('name', ''),
            'Score': float(rec.get('combined_score', 0)),
            'Recommendation': rec.get('recommendation', 'No Recommendation')
        })
    
    rec_plot_df = pd.DataFrame(rec_plot_data)
    
    # Create horizontal bar chart
    if not rec_plot_df.empty:
        # Sort by score
        rec_plot_df = rec_plot_df.sort_values(by='Score', ascending=False)
        
        fig = px.bar(
            rec_plot_df, 
            x='Score', 
            y='Ticker',
            color='Recommendation',
            color_discrete_map=color_map,
            title='Stock Recommendations by Score',
            orientation='h',
            height=400
        )
        
        fig.update_layout(
            xaxis_title='Combined Score',
            yaxis_title='Stock Ticker',
            yaxis={'categoryorder': 'total ascending'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Add styling directly through color coding in the UI
    # Use the base DataFrame without styling to avoid any string conversion issues
    
    # Display the table
    st.dataframe(rec_df, use_container_width=True)
    
    # Detailed recommendations
    st.write("### Detailed Recommendations")
    
    # Create tabs for different recommendation categories
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Strong Buy", "Buy", "Hold", "Reduce", "Sell"])
    
    # Tab 1: Strong Buy
    with tab1:
        if strong_buy:
            for rec in strong_buy:
                display_detailed_recommendation(rec)
        else:
            st.info("No Strong Buy recommendations available.")
    
    # Tab 2: Buy
    with tab2:
        if buy:
            for rec in buy:
                display_detailed_recommendation(rec)
        else:
            st.info("No Buy recommendations available.")
    
    # Tab 3: Hold
    with tab3:
        if hold:
            for rec in hold:
                display_detailed_recommendation(rec)
        else:
            st.info("No Hold recommendations available.")
    
    # Tab 4: Reduce
    with tab4:
        if reduce:
            for rec in reduce:
                display_detailed_recommendation(rec)
        else:
            st.info("No Reduce recommendations available.")
    
    # Tab 5: Sell
    with tab5:
        if sell:
            for rec in sell:
                display_detailed_recommendation(rec)
        else:
            st.info("No Sell recommendations available.")


def display_detailed_recommendation(rec):
    """
    Display detailed recommendation for a single stock.
    
    Args:
        rec (dict): Recommendation dictionary
    """
    ticker = rec.get('ticker', 'Unknown')
    name = rec.get('name', ticker)
    
    with st.expander(f"{name} ({ticker}) - {rec.get('recommendation', 'N/A')}"):
        # Create tabs for recommendation details and analysis summary
        detail_tab1, detail_tab2, detail_tab3 = st.tabs(["Recommendation", "Technical Analysis", "Fundamental Analysis"])
        
        # Tab 1: Recommendation Details
        with detail_tab1:
            # Basic info
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label="Current Price",
                    value=f"₹{rec.get('current_price', 0):.2f}"
                )
            
            with col2:
                target_price = rec.get('target_price')
                if target_price:
                    percent_change = ((target_price / rec.get('current_price', 1)) - 1) * 100
                    st.metric(
                        label="Target Price",
                        value=f"₹{target_price:.2f}",
                        delta=f"{percent_change:.1f}%"
                    )
                else:
                    st.metric(label="Target Price", value="N/A")
            
            with col3:
                stop_loss = rec.get('stop_loss')
                if stop_loss:
                    percent_change = ((stop_loss / rec.get('current_price', 1)) - 1) * 100
                    st.metric(
                        label="Stop Loss",
                        value=f"₹{stop_loss:.2f}",
                        delta=f"{percent_change:.1f}%"
                    )
                else:
                    st.metric(label="Stop Loss", value="N/A")
            
            # Scores
            st.write("##### Analysis Scores")
            score_cols = st.columns(3)
            
            with score_cols[0]:
                st.metric(
                    label="Technical Score",
                    value=f"{rec.get('technical_score', 0):.1f}/10"
                )
            
            with score_cols[1]:
                st.metric(
                    label="Fundamental Score",
                    value=f"{rec.get('fundamental_score', 0):.1f}/10"
                )
            
            with score_cols[2]:
                behavioral_score = rec.get('behavioral_score', 0)
                
                st.metric(
                    label="Behavioral Score",
                    value=f"{behavioral_score:.1f}/10"
                )
                
            # Overall recommendation and score
            rec_score = rec.get('combined_score', 0)
            rec_color = "#1b9e77" if rec_score >= 7 else "#7fc97f" if rec_score >= 3 else \
                        "#ffff99" if rec_score >= -3 else "#fdb462" if rec_score >= -7 else "#e41a1c"
                        
            st.markdown(f"""
            <div style="margin: 20px 0; padding: 10px; border-radius: 5px; background-color: {rec_color}; 
                     color: {'black' if -3 <= rec_score < 7 else 'white'}; text-align: center;">
                <div style="font-size: 1.5em; font-weight: bold; margin-bottom: 5px;">
                    {rec.get('recommendation', 'N/A')}
                </div>
                <div>Combined Score: {rec_score:.1f}/10</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Reasoning
            st.write("##### Recommendation Reasoning")
            reasoning = rec.get('reasoning', 'No detailed reasoning available.')
            st.write(reasoning)
            
            # Position sizing
            position_sizing = rec.get('position_sizing')
            if position_sizing:
                st.write("##### Suggested Position Size")
                ps_cols = st.columns(3)
                
                with ps_cols[0]:
                    # Ensure there's enough space by using a shorter format
                    conservative = position_sizing.get('Conservative', 0)
                    st.metric(
                        label="Conservative",
                        value=f"{conservative:.1f}%"
                    )
                
                with ps_cols[1]:
                    moderate = position_sizing.get('Moderate', 0)
                    st.metric(
                        label="Moderate",
                        value=f"{moderate:.1f}%"
                    )
                
                with ps_cols[2]:
                    aggressive = position_sizing.get('Aggressive', 0)
                    st.metric(
                        label="Aggressive",
                        value=f"{aggressive:.1f}%"
                    )
            
            # Time horizon
            horizon_text = rec.get('time_horizon', 'Medium Term')
            horizon_display = "Short Term (1-3 months)" if horizon_text == "short_term" else \
                              "Medium Term (3-9 months)" if horizon_text == "medium_term" else \
                              "Long Term (>12 months)"
            
            st.write(f"**Time Horizon:** {horizon_display}")
            
            # Confidence level
            confidence = rec.get('confidence', 0)
            confidence_text = "Very High" if confidence > 0.8 else "High" if confidence > 0.6 else "Moderate" if confidence > 0.4 else "Low"
            st.write(f"**Confidence Level:** {confidence_text} ({confidence:.1f})")
            
        # Tab 2: Technical Analysis Summary
        with detail_tab2:
            tech_analysis = rec.get('technical_analysis', {})
            
            if not tech_analysis:
                st.info("Technical analysis details not available for this recommendation.")
            else:
                # Technical score and overall assessment
                tech_score = tech_analysis.get('tech_score', 0)
                overall_technical = tech_analysis.get('overall_technical', 'Neutral')
                
                st.metric(
                    label="Technical Analysis Score",
                    value=f"{tech_score:.1f}/10",
                    delta=overall_technical
                )
                
                # Technical indicators table
                st.write("##### Key Technical Indicators")
                
                # Prepare data for the table
                indicators = {
                    'Trend': tech_analysis.get('trend', 'N/A'),
                    'RSI (14)': f"{tech_analysis.get('rsi', 0):.2f}",
                    'MACD Signal': tech_analysis.get('macd_signal', 'N/A'),
                    'ADX': f"{tech_analysis.get('adx', 0):.2f}",
                    'Bollinger Signal': tech_analysis.get('bollinger_signal', 'N/A'),
                    'Volume Signal': tech_analysis.get('volume_signal', 'N/A')
                }
                
                # Create a DataFrame and display
                tech_indicator_df = pd.DataFrame({
                    'Indicator': list(indicators.keys()),
                    'Value': list(indicators.values())
                })
                
                st.table(tech_indicator_df)
                
                # Technical signals
                st.write("##### Technical Signals")
                
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
                
                if signals:
                    for signal in signals:
                        st.write(signal)
                else:
                    st.write("No significant technical signals detected")
        
        # Tab 3: Fundamental Analysis Summary
        with detail_tab3:
            fund_analysis = rec.get('fundamental_analysis', {})
            
            if not fund_analysis:
                st.info("Fundamental analysis details not available for this recommendation.")
            else:
                # Fundamental score and overall assessment
                fund_score = fund_analysis.get('fund_score', 0)
                overall_fundamental = fund_analysis.get('overall_fundamental', 'Neutral')
                
                st.metric(
                    label="Fundamental Analysis Score",
                    value=f"{fund_score:.1f}/10",
                    delta=overall_fundamental
                )
                
                # Financial metrics
                st.write("##### Key Financial Metrics")
                
                # Get analysis data
                analysis = fund_analysis.get('analysis', {})
                
                # Valuation metrics
                valuation = analysis.get('valuation', {})
                if valuation:
                    st.write("**Valuation Metrics**")
                    
                    val_data = {'Metric': [], 'Value': [], 'Industry Avg': [], 'Analysis': []}
                    
                    for metric, details in valuation.items():
                        if metric != 'market_cap':
                            val_data['Metric'].append(metric.replace('_', ' ').title())
                            val_data['Value'].append(f"{details.get('value', 0):.2f}")
                            val_data['Industry Avg'].append(f"{details.get('industry_avg', 'N/A')}")
                            val_data['Analysis'].append(details.get('analysis', 'N/A'))
                    
                    if val_data['Metric']:
                        st.table(pd.DataFrame(val_data))
                
                # Financial health metrics
                financial_health = analysis.get('financial_health', {})
                if financial_health:
                    st.write("**Financial Health**")
                    
                    fin_data = {'Metric': [], 'Value': [], 'Industry Avg': [], 'Analysis': []}
                    
                    for metric, details in financial_health.items():
                        fin_data['Metric'].append(metric.replace('_', ' ').title())
                        fin_data['Value'].append(f"{details.get('value', 0):.2f}" if isinstance(details.get('value'), (int, float)) else details.get('value', 'N/A'))
                        fin_data['Industry Avg'].append(f"{details.get('industry_avg', 'N/A')}")
                        fin_data['Analysis'].append(details.get('analysis', 'N/A'))
                    
                    if fin_data['Metric']:
                        st.table(pd.DataFrame(fin_data))


def display_sample_recommendation():
    """
    Display a sample recommendation for demonstration purposes.
    """
    st.subheader("Sample Recommendation Visualization")
    
    # Sample data
    sample_data = {
        'Ticker': ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'TATAMOTORS'],
        'Name': ['Reliance Industries', 'Tata Consultancy Services', 'HDFC Bank', 'Infosys', 'Tata Motors'],
        'Score': [8.5, 6.2, 4.1, -2.3, -5.7],
        'Recommendation': ['Strong Buy', 'Buy', 'Hold', 'Reduce', 'Sell']
    }
    
    sample_df = pd.DataFrame(sample_data)
    
    # Color map
    color_map = {
        'Strong Buy': '#1b9e77',
        'Buy': '#7fc97f',
        'Hold': '#ffff99',
        'Reduce': '#fdb462',
        'Sell': '#e41a1c'
    }
    
    # Create horizontal bar chart
    fig = px.bar(
        sample_df, 
        x='Score', 
        y='Ticker',
        color='Recommendation',
        color_discrete_map=color_map,
        title='Sample Stock Recommendations by Score',
        orientation='h',
        height=300
    )
    
    fig.update_layout(
        xaxis_title='Combined Score',
        yaxis_title='Stock Ticker',
        yaxis={'categoryorder': 'total ascending'}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption("Note: This is a sample visualization. Generate real recommendations to see your portfolio analysis.")