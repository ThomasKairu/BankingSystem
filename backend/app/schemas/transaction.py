from typing import Optional, Dict
from pydantic import BaseModel, condecimal
from datetime import datetime
from app.models.transaction import TransactionType, TransactionStatus

class TransactionBase(BaseModel):
    account_id: int
    amount: condecimal(max_digits=18, decimal_places=2)
    type: TransactionType
    description: Optional[str] = None
    category: Optional[str] = None
    recipient_account: Optional[str] = None
    recipient_bank: Optional[str] = None
    merchant_info: Optional[Dict] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    reference_id: str
    user_id: int
    status: TransactionStatus
    currency: str
    created_at: datetime
    processed_at: Optional[datetime] = None
    risk_score: Optional[int] = None
    
    class Config:
        orm_mode = True

class TransactionStatistics(BaseModel):
    total_transactions: int
    total_deposits: condecimal(max_digits=18, decimal_places=2)
    total_withdrawals: condecimal(max_digits=18, decimal_places=2)
    total_transfers: condecimal(max_digits=18, decimal_places=2)
    net_flow: condecimal(max_digits=18, decimal_places=2)
    period_days: int
