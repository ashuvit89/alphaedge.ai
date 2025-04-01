import pandas as pd
import yfinance as yf
import pandas_datareader as pdr
from datetime import datetime, timedelta
import ta
from ta.trend import ADXIndicator, SMAIndicator, EMAIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volume import OnBalanceVolumeIndicator, MFIIndicator
from ta.volatility import BollingerBands
import json
import os


def get_stock_data(ticker, period='1y'):
    """
    Fetches stock data for a given ticker and period.
    
    Args:
        ticker (str): Stock ticker symbol
        period (str): Period for data fetching (default: '1y')
    
    Returns:
        pandas.DataFrame: Historical stock data
    """
    try:
        # Add .NS suffix for Indian stocks if not already present
        if not ticker.endswith(('.NS', '.BO')) and ticker not in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']:
            ticker = f"{ticker}.NS"
        
        # Fetch data from Yahoo Finance
        stock = yf.Ticker(ticker)
        hist_data = stock.history(period=period)
        
        # Check if data is available
        if hist_data.empty:
            print(f"No data available for {ticker}")
            return None
        
        # Reset index to make date a column
        hist_data = hist_data.reset_index()
        
        # Ensure column names are consistent
        hist_data.columns = [col if col != 'Date' else 'date' for col in hist_data.columns]
        hist_data.columns = [col if col != 'Open' else 'open' for col in hist_data.columns]
        hist_data.columns = [col if col != 'High' else 'high' for col in hist_data.columns]
        hist_data.columns = [col if col != 'Low' else 'low' for col in hist_data.columns]
        hist_data.columns = [col if col != 'Close' else 'close' for col in hist_data.columns]
        hist_data.columns = [col if col != 'Volume' else 'volume' for col in hist_data.columns]
        
        return hist_data
    
    except Exception as e:
        print(f"Error fetching stock data for {ticker}: {e}")
        return None


def calculate_technical_indicators(df):
    """
    Calculates technical indicators for a given dataframe.
    
    Args:
        df (pandas.DataFrame): DataFrame with stock price data
    
    Returns:
        pandas.DataFrame: DataFrame with added technical indicators
    """
    try:
        # Make a copy to avoid modifying the original
        df_with_indicators = df.copy()
        
        # Check if dataframe is empty
        if df_with_indicators.empty:
            return df_with_indicators
        
        # Ensure we have the necessary columns
        required_cols = ['close', 'high', 'low', 'volume']
        for col in required_cols:
            if col not in df_with_indicators.columns:
                print(f"Missing required column: {col}")
                return df
        
        # Moving Averages
        df_with_indicators['sma_20'] = SMAIndicator(close=df_with_indicators['close'], window=20).sma_indicator()
        df_with_indicators['sma_50'] = SMAIndicator(close=df_with_indicators['close'], window=50).sma_indicator()
        df_with_indicators['sma_200'] = SMAIndicator(close=df_with_indicators['close'], window=200).sma_indicator()
        
        df_with_indicators['ema_12'] = EMAIndicator(close=df_with_indicators['close'], window=12).ema_indicator()
        df_with_indicators['ema_26'] = EMAIndicator(close=df_with_indicators['close'], window=26).ema_indicator()
        
        # MACD (calculated from EMAs)
        df_with_indicators['macd'] = df_with_indicators['ema_12'] - df_with_indicators['ema_26']
        df_with_indicators['macd_signal'] = EMAIndicator(close=df_with_indicators['macd'], window=9).ema_indicator()
        df_with_indicators['macd_hist'] = df_with_indicators['macd'] - df_with_indicators['macd_signal']
        
        # RSI
        rsi = RSIIndicator(close=df_with_indicators['close'], window=14)
        df_with_indicators['rsi'] = rsi.rsi()
        
        # Stochastic Oscillator
        stoch = StochasticOscillator(
            high=df_with_indicators['high'],
            low=df_with_indicators['low'],
            close=df_with_indicators['close'],
            window=14,
            smooth_window=3
        )
        df_with_indicators['stoch_k'] = stoch.stoch()
        df_with_indicators['stoch_d'] = stoch.stoch_signal()
        
        # ADX
        adx = ADXIndicator(
            high=df_with_indicators['high'],
            low=df_with_indicators['low'],
            close=df_with_indicators['close'],
            window=14
        )
        df_with_indicators['adx'] = adx.adx()
        df_with_indicators['pdi'] = adx.adx_pos()
        df_with_indicators['ndi'] = adx.adx_neg()
        
        # Bollinger Bands
        bollinger = BollingerBands(close=df_with_indicators['close'], window=20, window_dev=2)
        df_with_indicators['bollinger_high'] = bollinger.bollinger_hband()
        df_with_indicators['bollinger_low'] = bollinger.bollinger_lband()
        df_with_indicators['bollinger_mid'] = bollinger.bollinger_mavg()
        
        # Volume Indicators
        df_with_indicators['obv'] = OnBalanceVolumeIndicator(
            close=df_with_indicators['close'],
            volume=df_with_indicators['volume']
        ).on_balance_volume()
        
        try:
            df_with_indicators['mfi'] = MFIIndicator(
                high=df_with_indicators['high'],
                low=df_with_indicators['low'],
                close=df_with_indicators['close'],
                volume=df_with_indicators['volume'],
                window=14
            ).money_flow_index()
        except:
            # MFI can fail if there are zeros in volume
            df_with_indicators['mfi'] = None
        
        # Add daily returns
        df_with_indicators['daily_return'] = df_with_indicators['close'].pct_change() * 100
        
        # Add daily volatility (rolling standard deviation of returns)
        df_with_indicators['volatility_30d'] = df_with_indicators['daily_return'].rolling(window=30).std()
        
        return df_with_indicators
    
    except Exception as e:
        print(f"Error calculating technical indicators: {e}")
        return df


