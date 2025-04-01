import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.portfolio import calculate_portfolio_metrics

def show_portfolio_dashboard(portfolio):
    """
    Display the portfolio dashboard page.
    
    Args:
        portfolio (dict): Portfolio data
    """
    st.title("Portfolio Dashboard")
    
    if not portfolio:
        st.warning("No portfolio data available. Please log in or select a portfolio.")
        return
    
    # Get portfolio metrics
    metrics = calculate_portfolio_metrics(portfolio)
    
    # Portfolio summary card
    with st.container():
        st.subheader("Portfolio Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Total Value",
                value=f"₹{portfolio['portfolio_value']:,.2f}",
                delta=f"₹{portfolio['daily_change']:,.2f} ({portfolio['daily_change_percent']:.2f}%)"
            )
        
        with col2:
            st.metric(
                label="Invested Amount",
                value=f"₹{portfolio['investment_value']:,.2f}"
            )
        
        with col3:
            profit_loss = portfolio['profit_loss']
            profit_loss_percent = portfolio['profit_loss_percent']
            st.metric(
                label="Overall P&L",
                value=f"₹{profit_loss:,.2f}",
                delta=f"{profit_loss_percent:.2f}%"
            )
    
    # Additional metrics
    with st.container():
        st.subheader("Performance Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Annualized Return",
                value=f"{metrics['annualized_return'] * 100:.2f}%"
            )
        
        with col2:
            st.metric(
                label="Risk Score",
                value=f"{metrics['risk_score']:.2f}"
            )
        
        with col3:
            st.metric(
                label="Risk-Adjusted Return",
                value=f"{metrics['risk_adjusted_return']:.2f}"
            )
        
        with col4:
            diversification = metrics['diversification_score']
            st.metric(
                label="Diversification",
                value=f"{diversification:.2f}",
                delta="Good" if diversification > 0.6 else "Average" if diversification > 0.3 else "Poor",
                delta_color="normal"
            )
    
    # Sector allocation chart
    with st.container():
        st.subheader("Sector Allocation")
        
        sector_allocation = portfolio['sector_allocation']
        
        if sector_allocation:
            # Create a DataFrame for the pie chart
            sector_df = pd.DataFrame({
                'Sector': list(sector_allocation.keys()),
                'Allocation (%)': list(sector_allocation.values())
            })
            
            # Create a pie chart using Plotly
            fig = px.pie(
                sector_df,
                values='Allocation (%)',
                names='Sector',
                title='Portfolio Sector Allocation',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            
            # Update layout
            fig.update_layout(
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5
                )
            )
            
            # Show the chart
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sector allocation data available.")
    
    # Holdings table
    with st.container():
        st.subheader("Portfolio Holdings")
        
        if portfolio['holdings']:
            # Create a DataFrame for the table
            holdings_df = pd.DataFrame(portfolio['holdings'])
            
            # Format the columns
            formatted_df = holdings_df.copy()
            formatted_df['current_value'] = formatted_df['current_value'].apply(lambda x: f"₹{x:,.2f}")
            formatted_df['investment_value'] = formatted_df['investment_value'].apply(lambda x: f"₹{x:,.2f}")
            formatted_df['profit_loss'] = formatted_df['profit_loss'].apply(lambda x: f"₹{x:,.2f}")
            formatted_df['profit_loss_percent'] = formatted_df['profit_loss_percent'].apply(lambda x: f"{x:.2f}%")
            formatted_df['current_price'] = formatted_df['current_price'].apply(lambda x: f"₹{x:,.2f}")
            formatted_df['buy_price'] = formatted_df['buy_price'].apply(lambda x: f"₹{x:,.2f}")
            
            # Select and rename columns for display
            display_df = formatted_df[[
                'ticker', 'name', 'sector', 'quantity', 
                'current_price', 'buy_price', 'current_value',
                'profit_loss', 'profit_loss_percent'
            ]].rename(columns={
                'ticker': 'Ticker',
                'name': 'Company',
                'sector': 'Sector',
                'quantity': 'Quantity',
                'current_price': 'Current Price',
                'buy_price': 'Buy Price',
                'current_value': 'Current Value',
                'profit_loss': 'P&L',
                'profit_loss_percent': 'P&L %'
            })
            
            # Show the table
            st.dataframe(
                display_df,
                use_container_width=True
            )
        else:
            st.info("No holdings data available.")
    
    # Performance chart
    with st.container():
        st.subheader("Contribution to P&L")
        
        if portfolio['holdings']:
            # Create a DataFrame for the bar chart
            holdings_df = pd.DataFrame(portfolio['holdings'])
            
            # Sort by absolute profit/loss contribution
            holdings_df = holdings_df.sort_values(by='profit_loss', key=abs, ascending=False)
            
            # Take top 10 contributors
            top_contributors = holdings_df.head(10)
            
            # Create a horizontal bar chart
            fig = go.Figure()
            
            # Add bars for positive and negative contributions
            colors = ['green' if x >= 0 else 'red' for x in top_contributors['profit_loss']]
            
            fig.add_trace(go.Bar(
                x=top_contributors['profit_loss'],
                y=top_contributors['name'],
                orientation='h',
                marker_color=colors,
                text=[f"₹{x:,.2f}" for x in top_contributors['profit_loss']],
                textposition='auto'
            ))
            
            # Update layout
            fig.update_layout(
                title='Top 10 P&L Contributors',
                xaxis_title='Profit/Loss (₹)',
                yaxis=dict(
                    title='Stock',
                    autorange="reversed"  # Reverses the order to have highest value at top
                )
            )
            
            # Show the chart
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No holdings data available for P&L contribution chart.")
    
    # Last updated info
    st.caption(f"Last updated: {portfolio.get('last_updated', 'Unknown')}")