import pandas as pd
import numpy as np
from utils.analysis import perform_complete_analysis

def generate_stock_recommendation(analysis_results, time_horizon='medium_term'):
    """
    Generates a stock recommendation based on analysis results and time horizon.
    
    Args:
        analysis_results (dict): Results from technical and fundamental analysis
        time_horizon (str): Time horizon for recommendation ('short_term', 'medium_term', 'long_term')
    
    Returns:
        dict: Recommendation details
    """
    # Check if analysis was successful
    if analysis_results.get('status') != 'success':
        return {
            'ticker': analysis_results.get('ticker', 'Unknown'),
            'recommendation': 'No Recommendation',
            'reasoning': 'Insufficient data for analysis',
            'confidence': 0,
            'position_sizing': None,
            'target_price': None,
            'stop_loss': None,
            'time_horizon': time_horizon
        }
    
    # Extract scores from analysis
    technical_score = analysis_results.get('technical', {}).get('tech_score', 0)
    fundamental_score = analysis_results.get('fundamental', {}).get('fund_score', 0)
    behavioral_score = analysis_results.get('behavioral', {}).get('behavioral_score', 0)
    
    # Adjust weights based on time horizon
    if time_horizon == 'short_term':
        # Short-term: emphasize technical analysis and behavioral factors
        tech_weight = 0.7
        fund_weight = 0.1
        behav_weight = 0.2
    elif time_horizon == 'long_term':
        # Long-term: emphasize fundamental analysis
        tech_weight = 0.2
        fund_weight = 0.7
        behav_weight = 0.1
    else:  # medium_term (default)
        # Medium-term: balanced approach
        tech_weight = 0.4
        fund_weight = 0.4
        behav_weight = 0.2
    
    # Combine scores using appropriate weights for the time horizon
    combined_score = (technical_score * tech_weight) + (fundamental_score * fund_weight) + (behavioral_score * behav_weight)
    
    # Determine recommendation based on combined score
    if combined_score >= 7:
        recommendation = 'Strong Buy'
        confidence = 0.9
    elif combined_score >= 3:
        recommendation = 'Buy'
        confidence = 0.7
    elif combined_score > -3:
        recommendation = 'Hold'
        confidence = 0.5
    elif combined_score > -7:
        recommendation = 'Reduce'
        confidence = 0.7
    else:
        recommendation = 'Sell'
        confidence = 0.9
    
    # Get current price for target calculations
    current_price = analysis_results.get('current_price')
    
    # Generate reasoning
    tech_analysis = analysis_results.get('technical', {})
    fund_analysis = analysis_results.get('fundamental', {}).get('analysis', {})
    
    reasoning_points = []
    
    # Technical factors
    if 'trend' in tech_analysis:
        reasoning_points.append(f"Stock is in a {tech_analysis.get('trend')} trend.")
    
    if 'rsi_signal' in tech_analysis and tech_analysis.get('rsi_signal') != 'Neutral':
        reasoning_points.append(f"RSI indicates stock is {tech_analysis.get('rsi_signal')}.")
    
    if 'macd_crossover' in tech_analysis and tech_analysis.get('macd_crossover'):
        reasoning_points.append(f"Recent {tech_analysis.get('macd_crossover')} MACD crossover detected.")
    
    if 'golden_cross' in tech_analysis and tech_analysis.get('golden_cross'):
        reasoning_points.append("Recent Golden Cross (50-day MA crossing above 200-day MA) signals positive trend.")
    
    if 'death_cross' in tech_analysis and tech_analysis.get('death_cross'):
        reasoning_points.append("Recent Death Cross (50-day MA crossing below 200-day MA) signals negative trend.")
    
    # Fundamental factors
    valuation = fund_analysis.get('valuation', {})
    financial_health = fund_analysis.get('financial_health', {})
    
    for metric, details in valuation.items():
        if 'analysis' in details and metric != 'market_cap':
            reasoning_points.append(f"{metric.replace('_', ' ').title()}: {details.get('analysis')}.")
    
    for metric, details in financial_health.items():
        if 'analysis' in details:
            reasoning_points.append(f"{metric.replace('_', ' ').title()}: {details.get('analysis')}.")
    
    # Combine reasoning points
    reasoning = " ".join(reasoning_points)
    
    # Calculate suggested target price
    target_price = None
    stop_loss = None
    
    if current_price:
        # Calculate based on recommendation and technical indicators
        if recommendation == 'Strong Buy':
            target_price = current_price * 1.15  # 15% upside target
            stop_loss = current_price * 0.93     # 7% downside risk
        elif recommendation == 'Buy':
            target_price = current_price * 1.1   # 10% upside target
            stop_loss = current_price * 0.95     # 5% downside risk
        elif recommendation == 'Reduce':
            target_price = current_price * 0.9   # 10% downside target
            stop_loss = current_price * 1.05     # 5% upside risk (for short positions)
        elif recommendation == 'Sell':
            target_price = current_price * 0.85  # 15% downside target
            stop_loss = current_price * 1.07     # 7% upside risk (for short positions)
    
    # Calculate position sizing
    position_sizing = calculate_position_size(recommendation, analysis_results)
    
    return {
        'ticker': analysis_results.get('ticker'),
        'name': analysis_results.get('name'),
        'current_price': current_price,
        'technical_score': technical_score,
        'fundamental_score': fundamental_score,
        'combined_score': combined_score,
        'recommendation': recommendation,
        'reasoning': reasoning,
        'confidence': confidence,
        'position_sizing': position_sizing,
        'target_price': target_price,
        'stop_loss': stop_loss,
        'time_horizon': time_horizon  # Use the passed time horizon parameter
    }