def get_fundamental_data(ticker):
    """
    Fetches fundamental data for a given ticker.
    
    Args:
        ticker (str): Stock ticker symbol
    
    Returns:
        dict: Fundamental metrics for the stock
    """
    try:
        # Add .NS suffix for Indian stocks if not already present
        if not ticker.endswith(('.NS', '.BO')) and ticker not in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']:
            yf_ticker = f"{ticker}.NS"
        else:
            yf_ticker = ticker
        
        # Fetch data from Yahoo Finance
        stock = yf.Ticker(yf_ticker)
        
        # Get basic info
        try:
            info = stock.info
        except:
            info = {}
        
        # Get financials
        try:
            financials = stock.financials
            if not isinstance(financials, pd.DataFrame) or financials.empty:
                financials = pd.DataFrame()
        except:
            financials = pd.DataFrame()
        
        # Get balance sheet
        try:
            balance_sheet = stock.balance_sheet
            if not isinstance(balance_sheet, pd.DataFrame) or balance_sheet.empty:
                balance_sheet = pd.DataFrame()
        except:
            balance_sheet = pd.DataFrame()
        
        # Get cash flow
        try:
            cash_flow = stock.cashflow
            if not isinstance(cash_flow, pd.DataFrame) or cash_flow.empty:
                cash_flow = pd.DataFrame()
        except:
            cash_flow = pd.DataFrame()
        
        # Extract fundamental metrics of interest
        fundamental_data = {
            'ticker': ticker,
            'name': info.get('shortName', ticker),
            'sector': info.get('sector', 'Unknown'),
            'industry': info.get('industry', 'Unknown'),
            'market_cap': info.get('marketCap', None),
            'pe_ratio': info.get('trailingPE', None),
            'forward_pe': info.get('forwardPE', None),
            'peg_ratio': info.get('pegRatio', None),
            'price_to_book': info.get('priceToBook', None),
            'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
            'eps': info.get('trailingEps', None),
            'beta': info.get('beta', None),
            'debt_to_equity': None,  # Will calculate if data available
            'return_on_equity': None,  # Will calculate if data available
            'profit_margin': info.get('profitMargin', None),
            'free_cash_flow': None,  # Will calculate if data available
            'analyst_recommendations': stock.recommendations
        }
        
        # Calculate additional metrics if data is available
        if not balance_sheet.empty and 'Total Debt' in balance_sheet.index and 'Total Stockholder Equity' in balance_sheet.index:
            latest_bs = balance_sheet.columns[0]  # Most recent period
            total_debt = balance_sheet.loc['Total Debt', latest_bs]
            total_equity = balance_sheet.loc['Total Stockholder Equity', latest_bs]
            
            if total_equity and total_equity != 0:
                fundamental_data['debt_to_equity'] = total_debt / total_equity
        
        if not financials.empty and 'Net Income' in financials.index and not balance_sheet.empty and 'Total Stockholder Equity' in balance_sheet.index:
            latest_fin = financials.columns[0]  # Most recent period
            latest_bs = balance_sheet.columns[0]  # Most recent period
            net_income = financials.loc['Net Income', latest_fin]
            total_equity = balance_sheet.loc['Total Stockholder Equity', latest_bs]
            
            if total_equity and total_equity != 0:
                fundamental_data['return_on_equity'] = net_income / total_equity
        
        if not cash_flow.empty and 'Free Cash Flow' in cash_flow.index:
            latest_cf = cash_flow.columns[0]  # Most recent period
            fundamental_data['free_cash_flow'] = cash_flow.loc['Free Cash Flow', latest_cf]
        
        return fundamental_data
    
    except Exception as e:
        print(f"Error fetching fundamental data for {ticker}: {e}")
        return {
            'ticker': ticker,
            'name': ticker,
            'sector': 'Unknown',
            'industry': 'Unknown'
        }


