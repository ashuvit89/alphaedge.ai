import streamlit as st
import pandas as pd
from utils.db import get_db_session, Portfolio, Stock, Holding, User
import datetime

def show_portfolio_management():
    """
    Display the portfolio management page.
    """
    st.title("Portfolio Management")
    
    if not st.session_state.authenticated:
        st.warning("Please log in to manage your portfolios.")
        st.button("Go to Login", on_click=lambda: st.session_state.update({"_current_page": "Login"}))
        return
    
    # Get user information
    user_id = st.session_state.user_id if 'user_id' in st.session_state else 1
    
    # Create tabs for different actions
    tab1, tab2, tab3 = st.tabs(["My Portfolios", "Create Portfolio", "Add/Edit Holdings"])
    
    # Tab 1: List portfolios
    with tab1:
        show_portfolios(user_id)
    
    # Tab 2: Create portfolio
    with tab2:
        create_portfolio(user_id)
    
    # Tab 3: Add/Edit Holdings
    with tab3:
        manage_holdings(user_id)


def show_portfolios(user_id):
    """
    Show existing portfolios for the user.
    
    Args:
        user_id (int): User ID
    """
    st.subheader("My Portfolios")
    
    # Get portfolios from database
    db = get_db_session()
    try:
        portfolios = db.query(Portfolio).filter_by(user_id=user_id).all()
        
        if not portfolios:
            st.info("You don't have any portfolios yet. Create one in the 'Create Portfolio' tab.")
            return
        
        # Display portfolios
        for portfolio in portfolios:
            with st.expander(f"Portfolio: {portfolio.name}"):
                st.write(f"**Description:** {portfolio.description}")
                st.write(f"**Created:** {portfolio.created_at}")
                
                # Get holdings for this portfolio
                holdings = (
                    db.query(Holding, Stock)
                    .join(Stock, Holding.stock_id == Stock.id)
                    .filter(Holding.portfolio_id == portfolio.id)
                    .all()
                )
                
                if holdings:
                    holdings_data = []
                    for holding, stock in holdings:
                        holdings_data.append({
                            'Ticker': stock.ticker,
                            'Name': stock.name,
                            'Quantity': holding.quantity,
                            'Buy Price': f"₹{holding.buy_price:.2f}",
                            'Buy Date': holding.buy_date.strftime('%Y-%m-%d') if holding.buy_date else 'N/A'
                        })
                    
                    st.write("**Holdings:**")
                    st.dataframe(pd.DataFrame(holdings_data))
                else:
                    st.write("No holdings in this portfolio.")
                
                # Action buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Set as Active", key=f"activate_{portfolio.id}"):
                        st.session_state.active_portfolio_id = portfolio.id
                        st.success(f"Portfolio '{portfolio.name}' set as active.")
                        st.rerun()
                
                with col2:
                    if st.button("Delete Portfolio", key=f"delete_{portfolio.id}"):
                        # Delete portfolio (in a real app, add confirmation)
                        db.query(Holding).filter_by(portfolio_id=portfolio.id).delete()
                        db.query(Portfolio).filter_by(id=portfolio.id).delete()
                        db.commit()
                        st.success(f"Portfolio '{portfolio.name}' deleted.")
                        st.rerun()
    finally:
        db.close()


def create_portfolio(user_id):
    """
    Create a new portfolio.
    
    Args:
        user_id (int): User ID
    """
    st.subheader("Create New Portfolio")
    
    portfolio_name = st.text_input("Portfolio Name", key="new_portfolio_name")
    portfolio_description = st.text_area("Description", key="new_portfolio_desc")
    
    if st.button("Create Portfolio"):
        if not portfolio_name:
            st.error("Portfolio name is required.")
            return
        
        # Create portfolio in database
        db = get_db_session()
        try:
            new_portfolio = Portfolio(
                user_id=user_id,
                name=portfolio_name,
                description=portfolio_description
            )
            db.add(new_portfolio)
            db.commit()
            
            st.success(f"Portfolio '{portfolio_name}' created successfully!")
            # Clear form
            st.session_state.new_portfolio_name = ""
            st.session_state.new_portfolio_desc = ""
        except Exception as e:
            st.error(f"Error creating portfolio: {e}")
        finally:
            db.close()


