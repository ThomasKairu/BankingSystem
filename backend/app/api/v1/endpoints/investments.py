from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.services.investment_service import InvestmentService
from app.schemas.investment import (
    Portfolio, PortfolioCreate, PortfolioUpdate,
    Transaction, TransactionCreate,
    Alert, AlertCreate,
    PortfolioSummary, PerformanceHistory
)
from app.models.user import User

router = APIRouter()

@router.post("/portfolios", response_model=Portfolio)
def create_portfolio(
    portfolio_data: PortfolioCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new investment portfolio."""
    investment_service = InvestmentService(db)
    return investment_service.create_portfolio(current_user.id, portfolio_data)

@router.get("/portfolios", response_model=List[Portfolio])
def get_portfolios(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all portfolios for the current user."""
    investment_service = InvestmentService(db)
    return investment_service.get_user_portfolios(current_user.id)

@router.get("/portfolios/{portfolio_id}", response_model=Portfolio)
def get_portfolio(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific portfolio by ID."""
    investment_service = InvestmentService(db)
    return investment_service.get_portfolio(portfolio_id, current_user.id)

@router.post("/portfolios/{portfolio_id}/transactions", response_model=Transaction)
def add_transaction(
    portfolio_id: int,
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new investment transaction."""
    investment_service = InvestmentService(db)
    # Verify portfolio belongs to user
    investment_service.get_portfolio(portfolio_id, current_user.id)
    return investment_service.add_transaction(portfolio_id, transaction_data)

@router.post("/portfolios/{portfolio_id}/update-prices")
def update_prices(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current prices for all holdings in a portfolio."""
    investment_service = InvestmentService(db)
    # Verify portfolio belongs to user
    investment_service.get_portfolio(portfolio_id, current_user.id)
    investment_service.update_prices(portfolio_id)
    return {"message": "Prices updated successfully"}

@router.get("/portfolios/{portfolio_id}/summary", response_model=PortfolioSummary)
def get_portfolio_summary(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a summary of portfolio performance and allocation."""
    investment_service = InvestmentService(db)
    # Verify portfolio belongs to user
    investment_service.get_portfolio(portfolio_id, current_user.id)
    return investment_service.get_portfolio_summary(portfolio_id)

@router.get("/portfolios/{portfolio_id}/performance", response_model=List[PerformanceHistory])
def get_performance_history(
    portfolio_id: int,
    timeframe: str = Query("1Y", regex="^(1M|3M|6M|1Y)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get historical performance data for a portfolio."""
    investment_service = InvestmentService(db)
    # Verify portfolio belongs to user
    investment_service.get_portfolio(portfolio_id, current_user.id)
    return investment_service.get_performance_history(portfolio_id, timeframe)

@router.post("/portfolios/{portfolio_id}/alerts", response_model=Alert)
def create_alert(
    portfolio_id: int,
    alert_data: AlertCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new portfolio alert."""
    investment_service = InvestmentService(db)
    # Verify portfolio belongs to user
    investment_service.get_portfolio(portfolio_id, current_user.id)
    return investment_service.create_alert(portfolio_id, alert_data)