def calculate_position_size(recommendation, analysis_results):
    """
    Calculates suggested position size based on recommendation and risk profile.
    
    Args:
        recommendation (str): Stock recommendation
        analysis_results (dict): Analysis results
    
    Returns:
        dict: Position size suggestions for different risk profiles
    """
    # Get volatility from technical analysis
    tech_analysis = analysis_results.get('technical', {})
    volatility_signal = tech_analysis.get('volatility_signal', 'Average')
    
    # Base allocation percentages by risk profile
    base_allocations = {
        'Conservative': 0.03,  # 3% of portfolio
        'Moderate': 0.05,      # 5% of portfolio
        'Aggressive': 0.08     # 8% of portfolio
    }
    
    # Adjust based on recommendation
    recommendation_multipliers = {
        'Strong Buy': 1.2,
        'Buy': 1.0,
        'Hold': 0.5,
        'Reduce': 0,
        'Sell': 0
    }
    
    # Adjust based on volatility
    volatility_multipliers = {
        'Low': 1.2,
        'Average': 1.0,
        'High': 0.8
    }
    
    # Calculate position sizes
    position_sizes = {}
    
    for risk_profile, base_allocation in base_allocations.items():
        # Skip calculation for sell recommendations
        if recommendation in ['Reduce', 'Sell']:
            position_sizes[risk_profile] = 0
            continue
        
        # Apply multipliers
        rec_multiplier = recommendation_multipliers.get(recommendation, 0)
        vol_multiplier = volatility_multipliers.get(volatility_signal, 1.0)
        
        # Calculate final allocation
        allocation = base_allocation * rec_multiplier * vol_multiplier
        
        # Ensure reasonable bounds
        allocation = min(allocation, 0.15)  # Max 15% of portfolio
        allocation = max(allocation, 0)     # Min 0% of portfolio
        
        # Convert to percentage
        position_sizes[risk_profile] = round(allocation * 100, 1)
    
    return position_sizes


def generate_all_recommendations(portfolio, time_horizon='medium_term'):
    """
    Generates recommendations for all stocks in a portfolio based on the specified time horizon.
    
    Args:
        portfolio (dict): Portfolio data containing stocks
        time_horizon (str): Time horizon for recommendations - 'short_term', 'medium_term', or 'long_term'
    
    Returns:
        list: Recommendations for all stocks
    """
    recommendations = []
    
    # Run analysis and generate recommendations for each holding
    for holding in portfolio.get('holdings', []):
        ticker = holding.get('ticker')
        
        # Skip if no ticker
        if not ticker:
            continue
        
        try:
            # Perform analysis
            analysis_results = perform_complete_analysis(ticker)
            
            # Generate recommendation with the specified time horizon
            recommendation = generate_stock_recommendation(analysis_results, time_horizon=time_horizon)
            
            # Include technical and fundamental analysis data for detailed view
            if recommendation:
                # Add the original analysis data to the recommendation for detailed display
                recommendation['technical_analysis'] = analysis_results.get('technical', {})
                recommendation['fundamental_analysis'] = analysis_results.get('fundamental', {})
                recommendation['behavioral_score'] = analysis_results.get('behavioral', {}).get('behavioral_score', 0)
                recommendations.append(recommendation)
        
        except Exception as e:
            print(f"Error generating recommendation for {ticker}: {e}")
            # Continue to next stock
    
    # Sort recommendations by score (highest first)
    recommendations.sort(key=lambda x: x.get('combined_score', 0), reverse=True)
    
    return recommendations