def manage_holdings(user_id):
    """
    Add or edit holdings in a portfolio.
    
    Args:
        user_id (int): User ID
    """
    st.subheader("Manage Holdings")
    
    # Get user's portfolios
    db = get_db_session()
    try:
        portfolios = db.query(Portfolio).filter_by(user_id=user_id).all()
        
        if not portfolios:
            st.info("You need to create a portfolio first.")
            return
        
        # Select portfolio
        portfolio_options = {p.name: p.id for p in portfolios}
        selected_portfolio = st.selectbox(
            "Select Portfolio", 
            options=list(portfolio_options.keys())
        )
        
        portfolio_id = portfolio_options[selected_portfolio]
        
        # Add new holding section
        st.write("### Add New Holding")
        col1, col2 = st.columns(2)
        
        with col1:
            ticker = st.text_input("Stock Ticker (e.g., RELIANCE, TCS)", key="new_holding_ticker")
            stock_name = st.text_input("Company Name", key="new_holding_name")
            sector = st.selectbox("Sector", options=[
                "Technology", "Financial Services", "Energy", "Healthcare", 
                "Consumer Cyclical", "Industrials", "Consumer Defensive", 
                "Basic Materials", "Real Estate", "Utilities", "Communication Services"
            ], key="new_holding_sector")
        
        with col2:
            quantity = st.number_input("Quantity", min_value=0.01, step=0.01, key="new_holding_qty")
            buy_price = st.number_input("Buy Price (₹)", min_value=0.01, step=0.01, key="new_holding_price")
            buy_date = st.date_input("Buy Date", value=datetime.datetime.now(), key="new_holding_date")
        
        if st.button("Add Holding"):
            if not ticker or not stock_name or quantity <= 0 or buy_price <= 0:
                st.error("Please fill in all required fields.")
                return
            
            # Format ticker for database
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
                    name=stock_name,
                    sector=sector
                )
                db.add(stock)
                db.commit()
                db.refresh(stock)
            
            # Check if holding already exists
            existing_holding = (
                db.query(Holding)
                .filter_by(portfolio_id=portfolio_id, stock_id=stock.id)
                .first()
            )
            
            if existing_holding:
                # Update existing holding
                existing_holding.quantity += quantity
                existing_holding.buy_price = (
                    (existing_holding.quantity * existing_holding.buy_price + quantity * buy_price) /
                    (existing_holding.quantity + quantity)
                )
                existing_holding.updated_at = datetime.datetime.now()
                
                db.commit()
                st.success(f"Updated holding for {stock_name} in {selected_portfolio}.")
            else:
                # Create new holding
                holding = Holding(
                    portfolio_id=portfolio_id,
                    stock_id=stock.id,
                    quantity=quantity,
                    buy_price=buy_price,
                    buy_date=buy_date
                )
                db.add(holding)
                db.commit()
                st.success(f"Added {stock_name} to {selected_portfolio}.")
            
            # Clear form
            st.session_state.new_holding_ticker = ""
            st.session_state.new_holding_name = ""
            st.session_state.new_holding_qty = 0.01
            st.session_state.new_holding_price = 0.01
        
        # Existing holdings section
        st.write("### Existing Holdings")
        holdings = (
            db.query(Holding, Stock)
            .join(Stock, Holding.stock_id == Stock.id)
            .filter(Holding.portfolio_id == portfolio_id)
            .all()
        )
        
        if not holdings:
            st.info("No holdings in this portfolio yet.")
            return
        
        for holding, stock in holdings:
            with st.expander(f"{stock.name} ({stock.ticker})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_qty = st.number_input(
                        "Quantity", 
                        min_value=0.0, 
                        value=float(holding.quantity),
                        key=f"edit_qty_{holding.id}"
                    )
                
                with col2:
                    new_price = st.number_input(
                        "Buy Price (₹)",
                        min_value=0.0,
                        value=float(holding.buy_price),
                        key=f"edit_price_{holding.id}"
                    )
                
                update_col, delete_col = st.columns(2)
                
                with update_col:
                    if st.button("Update", key=f"update_{holding.id}"):
                        if new_qty <= 0:
                            st.error("Quantity must be greater than zero.")
                        else:
                            holding.quantity = new_qty
                            holding.buy_price = new_price
                            holding.updated_at = datetime.datetime.now()
                            db.commit()
                            st.success(f"Updated {stock.name} holding.")
                
                with delete_col:
                    if st.button("Delete", key=f"delete_holding_{holding.id}"):
                        db.delete(holding)
                        db.commit()
                        st.success(f"Deleted {stock.name} from portfolio.")
                        st.rerun()
    finally:
        db.close()