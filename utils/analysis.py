import pandas as pd
import numpy as np
from utils.stock_data import get_stock_data, calculate_technical_indicators, get_fundamental_data, get_industry_averages

def analyze_technical_indicators(stock_data):
    """
    Analyzes technical indicators for a stock.
    
    Args:
        stock_data (pandas.DataFrame): DataFrame with stock data and indicators
    
    Returns:
        dict: Analysis results for technical indicators
    """
    # Check if we have enough data
    if stock_data is None or len(stock_data) < 200:
        return {
            'status': 'error',
            'message': 'Insufficient data for technical analysis'
        }
    
    # Get the most recent data
    latest = stock_data.iloc[-1]
    
    # Trend analysis based on SMA
    price = latest['close']
    sma_20 = latest['sma_20']
    sma_50 = latest['sma_50']
    sma_200 = latest['sma_200']
    
    # Check for golden cross / death cross (SMA 50 crossing SMA 200)
    golden_cross = False
    death_cross = False
    for i in range(-20, -1):
        if i+1 >= len(stock_data) or i >= len(stock_data):
            continue
        if stock_data.iloc[i]['sma_50'] < stock_data.iloc[i]['sma_200'] and \
           stock_data.iloc[i+1]['sma_50'] > stock_data.iloc[i+1]['sma_200']:
            golden_cross = True
        if stock_data.iloc[i]['sma_50'] > stock_data.iloc[i]['sma_200'] and \
           stock_data.iloc[i+1]['sma_50'] < stock_data.iloc[i+1]['sma_200']:
            death_cross = True
    
    # Trend determination
    trend = 'Sideways'
    trend_strength = 0
    
    # Strong uptrend: Price > SMA20 > SMA50 > SMA200
    if price > sma_20 > sma_50 > sma_200:
        trend = 'Strong Uptrend'
        trend_strength = 2
    # Uptrend: Price > SMA50 > SMA200
    elif price > sma_50 > sma_200:
        trend = 'Uptrend'
        trend_strength = 1
    # Strong downtrend: Price < SMA20 < SMA50 < SMA200
    elif price < sma_20 < sma_50 < sma_200:
        trend = 'Strong Downtrend'
        trend_strength = -2
    # Downtrend: Price < SMA50 < SMA200
    elif price < sma_50 < sma_200:
        trend = 'Downtrend'
        trend_strength = -1
    # Consolidation or potential reversal
    else:
        trend = 'Consolidating'
        trend_strength = 0
    
    # MACD analysis
    macd = latest['macd']
    macd_signal = latest['macd_signal']
    macd_hist = latest['macd_hist']
    
    macd_signal_strength = 0
    if macd > 0 and macd > macd_signal:
        macd_signal_strength = 2  # Bullish MACD
    elif macd > 0:
        macd_signal_strength = 1  # Weakly bullish
    elif macd < 0 and macd < macd_signal:
        macd_signal_strength = -2  # Bearish MACD
    elif macd < 0:
        macd_signal_strength = -1  # Weakly bearish
    
    # MACD crossover in last 5 days
    macd_crossover = None
    for i in range(-5, 0):
        if i+1 >= len(stock_data) or i >= len(stock_data):
            continue
        if stock_data.iloc[i]['macd'] < stock_data.iloc[i]['macd_signal'] and \
           stock_data.iloc[i+1]['macd'] > stock_data.iloc[i+1]['macd_signal']:
            macd_crossover = 'Bullish'
        if stock_data.iloc[i]['macd'] > stock_data.iloc[i]['macd_signal'] and \
           stock_data.iloc[i+1]['macd'] < stock_data.iloc[i+1]['macd_signal']:
            macd_crossover = 'Bearish'
    
    # RSI analysis
    rsi = latest['rsi']
    
    rsi_signal = 'Neutral'
    rsi_signal_strength = 0
    
    if rsi > 70:
        rsi_signal = 'Overbought'
        rsi_signal_strength = -1
    elif rsi > 65:
        rsi_signal = 'Approaching Overbought'
        rsi_signal_strength = -0.5
    elif rsi < 30:
        rsi_signal = 'Oversold'
        rsi_signal_strength = 1
    elif rsi < 35:
        rsi_signal = 'Approaching Oversold'
        rsi_signal_strength = 0.5
    
    # RSI divergence check (simplified)
    rsi_divergence = None
    # Check last 20 days for divergence
    price_highs = []
    rsi_highs = []
    price_lows = []
    rsi_lows = []
    
    for i in range(-20, 0):
        if i >= len(stock_data) or i+1 >= len(stock_data) or i-1 < 0 or i-1 >= len(stock_data):
            continue
        # Check for price highs
        if stock_data.iloc[i]['close'] > stock_data.iloc[i-1]['close'] and \
           stock_data.iloc[i]['close'] > stock_data.iloc[i+1]['close']:
            price_highs.append((i, stock_data.iloc[i]['close']))
        # Check for RSI highs
        if stock_data.iloc[i]['rsi'] > stock_data.iloc[i-1]['rsi'] and \
           stock_data.iloc[i]['rsi'] > stock_data.iloc[i+1]['rsi']:
            rsi_highs.append((i, stock_data.iloc[i]['rsi']))
        # Check for price lows
        if stock_data.iloc[i]['close'] < stock_data.iloc[i-1]['close'] and \
           stock_data.iloc[i]['close'] < stock_data.iloc[i+1]['close']:
            price_lows.append((i, stock_data.iloc[i]['close']))
        # Check for RSI lows
        if stock_data.iloc[i]['rsi'] < stock_data.iloc[i-1]['rsi'] and \
           stock_data.iloc[i]['rsi'] < stock_data.iloc[i+1]['rsi']:
            rsi_lows.append((i, stock_data.iloc[i]['rsi']))
    
    # Check for bullish divergence (price making lower lows, RSI making higher lows)
    if len(price_lows) >= 2 and len(rsi_lows) >= 2:
        if price_lows[-1][1] < price_lows[-2][1] and rsi_lows[-1][1] > rsi_lows[-2][1]:
            rsi_divergence = 'Bullish'
    
    # Check for bearish divergence (price making higher highs, RSI making lower highs)
    if len(price_highs) >= 2 and len(rsi_highs) >= 2:
        if price_highs[-1][1] > price_highs[-2][1] and rsi_highs[-1][1] < rsi_highs[-2][1]:
            rsi_divergence = 'Bearish'
    
    # Bollinger Bands analysis
    bb_high = latest['bollinger_high']
    bb_low = latest['bollinger_low']
    bb_mid = latest['bollinger_mid']
    
    bb_signal = 'Neutral'
    bb_signal_strength = 0
    
    # Price near upper band
    if price > bb_high * 0.98:
        bb_signal = 'Upper Band Test'
        bb_signal_strength = -0.5
    # Price above upper band
    elif price > bb_high:
        bb_signal = 'Overbought (BB)'
        bb_signal_strength = -1
    # Price near lower band
    elif price < bb_low * 1.02:
        bb_signal = 'Lower Band Test'
        bb_signal_strength = 0.5
    # Price below lower band
    elif price < bb_low:
        bb_signal = 'Oversold (BB)'
        bb_signal_strength = 1
    
    # ADX analysis for trend strength
    adx = latest['adx']
    pdi = latest['pdi']
    ndi = latest['ndi']
    
    adx_signal = 'Weak Trend'
    if adx > 25:
        if pdi > ndi:
            adx_signal = 'Strong Uptrend'
        else:
            adx_signal = 'Strong Downtrend'
    elif adx > 20:
        if pdi > ndi:
            adx_signal = 'Moderate Uptrend'
        else:
            adx_signal = 'Moderate Downtrend'
    
    # Calculate volatility
    volatility = latest.get('volatility_30d', stock_data['daily_return'].std())
    volatility_signal = 'Average'
    if volatility > stock_data['daily_return'].std() * 1.5:
        volatility_signal = 'High'
    elif volatility < stock_data['daily_return'].std() * 0.5:
        volatility_signal = 'Low'
    
    # Volume analysis
    recent_volume_avg = stock_data.iloc[-5:]['volume'].mean()
    longer_volume_avg = stock_data.iloc[-20:]['volume'].mean()
    volume_ratio = recent_volume_avg / longer_volume_avg if longer_volume_avg > 0 else 1
    
    volume_signal = 'Average'
    volume_signal_strength = 0
    
    if volume_ratio > 1.5:
        volume_signal = 'Increasing'
        volume_signal_strength = 0.5
    elif volume_ratio < 0.7:
        volume_signal = 'Decreasing'
        volume_signal_strength = -0.5
    
    # OBV (On Balance Volume) analysis
    recent_obv = stock_data.iloc[-1]['obv']
    previous_obv = stock_data.iloc[-10]['obv']
    obv_change = (recent_obv - previous_obv) / abs(previous_obv) if previous_obv != 0 else 0
    
    obv_signal = 'Neutral'
    if obv_change > 0.05:
        obv_signal = 'Accumulation'
    elif obv_change < -0.05:
        obv_signal = 'Distribution'
    
    # Money Flow Index analysis
    mfi = latest.get('mfi', 50)  # Default to neutral if MFI not available
    
    mfi_signal = 'Neutral'
    mfi_signal_strength = 0
    
    if mfi > 80:
        mfi_signal = 'Overbought (MFI)'
        mfi_signal_strength = -1
    elif mfi < 20:
        mfi_signal = 'Oversold (MFI)'
        mfi_signal_strength = 1
    
    # Calculate overall technical score
    tech_score = 0
    
    # Trend component (weight: 30%)
    tech_score += trend_strength * 0.3
    
    # MACD component (weight: 20%)
    tech_score += macd_signal_strength * 0.2
    
    # RSI component (weight: 15%)
    tech_score += rsi_signal_strength * 0.15
    
    # Bollinger Bands component (weight: 10%)
    tech_score += bb_signal_strength * 0.1
    
    # Volume component (weight: 10%)
    tech_score += volume_signal_strength * 0.1
    
    # MFI component (weight: 15%)
    tech_score += mfi_signal_strength * 0.15
    
    # Scale the score to range from -10 to 10
    tech_score = round(tech_score * 10, 1)
    
    # Determine overall technical outlook based on score
    if tech_score >= 7:
        overall_technical = 'Strong Buy'
    elif tech_score >= 3:
        overall_technical = 'Buy'
    elif tech_score >= -3:
        overall_technical = 'Neutral'
    elif tech_score >= -7:
        overall_technical = 'Sell'
    else:
        overall_technical = 'Strong Sell'
    
    return {
        'price': price,
        'trend': trend,
        'sma_20': sma_20,
        'sma_50': sma_50,
        'sma_200': sma_200,
        'golden_cross': golden_cross,
        'death_cross': death_cross,
        'macd': macd,
        'macd_signal': macd_signal,
        'macd_hist': macd_hist,
        'macd_crossover': macd_crossover,
        'rsi': rsi,
        'rsi_signal': rsi_signal,
        'rsi_divergence': rsi_divergence,
        'bollinger_high': bb_high,
        'bollinger_low': bb_low,
        'bollinger_mid': bb_mid,
        'bollinger_signal': bb_signal,
        'adx': adx,
        'adx_signal': adx_signal,
        'volatility': volatility,
        'volatility_signal': volatility_signal,
        'volume_signal': volume_signal,
        'obv_signal': obv_signal,
        'mfi': mfi,
        'mfi_signal': mfi_signal,
        'tech_score': tech_score,
        'overall_technical': overall_technical
    }


