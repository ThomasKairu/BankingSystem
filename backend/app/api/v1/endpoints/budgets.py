from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from datetime import datetime
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.services.budget_service import BudgetService
from app.schemas.budget import (
    Budget, BudgetCreate, BudgetUpdate, BudgetExpenseCreate,
    BudgetExpense, BudgetAlert, BudgetSummary
)
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=Budget)
def create_budget(
    budget_data: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new budget."""
    budget_service = BudgetService(db)
    return budget_service.create_budget(current_user.id, budget_data)

@router.get("/", response_model=List[Budget])
def get_budgets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all budgets for the current user."""
    budget_service = BudgetService(db)
    return budget_service.get_user_budgets(current_user.id)

@router.get("/{budget_id}", response_model=Budget)
def get_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific budget by ID."""
    budget_service = BudgetService(db)
    return budget_service.get_budget(budget_id, current_user.id)

@router.put("/{budget_id}", response_model=Budget)
def update_budget(
    budget_id: int,
    budget_data: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a budget."""
    budget_service = BudgetService(db)
    return budget_service.update_budget(budget_id, current_user.id, budget_data)

@router.delete("/{budget_id}")
def delete_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a budget."""
    budget_service = BudgetService(db)
    budget_service.delete_budget(budget_id, current_user.id)
    return {"message": "Budget deleted successfully"}

@router.post("/{budget_id}/expenses", response_model=BudgetExpense)
def add_expense(
    budget_id: int,
    expense_data: BudgetExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add an expense to a budget."""
    budget_service = BudgetService(db)
    # Verify budget belongs to user
    budget_service.get_budget(budget_id, current_user.id)
    return budget_service.add_expense(budget_id, expense_data)

@router.get("/{budget_id}/summary", response_model=BudgetSummary)
def get_budget_summary(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a summary of budget spending and remaining amount."""
    budget_service = BudgetService(db)
    return budget_service.get_budget_summary(budget_id, current_user.id)

@router.get("/spending/categories")
def get_category_spending(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get spending breakdown by category."""
    budget_service = BudgetService(db)
    return budget_service.get_category_spending(current_user.id, start_date, end_date)

@router.get("/alerts", response_model=List[BudgetAlert])
def get_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all active budget alerts."""
    budget_service = BudgetService(db)
    return budget_service.get_active_alerts(current_user.id)

@router.post("/alerts/{alert_id}/dismiss")
def dismiss_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dismiss a budget alert."""
    budget_service = BudgetService(db)
    budget_service.dismiss_alert(alert_id, current_user.id)
    return {"message": "Alert dismissed successfully"}
