from typing import Optional, Dict
from pydantic import BaseModel, condecimal
from datetime import datetime
from decimal import Decimal
from app.models.account import AccountType, AccountStatus

class AccountBase(BaseModel):
    type: Optional[AccountType] = None
    status: Optional[AccountStatus] = None
    currency: Optional[str] = "USD"
    daily_transfer_limit: Optional[condecimal(max_digits=18, decimal_places=2)] = None
    withdrawal_limit: Optional[condecimal(max_digits=18, decimal_places=2)] = None
    interest_rate: Optional[condecimal(max_digits=5, decimal_places=2)] = None
    features: Optional[Dict] = None
    metadata: Optional[Dict] = None

class AccountCreate(AccountBase):
    type: AccountType
    currency: str = "USD"
    initial_balance: condecimal(max_digits=18, decimal_places=2) = Decimal("0")

class AccountUpdate(AccountBase):
    pass

class AccountInDBBase(AccountBase):
    id: int
    account_number: str
    user_id: int
    balance: condecimal(max_digits=18, decimal_places=2)
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Account(AccountInDBBase):
    pass

class AccountBalance(BaseModel):
    balance: condecimal(max_digits=18, decimal_places=2)

class AccountTransaction(BaseModel):
    amount: condecimal(max_digits=18, decimal_places=2)
    operation: str  # "credit" or "debit"

class AccountLimits(BaseModel):
    daily_transfer_limit: Optional[condecimal(max_digits=18, decimal_places=2)] = None
    withdrawal_limit: Optional[condecimal(max_digits=18, decimal_places=2)] = None
