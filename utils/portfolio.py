import pandas as pd
import numpy as np
import datetime
import yfinance as yf
from utils.stock_data import get_stock_data


def get_portfolio_data():
    """
    Fetches portfolio data. In a real implementation, this would connect
    to Kite API to get actual portfolio data. For demo purposes, we'll
    return synthetic data.
    
    Returns:
        dict: Portfolio data
    """
    # Demo portfolio data
    holdings = [
        {
            'ticker': 'RELIANCE',
            'name': 'Reliance Industries',
            'sector': 'Energy',
            'quantity': 10,
            'buy_price': 2100,
            'current_price': 2200,
            'current_value': 22000,
            'investment_value': 21000,
            'profit_loss': 1000,
            'profit_loss_percent': 4.76,
            'daily_change': 0.5,
            'daily_change_value': 110
        },
        {
            'ticker': 'TCS',
            'name': 'Tata Consultancy Services',
            'sector': 'Technology',
            'quantity': 5,
            'buy_price': 3200,
            'current_price': 3300,
            'current_value': 16500,
            'investment_value': 16000,
            'profit_loss': 500,
            'profit_loss_percent': 3.13,
            'daily_change': -0.2,
            'daily_change_value': -33
        },
        {
            'ticker': 'INFY',
            'name': 'Infosys',
            'sector': 'Technology',
            'quantity': 15,
            'buy_price': 1500,
            'current_price': 1600,
            'current_value': 24000,
            'investment_value': 22500,
            'profit_loss': 1500,
            'profit_loss_percent': 6.67,
            'daily_change': 1.2,
            'daily_change_value': 288
        },
        {
            'ticker': 'HDFCBANK',
            'name': 'HDFC Bank',
            'sector': 'Financial Services',
            'quantity': 8,
            'buy_price': 1600,
            'current_price': 1550,
            'current_value': 12400,
            'investment_value': 12800,
            'profit_loss': -400,
            'profit_loss_percent': -3.13,
            'daily_change': -0.8,
            'daily_change_value': -99.2
        },
        {
            'ticker': 'TATAMOTORS',
            'name': 'Tata Motors',
            'sector': 'Consumer Cyclical',
            'quantity': 20,
            'buy_price': 400,
            'current_price': 450,
            'current_value': 9000,
            'investment_value': 8000,
            'profit_loss': 1000,
            'profit_loss_percent': 12.5,
            'daily_change': 2.1,
            'daily_change_value': 189
        },
        {
            'ticker': 'SUNPHARMA',
            'name': 'Sun Pharmaceutical',
            'sector': 'Healthcare',
            'quantity': 12,
            'buy_price': 800,
            'current_price': 820,
            'current_value': 9840,
            'investment_value': 9600,
            'profit_loss': 240,
            'profit_loss_percent': 2.5,
            'daily_change': 0.3,
            'daily_change_value': 29.52
        },
        {
            'ticker': 'BAJFINANCE',
            'name': 'Bajaj Finance',
            'sector': 'Financial Services',
            'quantity': 6,
            'buy_price': 5500,
            'current_price': 5800,
            'current_value': 34800,
            'investment_value': 33000,
            'profit_loss': 1800,
            'profit_loss_percent': 5.45,
            'daily_change': 1.5,
            'daily_change_value': 522
        },
        {
            'ticker': 'WIPRO',
            'name': 'Wipro',
            'sector': 'Technology',
            'quantity': 18,
            'buy_price': 450,
            'current_price': 430,
            'current_value': 7740,
            'investment_value': 8100,
            'profit_loss': -360,
            'profit_loss_percent': -4.44,
            'daily_change': -1.0,
            'daily_change_value': -77.4
        },
        {
            'ticker': 'ADANIPORTS',
            'name': 'Adani Ports',
            'sector': 'Industrials',
            'quantity': 7,
            'buy_price': 700,
            'current_price': 750,
            'current_value': 5250,
            'investment_value': 4900,
            'profit_loss': 350,
            'profit_loss_percent': 7.14,
            'daily_change': 0.9,
            'daily_change_value': 47.25
        },
        {
            'ticker': 'AXISBANK',
            'name': 'Axis Bank',
            'sector': 'Financial Services',
            'quantity': 9,
            'buy_price': 750,
            'current_price': 760,
            'current_value': 6840,
            'investment_value': 6750,
            'profit_loss': 90,
            'profit_loss_percent': 1.33,
            'daily_change': 0.1,
            'daily_change_value': 6.84
        }
    ]
    
    # Calculate portfolio level metrics
    portfolio_value = sum(holding['current_value'] for holding in holdings)
    investment_value = sum(holding['investment_value'] for holding in holdings)
    profit_loss = portfolio_value - investment_value
    profit_loss_percent = (profit_loss / investment_value) * 100 if investment_value else 0
    daily_change = sum(holding['daily_change_value'] for holding in holdings)
    daily_change_percent = (daily_change / (portfolio_value - daily_change)) * 100 if abs(portfolio_value - daily_change) > 0.001 else 0
    
    # Calculate sector allocation
    sector_allocation = {}
    for holding in holdings:
        sector = holding['sector']
        if sector in sector_allocation:
            sector_allocation[sector] += holding['current_value']
        else:
            sector_allocation[sector] = holding['current_value']
    
    # Convert to percentages
    sector_percentages = {sector: (value / portfolio_value) * 100 for sector, value in sector_allocation.items()}
    
    # Prepare return object
    portfolio_data = {
        'holdings': holdings,
        'portfolio_value': portfolio_value,
        'investment_value': investment_value,
        'profit_loss': profit_loss,
        'profit_loss_percent': profit_loss_percent,
        'daily_change': daily_change,
        'daily_change_percent': daily_change_percent,
        'sector_allocation': sector_percentages,
        'last_updated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return portfolio_data


def calculate_portfolio_metrics(portfolio):
    """
    Calculates various metrics for the portfolio.
    
    Args:
        portfolio (dict): Portfolio data
    
    Returns:
        dict: Calculated metrics
    """
    holdings = portfolio['holdings']
    
    # Calculate weighted beta
    weighted_beta = 0
    total_weight = 0
    
    # Get correlation matrix for diversification calculation
    tickers = [holding['ticker'] + '.NS' for holding in holdings]
    start_date = datetime.datetime.now() - datetime.timedelta(days=365)
    end_date = datetime.datetime.now()
    
    try:
        # Try to fetch historical data for correlation matrix
        stock_data = {}
        for ticker in tickers:
            data = get_stock_data(ticker, period='1y')
            if data is not None:
                stock_data[ticker] = data['close']
        
        # Create a DataFrame with all stock prices
        if stock_data:
            prices_df = pd.DataFrame(stock_data)
            # Calculate correlation matrix
            correlation_matrix = prices_df.corr()
            # Calculate average correlation (excluding self-correlations)
            correlations = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    correlations.append(correlation_matrix.iloc[i, j])
            avg_correlation = np.mean(correlations) if correlations else 0
            diversification_score = 1 - avg_correlation
        else:
            diversification_score = 0.5  # Default if data fetch fails
    except Exception as e:
        print(f"Error calculating diversification score: {e}")
        diversification_score = 0.5  # Default value
    
    # Calculate return metrics
    try:
        # Calculate portfolio returns
        investment_value = portfolio['investment_value']
        current_value = portfolio['portfolio_value']
        total_return = (current_value - investment_value) / investment_value
        
        # Calculate daily return
        daily_change_percent = portfolio['daily_change_percent']
        
        # Annualized metrics
        annualized_return = ((1 + total_return) ** (365 / 30)) - 1  # Assuming 30 days of holding
        
        # Estimate risk
        risk_score = 0
        # Add risk based on sector concentration
        sector_allocation = portfolio['sector_allocation']
        max_sector_allocation = max(sector_allocation.values()) if sector_allocation else 0
        if max_sector_allocation > 40:
            risk_score += 0.3  # High concentration risk
        elif max_sector_allocation > 25:
            risk_score += 0.2  # Medium concentration risk
        else:
            risk_score += 0.1  # Low concentration risk
        
        # Add risk based on diversification
        if diversification_score < 0.3:
            risk_score += 0.3  # Low diversification
        elif diversification_score < 0.6:
            risk_score += 0.2  # Medium diversification
        else:
            risk_score += 0.1  # High diversification
        
        # Scale risk score
        risk_score = min(risk_score, 1.0)
        
        # Calculate potential risk-adjusted return (Sharpe ratio like)
        if risk_score > 0:
            risk_adjusted_return = annualized_return / risk_score
        else:
            risk_adjusted_return = 0
    
    except Exception as e:
        print(f"Error calculating return metrics: {e}")
        total_return = 0
        annualized_return = 0
        risk_score = 0.5
        risk_adjusted_return = 0
        daily_change_percent = 0
    
    # Prepare metrics object
    metrics = {
        'total_return': total_return,
        'annualized_return': annualized_return,
        'daily_return': daily_change_percent / 100,  # Convert percentage to decimal
        'risk_score': risk_score,
        'risk_adjusted_return': risk_adjusted_return,
        'diversification_score': diversification_score
    }
    
    return metrics