def analyze_fundamental_data(fundamental_data):
    """
    Analyzes fundamental data for a stock.
    
    Args:
        fundamental_data (dict): Dictionary with fundamental data
    
    Returns:
        dict: Analysis results for fundamental data
    """
    # Initialize result dictionary
    analysis = {
        'status': 'success',
        'valuation': {},
        'financial_health': {},
        'growth': {},
        'dividend': {},
        'comparison': {}
    }
    
    # Extract sector for industry comparisons
    sector = fundamental_data.get('sector', 'Unknown')
    industry_avg = get_industry_averages(sector)
    
    # Valuation metrics analysis
    pe_ratio = fundamental_data.get('pe_ratio')
    forward_pe = fundamental_data.get('forward_pe')
    peg_ratio = fundamental_data.get('peg_ratio')
    price_to_book = fundamental_data.get('price_to_book')
    
    # PE Ratio analysis
    if pe_ratio:
        pe_industry_avg = industry_avg.get('pe_ratio', 20)
        
        if pe_ratio < pe_industry_avg * 0.7:
            pe_analysis = 'Undervalued'
            pe_score = 1
        elif pe_ratio > pe_industry_avg * 1.3:
            pe_analysis = 'Overvalued'
            pe_score = -1
        else:
            pe_analysis = 'Fair Valued'
            pe_score = 0
        
        analysis['valuation']['pe_ratio'] = {
            'value': pe_ratio,
            'industry_avg': pe_industry_avg,
            'analysis': pe_analysis
        }
    else:
        pe_score = 0
    
    # Forward PE analysis
    if forward_pe:
        if pe_ratio and forward_pe < pe_ratio:
            forward_pe_analysis = 'Earnings Growth Expected'
            forward_pe_score = 1
        elif pe_ratio and forward_pe > pe_ratio:
            forward_pe_analysis = 'Earnings Decline Expected'
            forward_pe_score = -1
        else:
            forward_pe_analysis = 'Stable Earnings Expected'
            forward_pe_score = 0
        
        analysis['valuation']['forward_pe'] = {
            'value': forward_pe,
            'analysis': forward_pe_analysis
        }
    else:
        forward_pe_score = 0
    
    # PEG Ratio analysis
    if peg_ratio:
        if peg_ratio < 1:
            peg_analysis = 'Undervalued (Growth)'
            peg_score = 1
        elif peg_ratio > 2:
            peg_analysis = 'Overvalued (Growth)'
            peg_score = -1
        else:
            peg_analysis = 'Fair Valued (Growth)'
            peg_score = 0
        
        analysis['valuation']['peg_ratio'] = {
            'value': peg_ratio,
            'analysis': peg_analysis
        }
    else:
        peg_score = 0
    
    # Price-to-Book analysis
    if price_to_book:
        pb_industry_avg = industry_avg.get('price_to_book', 2.5)
        
        if price_to_book < pb_industry_avg * 0.7:
            pb_analysis = 'Trading Below Book Value'
            pb_score = 1
        elif price_to_book > pb_industry_avg * 1.3:
            pb_analysis = 'Premium to Book Value'
            pb_score = -1
        else:
            pb_analysis = 'Fair Book Value'
            pb_score = 0
        
        analysis['valuation']['price_to_book'] = {
            'value': price_to_book,
            'industry_avg': pb_industry_avg,
            'analysis': pb_analysis
        }
    else:
        pb_score = 0
    
    # Financial health metrics
    debt_to_equity = fundamental_data.get('debt_to_equity')
    return_on_equity = fundamental_data.get('return_on_equity')
    profit_margin = fundamental_data.get('profit_margin')
    free_cash_flow = fundamental_data.get('free_cash_flow')
    
    # Debt-to-Equity analysis
    if debt_to_equity is not None:
        de_industry_avg = industry_avg.get('debt_to_equity', 0.4)
        
        if debt_to_equity < de_industry_avg * 0.7:
            de_analysis = 'Low Debt'
            de_score = 1
        elif debt_to_equity > de_industry_avg * 1.3:
            de_analysis = 'High Debt'
            de_score = -1
        else:
            de_analysis = 'Average Debt'
            de_score = 0
        
        analysis['financial_health']['debt_to_equity'] = {
            'value': debt_to_equity,
            'industry_avg': de_industry_avg,
            'analysis': de_analysis
        }
    else:
        de_score = 0
    
    # Return on Equity analysis
    if return_on_equity is not None:
        roe_industry_avg = industry_avg.get('return_on_equity', 0.15)
        
        if return_on_equity > roe_industry_avg * 1.3:
            roe_analysis = 'Strong ROE'
            roe_score = 1
        elif return_on_equity < roe_industry_avg * 0.7:
            roe_analysis = 'Weak ROE'
            roe_score = -1
        else:
            roe_analysis = 'Average ROE'
            roe_score = 0
        
        analysis['financial_health']['return_on_equity'] = {
            'value': return_on_equity,
            'industry_avg': roe_industry_avg,
            'analysis': roe_analysis
        }
    else:
        roe_score = 0
    
    # Profit Margin analysis
    if profit_margin is not None:
        pm_industry_avg = industry_avg.get('profit_margin', 0.1)
        
        if profit_margin > pm_industry_avg * 1.3:
            pm_analysis = 'High Margins'
            pm_score = 1
        elif profit_margin < pm_industry_avg * 0.7:
            pm_analysis = 'Low Margins'
            pm_score = -1
        else:
            pm_analysis = 'Average Margins'
            pm_score = 0
        
        analysis['financial_health']['profit_margin'] = {
            'value': profit_margin,
            'industry_avg': pm_industry_avg,
            'analysis': pm_analysis
        }
    else:
        pm_score = 0
    
    # Free Cash Flow analysis
    if free_cash_flow is not None:
        if free_cash_flow > 0:
            fcf_analysis = 'Positive FCF'
            fcf_score = 1
        else:
            fcf_analysis = 'Negative FCF'
            fcf_score = -1
        
        analysis['financial_health']['free_cash_flow'] = {
            'value': free_cash_flow,
            'analysis': fcf_analysis
        }
    else:
        fcf_score = 0
    
    # Dividend analysis
    dividend_yield = fundamental_data.get('dividend_yield')
    
    if dividend_yield is not None:
        div_industry_avg = industry_avg.get('dividend_yield', 2.0)
        
        if dividend_yield > div_industry_avg * 1.3:
            div_analysis = 'High Yield'
            div_score = 1
        elif dividend_yield > 0 and dividend_yield < div_industry_avg * 0.7:
            div_analysis = 'Low Yield'
            div_score = 0
        elif dividend_yield == 0:
            div_analysis = 'No Dividend'
            div_score = 0  # Neutral, some investors prefer growth over dividends
        else:
            div_analysis = 'Average Yield'
            div_score = 0.5
        
        analysis['dividend']['dividend_yield'] = {
            'value': dividend_yield,
            'industry_avg': div_industry_avg,
            'analysis': div_analysis
        }
    else:
        div_score = 0
    
    # Market cap analysis (size)
    market_cap = fundamental_data.get('market_cap')
    
    if market_cap is not None:
        if market_cap > 200000000000:  # $200B
            size = 'Mega Cap'
        elif market_cap > 10000000000:  # $10B
            size = 'Large Cap'
        elif market_cap > 2000000000:  # $2B
            size = 'Mid Cap'
        elif market_cap > 300000000:  # $300M
            size = 'Small Cap'
        else:
            size = 'Micro Cap'
        
        analysis['valuation']['market_cap'] = {
            'value': market_cap,
            'category': size
        }
    
    # Beta analysis (volatility)
    beta = fundamental_data.get('beta')
    
    if beta is not None:
        if beta < 0.8:
            beta_analysis = 'Low Volatility'
        elif beta < 1.2:
            beta_analysis = 'Market-like Volatility'
        else:
            beta_analysis = 'High Volatility'
        
        analysis['financial_health']['beta'] = {
            'value': beta,
            'analysis': beta_analysis
        }
    
    # EPS analysis
    eps = fundamental_data.get('eps')
    
    if eps is not None:
        if eps <= 0:
            eps_analysis = 'Negative Earnings'
            eps_score = -1
        else:
            eps_analysis = 'Positive Earnings'
            eps_score = 1
        
        analysis['financial_health']['eps'] = {
            'value': eps,
            'analysis': eps_analysis
        }
    else:
        eps_score = 0
    
    # Overall fundamental score calculation
    # Valuation component (40%)
    valuation_score = (pe_score + forward_pe_score + peg_score + pb_score) / 4 * 0.4
    
    # Financial health component (40%)
    financial_health_score = (de_score + roe_score + pm_score + fcf_score + eps_score) / 5 * 0.4
    
    # Dividend component (20%)
    dividend_score = div_score * 0.2
    
    # Combined fundamental score
    fund_score = (valuation_score + financial_health_score + dividend_score) * 10
    fund_score = round(fund_score, 1)
    
    # Determine overall fundamental outlook
    if fund_score >= 7:
        overall_fundamental = 'Strong Buy'
    elif fund_score >= 3:
        overall_fundamental = 'Buy'
    elif fund_score >= -3:
        overall_fundamental = 'Neutral'
    elif fund_score >= -7:
        overall_fundamental = 'Sell'
    else:
        overall_fundamental = 'Strong Sell'
    
    return {
        'analysis': analysis,
        'overall_fundamental': overall_fundamental,
        'fund_score': fund_score
    }

