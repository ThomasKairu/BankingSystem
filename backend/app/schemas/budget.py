from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from app.models.budget import BudgetCategory, BudgetPeriod, AlertType, AlertStatus

class BudgetBase(BaseModel):
    name: str
    category: BudgetCategory
    amount: float
    period: BudgetPeriod
    start_date: datetime
    end_date: Optional[datetime] = None

    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

    @validator('end_date')
    def end_date_must_be_after_start_date(cls, v, values):
        if v and 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v

class BudgetCreate(BudgetBase):
    pass

class BudgetUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[BudgetCategory] = None
    amount: Optional[float] = None
    period: Optional[BudgetPeriod] = None
    end_date: Optional[datetime] = None

class BudgetExpenseBase(BaseModel):
    transaction_id: Optional[int] = None
    amount: float
    description: Optional[str] = None
    date: Optional[datetime] = None

    @validator('amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

class BudgetExpenseCreate(BudgetExpenseBase):
    pass

class BudgetExpense(BudgetExpenseBase):
    id: int
    budget_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class BudgetAlert(BaseModel):
    id: int
    budget_id: int
    type: AlertType
    status: AlertStatus
    message: str
    threshold_percentage: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Budget(BudgetBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    expenses: List[BudgetExpense]
    alerts: List[BudgetAlert]

    class Config:
        orm_mode = True

class BudgetSummary(BaseModel):
    budget_id: int
    total_budget: float
    total_spent: float
    remaining: float
    percentage_used: float
    period: BudgetPeriod
    category: BudgetCategory

class CategorySpending(BaseModel):
    total_spent: float
    budget_amount: float
