from typing import List, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
import yfinance as yf
import pandas as pd
import numpy as np
from app.models.investment import (
    Portfolio, Holding, InvestmentTransaction, PortfolioAlert,
    PortfolioPerformance, AssetType, TransactionType
)
from app.schemas.investment import (
    PortfolioCreate, PortfolioUpdate, HoldingCreate,
    TransactionCreate, AlertCreate
)
from app.core.exceptions import NotFoundException, ValidationError

class InvestmentService:
    def __init__(self, db: Session):
        self.db = db

    def create_portfolio(self, user_id: int, portfolio_data: PortfolioCreate) -> Portfolio:
        """Create a new investment portfolio."""
        portfolio = Portfolio(
            user_id=user_id,
            name=portfolio_data.name,
            description=portfolio_data.description
        )
        self.db.add(portfolio)
        self.db.commit()
        self.db.refresh(portfolio)
        return portfolio

    def get_portfolio(self, portfolio_id: int, user_id: int) -> Portfolio:
        """Get a specific portfolio by ID."""
        portfolio = self.db.query(Portfolio).filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user_id
        ).first()
        if not portfolio:
            raise NotFoundException("Portfolio not found")
        return portfolio

    def get_user_portfolios(self, user_id: int) -> List[Portfolio]:
        """Get all portfolios for a user."""
        return self.db.query(Portfolio).filter(Portfolio.user_id == user_id).all()

    def add_transaction(self, portfolio_id: int, transaction_data: TransactionCreate) -> InvestmentTransaction:
        """Add a new investment transaction and update holdings."""
        # Create transaction
        transaction = InvestmentTransaction(
            portfolio_id=portfolio_id,
            transaction_type=transaction_data.transaction_type,
            symbol=transaction_data.symbol,
            quantity=transaction_data.quantity,
            price=transaction_data.price,
            total_amount=transaction_data.quantity * transaction_data.price + (transaction_data.fees or 0),
            fees=transaction_data.fees,
            date=transaction_data.date or datetime.utcnow(),
            notes=transaction_data.notes
        )

        # Update or create holding
        holding = self.db.query(Holding).filter(
            Holding.portfolio_id == portfolio_id,
            Holding.symbol == transaction_data.symbol
        ).first()

        if transaction_data.transaction_type in [TransactionType.BUY, TransactionType.SELL]:
            if not holding and transaction_data.transaction_type == TransactionType.BUY:
                holding = Holding(
                    portfolio_id=portfolio_id,
                    asset_type=transaction_data.asset_type,
                    symbol=transaction_data.symbol,
                    quantity=transaction_data.quantity,
                    average_price=transaction_data.price,
                    current_price=transaction_data.price,
                    last_updated=datetime.utcnow()
                )
                self.db.add(holding)
            elif holding:
                if transaction_data.transaction_type == TransactionType.BUY:
                    # Update average price and quantity
                    total_cost = (holding.quantity * holding.average_price) + (transaction_data.quantity * transaction_data.price)
                    holding.quantity += transaction_data.quantity
                    holding.average_price = total_cost / holding.quantity
                else:  # SELL
                    holding.quantity -= transaction_data.quantity
                    if holding.quantity <= 0:
                        self.db.delete(holding)
                    
        transaction.holding_id = holding.id if holding else None
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        
        # Update portfolio performance
        self._update_portfolio_performance(portfolio_id)
        return transaction

    def update_prices(self, portfolio_id: int) -> None:
        """Update current prices for all holdings in a portfolio."""
        holdings = self.db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()
        
        for holding in holdings:
            if holding.asset_type in [AssetType.STOCK, AssetType.ETF]:
                try:
                    ticker = yf.Ticker(holding.symbol)
                    current_price = ticker.info.get('regularMarketPrice')
                    if current_price:
                        holding.current_price = current_price
                        holding.last_updated = datetime.utcnow()
                except Exception as e:
                    print(f"Error updating price for {holding.symbol}: {str(e)}")

        self.db.commit()
        self._update_portfolio_performance(portfolio_id)
        self._check_alerts(portfolio_id)

    def get_portfolio_summary(self, portfolio_id: int) -> Dict:
        """Get a summary of portfolio performance and allocation."""
        holdings = self.db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()
        
        total_value = sum(holding.market_value for holding in holdings)
        total_gain_loss = sum(holding.gain_loss for holding in holdings)
        
        # Calculate allocation by asset type
        allocation = {}
        for holding in holdings:
            if holding.asset_type not in allocation:
                allocation[holding.asset_type] = 0
            allocation[holding.asset_type] += holding.market_value
            
        # Convert to percentages
        if total_value > 0:
            allocation = {k: (v/total_value)*100 for k, v in allocation.items()}

        return {
            "total_value": total_value,
            "total_gain_loss": total_gain_loss,
            "gain_loss_percentage": (total_gain_loss / (total_value - total_gain_loss)) * 100 if total_value > total_gain_loss else 0,
            "allocation": allocation,
            "last_updated": max(holding.last_updated for holding in holdings) if holdings else None
        }

    def get_performance_history(self, portfolio_id: int, timeframe: str = "1Y") -> List[Dict]:
        """Get historical performance data for a portfolio."""
        end_date = datetime.utcnow()
        
        if timeframe == "1M":
            start_date = end_date - timedelta(days=30)
        elif timeframe == "3M":
            start_date = end_date - timedelta(days=90)
        elif timeframe == "6M":
            start_date = end_date - timedelta(days=180)
        elif timeframe == "1Y":
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=365)

        performance_data = self.db.query(PortfolioPerformance).filter(
            PortfolioPerformance.portfolio_id == portfolio_id,
            PortfolioPerformance.date >= start_date
        ).order_by(PortfolioPerformance.date).all()

        return [{
            "date": data.date,
            "total_value": data.total_value,
            "daily_return": data.daily_return,
            "total_return": data.total_return
        } for data in performance_data]

    def create_alert(self, portfolio_id: int, alert_data: AlertCreate) -> PortfolioAlert:
        """Create a new portfolio alert."""
        alert = PortfolioAlert(
            portfolio_id=portfolio_id,
            holding_id=alert_data.holding_id,
            alert_type=alert_data.alert_type,
            threshold=alert_data.threshold,
            message=alert_data.message
        )
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def _update_portfolio_performance(self, portfolio_id: int) -> None:
        """Update portfolio performance metrics."""
        holdings = self.db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()
        total_value = sum(holding.market_value for holding in holdings)
        
        # Get previous day's performance
        yesterday = datetime.utcnow().date() - timedelta(days=1)
        prev_performance = self.db.query(PortfolioPerformance).filter(
            PortfolioPerformance.portfolio_id == portfolio_id,
            PortfolioPerformance.date == yesterday
        ).first()

        # Calculate returns
        daily_return = None
        if prev_performance:
            daily_return = ((total_value - prev_performance.total_value) / prev_performance.total_value) * 100

        # Calculate total return
        initial_value = self.db.query(func.sum(InvestmentTransaction.total_amount)).filter(
            InvestmentTransaction.portfolio_id == portfolio_id,
            InvestmentTransaction.transaction_type.in_([TransactionType.DEPOSIT, TransactionType.WITHDRAWAL])
        ).scalar() or 0

        total_return = ((total_value - initial_value) / initial_value) * 100 if initial_value > 0 else 0

        # Save performance data
        performance = PortfolioPerformance(
            portfolio_id=portfolio_id,
            date=datetime.utcnow().date(),
            total_value=total_value,
            daily_return=daily_return,
            total_return=total_return
        )
        self.db.add(performance)
        self.db.commit()

    def _check_alerts(self, portfolio_id: int) -> None:
        """Check and trigger portfolio alerts."""
        alerts = self.db.query(PortfolioAlert).filter(
            PortfolioAlert.portfolio_id == portfolio_id,
            PortfolioAlert.is_active == True
        ).all()

        for alert in alerts:
            if alert.holding_id:
                holding = self.db.query(Holding).get(alert.holding_id)
                if not holding:
                    continue

                if alert.alert_type == "price_target" and holding.current_price:
                    if holding.current_price >= alert.threshold:
                        alert.triggered_at = datetime.utcnow()
                        alert.is_active = False

                elif alert.alert_type == "price_change" and holding.current_price:
                    price_change = ((holding.current_price - holding.average_price) / holding.average_price) * 100
                    if abs(price_change) >= alert.threshold:
                        alert.triggered_at = datetime.utcnow()
                        alert.is_active = False

            else:  # Portfolio-wide alert
                portfolio_value = self.get_portfolio_summary(portfolio_id)["total_value"]
                if alert.alert_type == "portfolio_change":
                    # Get previous day's value
                    yesterday = datetime.utcnow().date() - timedelta(days=1)
                    prev_performance = self.db.query(PortfolioPerformance).filter(
                        PortfolioPerformance.portfolio_id == portfolio_id,
                        PortfolioPerformance.date == yesterday
                    ).first()

                    if prev_performance:
                        change = ((portfolio_value - prev_performance.total_value) / prev_performance.total_value) * 100
                        if abs(change) >= alert.threshold:
                            alert.triggered_at = datetime.utcnow()
                            alert.is_active = False

        self.db.commit()
