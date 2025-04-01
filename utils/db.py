import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
from urllib.parse import quote_plus

# Provide a default SQLite database URL if DATABASE_URL is not set
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///default.db')

# Create database engine
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Define the models
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True)
    password_hash = Column(String(255))  # In a real app, store hashed passwords only
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    # Relationship
    portfolios = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(username='{self.username}')>"


class Portfolio(Base):
    __tablename__ = 'portfolios'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    # Relationships
    user = relationship("User", back_populates="portfolios")
    holdings = relationship("Holding", back_populates="portfolio", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Portfolio(name='{self.name}')>"


class Stock(Base):
    __tablename__ = 'stocks'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String(20), unique=True, nullable=False)
    name = Column(String(255))
    sector = Column(String(100))
    industry = Column(String(100))
    country = Column(String(50))
    exchange = Column(String(50))
    last_updated = Column(DateTime, default=datetime.datetime.now)
    
    # Relationships
    holdings = relationship("Holding", back_populates="stock")
    historical_data = relationship("StockHistoricalData", back_populates="stock", cascade="all, delete-orphan")
    fundamental_data = relationship("StockFundamentalData", back_populates="stock", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Stock(ticker='{self.ticker}', name='{self.name}')>"


class Holding(Base):
    __tablename__ = 'holdings'
    
    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'), nullable=False)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    quantity = Column(Float, nullable=False)
    buy_price = Column(Float, nullable=False)
    buy_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")
    stock = relationship("Stock", back_populates="holdings")
    
    def __repr__(self):
        return f"<Holding(stock_id={self.stock_id}, quantity={self.quantity})>"


class StockHistoricalData(Base):
    __tablename__ = 'stock_historical_data'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    
    # Relationships
    stock = relationship("Stock", back_populates="historical_data")
    
    def __repr__(self):
        return f"<StockHistoricalData(stock_id={self.stock_id}, date='{self.date}')>"


class StockFundamentalData(Base):
    __tablename__ = 'stock_fundamental_data'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    pe_ratio = Column(Float)
    forward_pe = Column(Float)
    peg_ratio = Column(Float)
    price_to_book = Column(Float)
    dividend_yield = Column(Float)
    eps = Column(Float)
    beta = Column(Float)
    market_cap = Column(Float)
    debt_to_equity = Column(Float)
    return_on_equity = Column(Float)
    profit_margin = Column(Float)
    free_cash_flow = Column(Float)
    
    # Relationships
    stock = relationship("Stock", back_populates="fundamental_data")
    
    def __repr__(self):
        return f"<StockFundamentalData(stock_id={self.stock_id}, date='{self.date}')>"


class AnalysisResult(Base):
    __tablename__ = 'analysis_results'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    analysis_type = Column(String(50))  # technical, fundamental, or combined
    recommendation = Column(String(20))  # Strong Buy, Buy, Hold, Reduce, Sell
    technical_score = Column(Float)
    fundamental_score = Column(Float)
    combined_score = Column(Float)
    reasoning = Column(Text)
    
    # Relationships
    stock = relationship("Stock")
    
    def __repr__(self):
        return f"<AnalysisResult(stock_id={self.stock_id}, date='{self.date}', recommendation='{self.recommendation}')>"


# Create the tables in the database
def init_db():
    Base.metadata.create_all(engine)


# Create a session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Helper function to get a database session
def get_db_session():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


# Initialize demo data
def init_demo_data():
    # Create the database session
    db = get_db_session()
    
    # Check if we already have demo data
    user_exists = db.query(User).filter_by(username='demo_user').first()
    if user_exists:
        db.close()
        return
    
    # Create demo user
    demo_user = User(
        username='demo_user',
        email='demo@example.com',
        password_hash='password'  # In a real app, this would be hashed
    )
    db.add(demo_user)
    db.commit()
    
    # Create demo portfolio
    demo_portfolio = Portfolio(
        user_id=demo_user.id,
        name='Demo Portfolio',
        description='A demonstration portfolio with Indian stocks'
    )
    db.add(demo_portfolio)
    db.commit()
    
    # Demo stock data
    demo_stocks = [
        {'ticker': 'RELIANCE.NS', 'name': 'Reliance Industries', 'sector': 'Energy', 'quantity': 10, 'buy_price': 2100},
        {'ticker': 'TCS.NS', 'name': 'Tata Consultancy Services', 'sector': 'Technology', 'quantity': 5, 'buy_price': 3200},
        {'ticker': 'INFY.NS', 'name': 'Infosys', 'sector': 'Technology', 'quantity': 15, 'buy_price': 1500},
        {'ticker': 'HDFCBANK.NS', 'name': 'HDFC Bank', 'sector': 'Financial Services', 'quantity': 8, 'buy_price': 1600},
        {'ticker': 'TATAMOTORS.NS', 'name': 'Tata Motors', 'sector': 'Consumer Cyclical', 'quantity': 20, 'buy_price': 400},
        {'ticker': 'SUNPHARMA.NS', 'name': 'Sun Pharmaceutical', 'sector': 'Healthcare', 'quantity': 12, 'buy_price': 800},
        {'ticker': 'BAJFINANCE.NS', 'name': 'Bajaj Finance', 'sector': 'Financial Services', 'quantity': 6, 'buy_price': 5500},
        {'ticker': 'WIPRO.NS', 'name': 'Wipro', 'sector': 'Technology', 'quantity': 18, 'buy_price': 450},
        {'ticker': 'ADANIPORTS.NS', 'name': 'Adani Ports', 'sector': 'Industrials', 'quantity': 7, 'buy_price': 700},
        {'ticker': 'AXISBANK.NS', 'name': 'Axis Bank', 'sector': 'Financial Services', 'quantity': 9, 'buy_price': 750}
    ]
    
    # Add stocks and holdings
    for stock_data in demo_stocks:
        # Check if stock already exists
        stock = db.query(Stock).filter_by(ticker=stock_data['ticker']).first()
        if not stock:
            stock = Stock(
                ticker=stock_data['ticker'],
                name=stock_data['name'],
                sector=stock_data['sector']
            )
            db.add(stock)
            db.commit()
        
        # Add holding
        holding = Holding(
            portfolio_id=demo_portfolio.id,
            stock_id=stock.id,
            quantity=stock_data['quantity'],
            buy_price=stock_data['buy_price'],
            buy_date=datetime.datetime.now() - datetime.timedelta(days=30)  # Bought 30 days ago
        )
        db.add(holding)
    
    db.commit()
    db.close()


# Function to get portfolio data from database
def get_portfolio_data_from_db(user_id=1, portfolio_id=1):
    """
    Fetches portfolio data from the database.
    
    Args:
        user_id (int): User ID
        portfolio_id (int): Portfolio ID
        
    Returns:
        dict: Portfolio data
    """
    db = get_db_session()
    
    try:
        # Get portfolio
        portfolio = db.query(Portfolio).filter_by(id=portfolio_id, user_id=user_id).first()
        if not portfolio:
            return None
        
        # Get holdings with stock info
        holdings_query = db.query(
            Holding, Stock
        ).join(
            Stock, Holding.stock_id == Stock.id
        ).filter(
            Holding.portfolio_id == portfolio_id
        ).all()
        
        holdings = []
        portfolio_value = 0
        investment_value = 0
        daily_change = 0
        
        for holding, stock in holdings_query:
            # Format the ticker for yfinance (remove the .NS if needed)
            yf_ticker = stock.ticker
            
            # This would fetch the current price from the database
            # For now, we'll calculate a synthetic current price based on buy price
            import random
            current_price = holding.buy_price * random.uniform(0.8, 1.2)
            
            # Calculate values
            current_value = current_price * holding.quantity
            investment_value_item = holding.buy_price * holding.quantity
            profit_loss = current_value - investment_value_item
            profit_loss_percent = (profit_loss / investment_value_item) * 100
            daily_change_percent = random.uniform(-2, 2)
            daily_change_value = current_value * (daily_change_percent / 100)
            
            # Add to totals
            portfolio_value += current_value
            investment_value += investment_value_item
            daily_change += daily_change_value
            
            # Create holding dict
            holding_dict = {
                'ticker': stock.ticker.replace('.NS', ''),
                'name': stock.name,
                'sector': stock.sector,
                'quantity': holding.quantity,
                'buy_price': holding.buy_price,
                'current_price': current_price,
                'current_value': current_value,
                'investment_value': investment_value_item,
                'profit_loss': profit_loss,
                'profit_loss_percent': profit_loss_percent,
                'daily_change': daily_change_percent,
                'daily_change_value': daily_change_value
            }
            
            holdings.append(holding_dict)
        
        # Calculate total P&L
        total_profit_loss = portfolio_value - investment_value
        total_profit_loss_percent = (total_profit_loss / investment_value) * 100 if investment_value else 0
        
        # Calculate sector allocation
        sector_allocation = {}
        for holding_dict in holdings:
            sector = holding_dict['sector']
            if sector in sector_allocation:
                sector_allocation[sector] += holding_dict['current_value']
            else:
                sector_allocation[sector] = holding_dict['current_value']
        
        # Convert to percentages
        sector_percentages = {sector: (value / portfolio_value) * 100 for sector, value in sector_allocation.items()}
        
        # Prepare return object
        portfolio_data = {
            'holdings': holdings,
            'portfolio_value': portfolio_value,
            'investment_value': investment_value,
            'profit_loss': total_profit_loss,
            'profit_loss_percent': total_profit_loss_percent,
            'daily_change': daily_change,
            'daily_change_percent': (daily_change / (portfolio_value - daily_change)) * 100 if abs(portfolio_value - daily_change) > 0.001 else 0,
            'sector_allocation': sector_percentages,
            'last_updated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return portfolio_data
    
    finally:
        db.close()


# Function to get stock data from database or insert if not exists
def get_or_create_stock(ticker):
    """
    Gets a stock from the database, or creates it if it doesn't exist.
    
    Args:
        ticker (str): Stock ticker symbol
        
    Returns:
        Stock: Stock object
    """
    db = get_db_session()
    
    try:
        # Format ticker for database (add .NS for Indian stocks)
        if not ticker.endswith(('.NS', '.BO')) and ticker not in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']:
            db_ticker = f"{ticker}.NS"
        else:
            db_ticker = ticker
        
        # Check if stock exists
        stock = db.query(Stock).filter_by(ticker=db_ticker).first()
        
        if not stock:
            # Create new stock
            stock = Stock(
                ticker=db_ticker,
                name=ticker  # Will be updated with actual name later
            )
            db.add(stock)
            db.commit()
            db.refresh(stock)
        
        return stock
    
    finally:
        db.close()


# Function to save analysis results to database
def save_analysis_result(ticker, analysis_results):
    """
    Saves analysis results to the database.
    
    Args:
        ticker (str): Stock ticker symbol
        analysis_results (dict): Analysis results
        
    Returns:
        bool: True if successful, False otherwise
    """
    if analysis_results.get('status') != 'success':
        return False
    
    db = get_db_session()
    
    try:
        # Get or create stock
        stock = get_or_create_stock(ticker)
        
        # Create analysis result
        analysis_result = AnalysisResult(
            stock_id=stock.id,
            date=datetime.datetime.now(),
            analysis_type='combined',
            recommendation=analysis_results.get('recommendation', 'Hold'),
            technical_score=analysis_results.get('technical_score', 0),
            fundamental_score=analysis_results.get('fundamental_score', 0),
            combined_score=analysis_results.get('combined_score', 0),
            reasoning=str(analysis_results.get('reasoning', ''))
        )
        
        db.add(analysis_result)
        db.commit()
        
        return True
    
    except Exception as e:
        print(f"Error saving analysis result: {e}")
        return False
    
    finally:
        db.close()


# Initialize the database
init_db()

# Initialize demo data
init_demo_data()