def analyze_behavioral_sentiment(ticker):
    """
    Analyzes news sentiment and market behavior for a stock.
    
    Args:
        ticker (str): Stock ticker symbol
    
    Returns:
        dict: Behavioral sentiment analysis results
    """
    # In a production app, this would connect to a news API and sentiment analysis service
    # For demonstration purposes, we'll generate synthetic behavioral data
    import random
    from datetime import datetime, timedelta
    
    # Generate synthetic news sentiment
    sentiment_score = random.uniform(-1.0, 1.0)  # -1.0 (very negative) to 1.0 (very positive)
    
    # News count (with higher density for well-known stocks)
    is_major_stock = any(major in ticker for major in ['.NS', 'RELIANCE', 'TCS', 'INFY', 'HDFC'])
    news_count = random.randint(5, 25) if is_major_stock else random.randint(1, 10)
    
    # News sources
    sources = ["Economic Times", "Business Standard", "Mint", "Financial Express", 
               "Bloomberg", "Reuters", "CNBC", "MoneyControl"]
    
    # Generate sample news headlines
    headlines = []
    for _ in range(min(5, news_count)):
        sentiment = random.choice(["positive", "neutral", "negative"])
        
        if sentiment == "positive":
            headline_templates = [
                "{} reports stronger-than-expected quarterly results",
                "{} shares surge as analysts upgrade rating",
                "{} announces expansion plans in growing markets",
                "{} dividend increase indicates management confidence",
                "Analysts remain bullish on {} despite market volatility"
            ]
        elif sentiment == "neutral":
            headline_templates = [
                "{} quarterly results in line with expectations",
                "{} maintains market position despite competition",
                "Industry challenges may impact {} growth plans",
                "{} restructuring efforts ongoing, results mixed",
                "{} faces regulatory scrutiny but analysts remain cautious"
            ]
        else:  # negative
            headline_templates = [
                "{} disappoints with lower-than-expected earnings",
                "{} shares drop as key executive announces departure",
                "Analysts downgrade {} amid industry headwinds",
                "{} faces increasing competition in core markets",
                "{} dividend cut signals financial pressure"
            ]
            
        # Generate headline data
        stock_name = ticker.split('.')[0] if '.' in ticker else ticker
        headline = random.choice(headline_templates).format(stock_name)
        source = random.choice(sources)
        days_ago = random.randint(0, 14)
        date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        headlines.append({
            "headline": headline,
            "source": source,
            "date": date,
            "sentiment": sentiment
        })
    
    # Calculate fear and greed components
    fear_index = random.randint(20, 80)  # 0-100 scale, lower means more fear
    insider_trading = random.choice(["Neutral", "Buying", "Selling"])
    
    # Volatility relative to market
    relative_volatility = random.uniform(0.5, 2.0)
    
    # Social media mentions/sentiment
    social_media_buzz = random.randint(0, 100)  # 0-100 scale
    social_sentiment = random.uniform(-1.0, 1.0)  # -1.0 to 1.0
    
    # Calculate behavioral score (1-10 scale)
    base_score = 5.0
    
    # Sentiment contribution (-2 to +2)
    sentiment_contribution = sentiment_score * 2
    
    # Fear index contribution (-1.5 to +1.5) - higher fear means lower score
    fear_contribution = (fear_index - 50) / 50 * 1.5
    
    # Insider contribution (-1 to +1)
    insider_contribution = 1.0 if insider_trading == "Buying" else -1.0 if insider_trading == "Selling" else 0.0
    
    # Social contribution (-0.5 to +0.5)
    social_contribution = social_sentiment * 0.5
    
    # Calculate final score
    behavioral_score = base_score + sentiment_contribution + fear_contribution + insider_contribution + social_contribution
    
    # Ensure score is within 1-10 range
    behavioral_score = max(1.0, min(10.0, behavioral_score))
    
    # Determine sentiment signal
    if behavioral_score >= 7.5:
        sentiment_signal = "Very Bullish"
    elif behavioral_score >= 6.0:
        sentiment_signal = "Bullish"
    elif behavioral_score >= 4.0:
        sentiment_signal = "Neutral"
    elif behavioral_score >= 2.5:
        sentiment_signal = "Bearish"
    else:
        sentiment_signal = "Very Bearish"
    
    return {
        "behavioral_score": behavioral_score,
        "sentiment_signal": sentiment_signal,
        "news_sentiment": sentiment_score,
        "news_count": news_count,
        "headlines": headlines,
        "market_fear_index": fear_index,
        "insider_trading": insider_trading,
        "relative_volatility": relative_volatility,
        "social_media": {
            "buzz": social_media_buzz,
            "sentiment": social_sentiment
        }
    }