# Create a directory for caching stock lists
os.makedirs('cache', exist_ok=True)
STOCK_LIST_CACHE = 'cache/stock_list.json'
CACHE_EXPIRY = 24 * 60 * 60  # 24 hours in seconds

def get_stock_list():
    """
    Get a comprehensive list of Indian stocks (BSE and NSE).
    Returns cached data if available and recent, otherwise fetches new data.
    
    Returns:
        list: List of dictionaries with stock information
    """
    # Check if we have a cached list and if it's fresh (less than 24 hours old)
    if os.path.exists(STOCK_LIST_CACHE):
        try:
            modified_time = os.path.getmtime(STOCK_LIST_CACHE)
            if datetime.now().timestamp() - modified_time < CACHE_EXPIRY:
                with open(STOCK_LIST_CACHE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error reading cache: {e}")
    
    # Comprehensive list of popular Indian stocks (we'll add more dynamically later)
    indian_stocks = [
        {"ticker": "RELIANCE.NS", "name": "Reliance Industries Ltd.", "exchange": "NSE"},
        {"ticker": "TCS.NS", "name": "Tata Consultancy Services Ltd.", "exchange": "NSE"},
        {"ticker": "INFY.NS", "name": "Infosys Ltd.", "exchange": "NSE"},
        {"ticker": "HDFCBANK.NS", "name": "HDFC Bank Ltd.", "exchange": "NSE"},
        {"ticker": "HINDUNILVR.NS", "name": "Hindustan Unilever Ltd.", "exchange": "NSE"},
        {"ticker": "ICICIBANK.NS", "name": "ICICI Bank Ltd.", "exchange": "NSE"},
        {"ticker": "SBIN.NS", "name": "State Bank of India", "exchange": "NSE"},
        {"ticker": "BHARTIARTL.NS", "name": "Bharti Airtel Ltd.", "exchange": "NSE"},
        {"ticker": "BAJFINANCE.NS", "name": "Bajaj Finance Ltd.", "exchange": "NSE"},
        {"ticker": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank Ltd.", "exchange": "NSE"},
        {"ticker": "WIPRO.NS", "name": "Wipro Ltd.", "exchange": "NSE"},
        {"ticker": "ADANIPORTS.NS", "name": "Adani Ports and Special Economic Zone Ltd.", "exchange": "NSE"},
        {"ticker": "AXISBANK.NS", "name": "Axis Bank Ltd.", "exchange": "NSE"},
        {"ticker": "ASIANPAINT.NS", "name": "Asian Paints Ltd.", "exchange": "NSE"},
        {"ticker": "MARUTI.NS", "name": "Maruti Suzuki India Ltd.", "exchange": "NSE"},
        {"ticker": "ITC.NS", "name": "ITC Ltd.", "exchange": "NSE"},
        {"ticker": "TATASTEEL.NS", "name": "Tata Steel Ltd.", "exchange": "NSE"},
        {"ticker": "SUNPHARMA.NS", "name": "Sun Pharmaceutical Industries Ltd.", "exchange": "NSE"},
        {"ticker": "TATAMOTORS.NS", "name": "Tata Motors Ltd.", "exchange": "NSE"},
        {"ticker": "NTPC.NS", "name": "NTPC Ltd.", "exchange": "NSE"},
        {"ticker": "ULTRACEMCO.NS", "name": "UltraTech Cement Ltd.", "exchange": "NSE"},
        {"ticker": "LT.NS", "name": "Larsen & Toubro Ltd.", "exchange": "NSE"},
        {"ticker": "HCLTECH.NS", "name": "HCL Technologies Ltd.", "exchange": "NSE"},
        {"ticker": "TITAN.NS", "name": "Titan Company Ltd.", "exchange": "NSE"},
        {"ticker": "POWERGRID.NS", "name": "Power Grid Corporation of India Ltd.", "exchange": "NSE"},
        # BSE equivalents
        {"ticker": "RELIANCE.BO", "name": "Reliance Industries Ltd.", "exchange": "BSE"},
        {"ticker": "TCS.BO", "name": "Tata Consultancy Services Ltd.", "exchange": "BSE"},
        {"ticker": "INFY.BO", "name": "Infosys Ltd.", "exchange": "BSE"},
        {"ticker": "HDFCBANK.BO", "name": "HDFC Bank Ltd.", "exchange": "BSE"},
        {"ticker": "HINDUNILVR.BO", "name": "Hindustan Unilever Ltd.", "exchange": "BSE"},
        {"ticker": "ICICIBANK.BO", "name": "ICICI Bank Ltd.", "exchange": "BSE"},
        {"ticker": "SBIN.BO", "name": "State Bank of India", "exchange": "BSE"},
        # Additional popular stocks
        {"ticker": "BAJAJFINSV.NS", "name": "Bajaj Finserv Ltd.", "exchange": "NSE"},
        {"ticker": "DIVISLAB.NS", "name": "Divi's Laboratories Ltd.", "exchange": "NSE"},
        {"ticker": "DRREDDY.NS", "name": "Dr. Reddy's Laboratories Ltd.", "exchange": "NSE"},
        {"ticker": "EICHERMOT.NS", "name": "Eicher Motors Ltd.", "exchange": "NSE"},
        {"ticker": "GRASIM.NS", "name": "Grasim Industries Ltd.", "exchange": "NSE"},
        {"ticker": "INDUSINDBK.NS", "name": "IndusInd Bank Ltd.", "exchange": "NSE"},
        {"ticker": "JSWSTEEL.NS", "name": "JSW Steel Ltd.", "exchange": "NSE"},
        {"ticker": "M&M.NS", "name": "Mahindra & Mahindra Ltd.", "exchange": "NSE"},
        {"ticker": "NESTLEIND.NS", "name": "Nestle India Ltd.", "exchange": "NSE"},
        {"ticker": "ONGC.NS", "name": "Oil and Natural Gas Corporation Ltd.", "exchange": "NSE"},
        {"ticker": "SHREECEM.NS", "name": "Shree Cement Ltd.", "exchange": "NSE"},
        {"ticker": "TATACONSUM.NS", "name": "Tata Consumer Products Ltd.", "exchange": "NSE"},
        {"ticker": "TECHM.NS", "name": "Tech Mahindra Ltd.", "exchange": "NSE"},
        {"ticker": "UPL.NS", "name": "UPL Ltd.", "exchange": "NSE"},
        {"ticker": "BPCL.NS", "name": "Bharat Petroleum Corporation Ltd.", "exchange": "NSE"},
        {"ticker": "BRITANNIA.NS", "name": "Britannia Industries Ltd.", "exchange": "NSE"},
        {"ticker": "CIPLA.NS", "name": "Cipla Ltd.", "exchange": "NSE"},
        {"ticker": "COALINDIA.NS", "name": "Coal India Ltd.", "exchange": "NSE"},
        {"ticker": "HEROMOTOCO.NS", "name": "Hero MotoCorp Ltd.", "exchange": "NSE"},
        {"ticker": "HINDALCO.NS", "name": "Hindalco Industries Ltd.", "exchange": "NSE"},
    ]
    
    # Save to cache
    try:
        with open(STOCK_LIST_CACHE, 'w') as f:
            json.dump(indian_stocks, f)
    except Exception as e:
        print(f"Error saving stock list to cache: {e}")
    
    return indian_stocks

def search_stocks(query):
    """
    Search for stocks based on query text.
    
    Args:
        query (str): Search query for stock name or ticker
    
    Returns:
        list: Filtered list of matching stocks
    """
    if not query or len(query) < 2:
        return []
    
    stocks = get_stock_list()
    query = query.lower()
    
    # First, find exact ticker matches (highest priority)
    exact_ticker_matches = [s for s in stocks if query.upper() == s["ticker"].split('.')[0]]
    if exact_ticker_matches:
        return exact_ticker_matches
    
    # Find stocks that start with the query (higher priority)
    starts_with_matches = [s for s in stocks if 
                          s["ticker"].lower().startswith(query) or 
                          s["name"].lower().startswith(query)]
    
    # Find stocks that contain the query somewhere
    contains_matches = [s for s in stocks if 
                       (query in s["ticker"].lower() or 
                       query in s["name"].lower()) and
                       s not in starts_with_matches]
    
    # Return results ordered by relevance
    return starts_with_matches + contains_matches[:10]  # Limit to top 10 results

def get_industry_averages(sector):
    """
    Returns industry average metrics for a given sector.
    This is a simplified version - in a real implementation,
    this would fetch actual industry averages from a database or API.
    
    Args:
        sector (str): Industry sector
    
    Returns:
        dict: Industry average metrics
    """
    # Default values if sector isn't found
    default_metrics = {
        'pe_ratio': 20.0,
        'price_to_book': 2.5,
        'dividend_yield': 2.0,
        'debt_to_equity': 0.4,
        'return_on_equity': 0.15,
        'profit_margin': 0.1
    }
    
    # Industry averages by sector
    industry_metrics = {
        'Technology': {
            'pe_ratio': 25.0,
            'price_to_book': 5.0,
            'dividend_yield': 1.0,
            'debt_to_equity': 0.2,
            'return_on_equity': 0.22,
            'profit_margin': 0.15
        },
        'Financial Services': {
            'pe_ratio': 15.0,
            'price_to_book': 1.2,
            'dividend_yield': 3.5,
            'debt_to_equity': 0.6,
            'return_on_equity': 0.12,
            'profit_margin': 0.2
        },
        'Energy': {
            'pe_ratio': 12.0,
            'price_to_book': 1.5,
            'dividend_yield': 4.0,
            'debt_to_equity': 0.45,
            'return_on_equity': 0.1,
            'profit_margin': 0.08
        },
        'Healthcare': {
            'pe_ratio': 22.0,
            'price_to_book': 4.0,
            'dividend_yield': 1.5,
            'debt_to_equity': 0.25,
            'return_on_equity': 0.18,
            'profit_margin': 0.12
        },
        'Consumer Cyclical': {
            'pe_ratio': 18.0,
            'price_to_book': 3.0,
            'dividend_yield': 2.0,
            'debt_to_equity': 0.35,
            'return_on_equity': 0.16,
            'profit_margin': 0.09
        },
        'Industrials': {
            'pe_ratio': 20.0,
            'price_to_book': 2.8,
            'dividend_yield': 2.2,
            'debt_to_equity': 0.4,
            'return_on_equity': 0.14,
            'profit_margin': 0.08
        }
    }
    
    return industry_metrics.get(sector, default_metrics)