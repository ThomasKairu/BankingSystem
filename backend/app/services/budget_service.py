from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.budget import Budget, BudgetExpense, BudgetAlert, BudgetCategory, BudgetPeriod, AlertType, AlertStatus
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetExpenseCreate
from app.services.transaction_service import TransactionService
from app.core.exceptions import NotFoundException, ValidationError

class BudgetService:
    def __init__(self, db: Session):
        self.db = db
        self.transaction_service = TransactionService(db)

    def create_budget(self, user_id: int, budget_data: BudgetCreate) -> Budget:
        """Create a new budget for a user."""
        budget = Budget(
            user_id=user_id,
            name=budget_data.name,
            category=budget_data.category,
            amount=budget_data.amount,
            period=budget_data.period,
            start_date=budget_data.start_date,
            end_date=budget_data.end_date
        )
        self.db.add(budget)
        self.db.commit()
        self.db.refresh(budget)
        return budget

    def get_budget(self, budget_id: int, user_id: int) -> Budget:
        """Get a specific budget by ID."""
        budget = self.db.query(Budget).filter(
            Budget.id == budget_id,
            Budget.user_id == user_id
        ).first()
        if not budget:
            raise NotFoundException("Budget not found")
        return budget

    def get_user_budgets(self, user_id: int) -> List[Budget]:
        """Get all budgets for a user."""
        return self.db.query(Budget).filter(Budget.user_id == user_id).all()

    def update_budget(self, budget_id: int, user_id: int, budget_data: BudgetUpdate) -> Budget:
        """Update an existing budget."""
        budget = self.get_budget(budget_id, user_id)
        for field, value in budget_data.dict(exclude_unset=True).items():
            setattr(budget, field, value)
        self.db.commit()
        self.db.refresh(budget)
        return budget

    def delete_budget(self, budget_id: int, user_id: int) -> None:
        """Delete a budget."""
        budget = self.get_budget(budget_id, user_id)
        self.db.delete(budget)
        self.db.commit()

    def add_expense(self, budget_id: int, expense_data: BudgetExpenseCreate) -> BudgetExpense:
        """Add an expense to a budget."""
        expense = BudgetExpense(
            budget_id=budget_id,
            transaction_id=expense_data.transaction_id,
            amount=expense_data.amount,
            description=expense_data.description,
            date=expense_data.date or datetime.utcnow()
        )
        self.db.add(expense)
        self.db.commit()
        self.db.refresh(expense)
        
        # Check if budget alerts need to be created
        self._check_and_create_alerts(budget_id)
        return expense

    def get_budget_summary(self, budget_id: int, user_id: int) -> dict:
        """Get a summary of budget spending and remaining amount."""
        budget = self.get_budget(budget_id, user_id)
        total_spent = sum(expense.amount for expense in budget.expenses)
        remaining = budget.amount - total_spent
        percentage_used = (total_spent / budget.amount) * 100 if budget.amount > 0 else 0

        return {
            "budget_id": budget_id,
            "total_budget": budget.amount,
            "total_spent": total_spent,
            "remaining": remaining,
            "percentage_used": percentage_used,
            "period": budget.period,
            "category": budget.category
        }

    def get_category_spending(self, user_id: int, start_date: datetime, end_date: datetime) -> dict:
        """Get spending breakdown by category."""
        budgets = self.get_user_budgets(user_id)
        category_spending = {}
        
        for budget in budgets:
            expenses = self.db.query(BudgetExpense).filter(
                BudgetExpense.budget_id == budget.id,
                BudgetExpense.date >= start_date,
                BudgetExpense.date <= end_date
            ).all()
            
            category_spending[budget.category] = {
                "total_spent": sum(expense.amount for expense in expenses),
                "budget_amount": budget.amount
            }
        
        return category_spending

    def _check_and_create_alerts(self, budget_id: int) -> None:
        """Check and create budget alerts based on spending patterns."""
        budget = self.db.query(Budget).get(budget_id)
        if not budget:
            return

        total_spent = sum(expense.amount for expense in budget.expenses)
        percentage_used = (total_spent / budget.amount) * 100 if budget.amount > 0 else 0

        # Check for approaching limit (80% of budget)
        if percentage_used >= 80 and percentage_used < 100:
            self._create_alert(
                budget_id,
                AlertType.APPROACHING_LIMIT,
                f"You have used {percentage_used:.1f}% of your {budget.category} budget",
                percentage_used
            )

        # Check for overspent
        if percentage_used >= 100:
            self._create_alert(
                budget_id,
                AlertType.OVERSPENT,
                f"You have exceeded your {budget.category} budget by {(percentage_used - 100):.1f}%",
                percentage_used
            )

    def _create_alert(self, budget_id: int, alert_type: AlertType, message: str, threshold_percentage: float) -> None:
        """Create a budget alert if one doesn't already exist."""
        existing_alert = self.db.query(BudgetAlert).filter(
            BudgetAlert.budget_id == budget_id,
            BudgetAlert.type == alert_type,
            BudgetAlert.status == AlertStatus.ACTIVE
        ).first()

        if not existing_alert:
            alert = BudgetAlert(
                budget_id=budget_id,
                type=alert_type,
                message=message,
                threshold_percentage=threshold_percentage
            )
            self.db.add(alert)
            self.db.commit()

    def get_active_alerts(self, user_id: int) -> List[BudgetAlert]:
        """Get all active alerts for a user's budgets."""
        return self.db.query(BudgetAlert).join(Budget).filter(
            Budget.user_id == user_id,
            BudgetAlert.status == AlertStatus.ACTIVE
        ).all()

    def dismiss_alert(self, alert_id: int, user_id: int) -> None:
        """Dismiss a budget alert."""
        alert = self.db.query(BudgetAlert).join(Budget).filter(
            BudgetAlert.id == alert_id,
            Budget.user_id == user_id
        ).first()
        
        if alert:
            alert.status = AlertStatus.DISMISSED
            self.db.commit()