def perform_complete_analysis(ticker):
    """
    Performs a complete analysis of a stock including technical, fundamental, and behavioral.
    
    Args:
        ticker (str): Stock ticker symbol
    
    Returns:
        dict: Complete analysis results
    """
    # Get stock data
    stock_data = get_stock_data(ticker)
    if stock_data is None:
        return {
            'ticker': ticker,
            'error': 'Unable to fetch stock data',
            'status': 'error'
        }
    
    # Calculate technical indicators
    stock_data_with_indicators = calculate_technical_indicators(stock_data)
    
    # Get fundamental data
    fundamental_data = get_fundamental_data(ticker)
    
    # Analyze technical indicators
    technical_analysis = analyze_technical_indicators(stock_data_with_indicators)
    
    # Analyze fundamental data
    fundamental_analysis = analyze_fundamental_data(fundamental_data)
    
    # Get behavioral analysis (news sentiment, fear index, etc.)
    behavioral_analysis = analyze_behavioral_sentiment(ticker)
    
    # Combine the analyses
    analysis_results = {
        'ticker': ticker,
        'name': fundamental_data.get('name', ticker),
        'sector': fundamental_data.get('sector', 'N/A'),
        'current_price': stock_data['close'].iloc[-1] if len(stock_data) > 0 else None,
        'technical': technical_analysis,
        'fundamental': fundamental_analysis,
        'behavioral': behavioral_analysis,
        'data': stock_data_with_indicators,
        'status': 'success'
    }
    
    # Try to save the analysis results to the database
    try:
        from utils.db import save_analysis_result
        save_analysis_result(ticker, analysis_results)
    except Exception as e:
        print(f"Error saving analysis to database: {e}")
        # Continue even if database save fails
    
    return analysis_results