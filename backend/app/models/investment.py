from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base
from app.models.user import User

class AssetType(str, enum.Enum):
    STOCK = "stock"
    BOND = "bond"
    ETF = "etf"
    MUTUAL_FUND = "mutual_fund"
    CRYPTO = "crypto"
    REAL_ESTATE = "real_estate"
    COMMODITY = "commodity"
    CASH = "cash"

class TransactionType(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"
    DIVIDEND = "dividend"
    INTEREST = "interest"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="portfolios")
    holdings = relationship("Holding", back_populates="portfolio")
    transactions = relationship("InvestmentTransaction", back_populates="portfolio")

class Holding(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    asset_type = Column(Enum(AssetType), nullable=False)
    symbol = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    average_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=True)
    last_updated = Column(DateTime, nullable=True)
    metadata = Column(JSON, nullable=True)  # Store additional asset-specific data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")
    transactions = relationship("InvestmentTransaction", back_populates="holding")

    @property
    def market_value(self) -> float:
        return self.quantity * (self.current_price or self.average_price)

    @property
    def gain_loss(self) -> float:
        if not self.current_price:
            return 0
        return (self.current_price - self.average_price) * self.quantity

    @property
    def gain_loss_percentage(self) -> float:
        if not self.current_price or self.average_price == 0:
            return 0
        return ((self.current_price - self.average_price) / self.average_price) * 100

class InvestmentTransaction(Base):
    __tablename__ = "investment_transactions"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    holding_id = Column(Integer, ForeignKey("holdings.id"), nullable=True)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    symbol = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    fees = Column(Float, default=0)
    date = Column(DateTime, nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="transactions")
    holding = relationship("Holding", back_populates="transactions")

class PortfolioAlert(Base):
    __tablename__ = "portfolio_alerts"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    holding_id = Column(Integer, ForeignKey("holdings.id"), nullable=True)
    alert_type = Column(String, nullable=False)  # price_target, price_change, portfolio_change
    threshold = Column(Float, nullable=False)
    message = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    triggered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="alerts")
    holding = relationship("Holding", back_populates="alerts")

class PortfolioPerformance(Base):
    __tablename__ = "portfolio_performance"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    total_value = Column(Float, nullable=False)
    daily_return = Column(Float, nullable=True)
    total_return = Column(Float, nullable=True)
    cash_flow = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="performance_history")

# Update User model to include portfolio relationship
User.portfolios = relationship("Portfolio", back_populates="user")
