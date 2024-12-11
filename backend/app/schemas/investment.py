from pydantic import BaseModel, validator
from typing import Optional, List, Dict
from datetime import datetime
from app.models.investment import AssetType, TransactionType

class PortfolioBase(BaseModel):
    name: str
    description: Optional[str] = None

class PortfolioCreate(PortfolioBase):
    pass

class PortfolioUpdate(PortfolioBase):
    pass

class HoldingBase(BaseModel):
    asset_type: AssetType
    symbol: str
    quantity: float
    average_price: float
    current_price: Optional[float] = None
    metadata: Optional[Dict] = None

class HoldingCreate(HoldingBase):
    pass

class Holding(HoldingBase):
    id: int
    portfolio_id: int
    last_updated: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    market_value: float
    gain_loss: float
    gain_loss_percentage: float

    class Config:
        orm_mode = True

class TransactionBase(BaseModel):
    transaction_type: TransactionType
    symbol: str
    quantity: float
    price: float
    fees: Optional[float] = 0
    date: Optional[datetime] = None
    notes: Optional[str] = None
    asset_type: AssetType

    @validator('quantity')
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v

    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    portfolio_id: int
    holding_id: Optional[int]
    total_amount: float
    created_at: datetime

    class Config:
        orm_mode = True

class AlertBase(BaseModel):
    holding_id: Optional[int]
    alert_type: str  # price_target, price_change, portfolio_change
    threshold: float
    message: str

class AlertCreate(AlertBase):
    pass

class Alert(AlertBase):
    id: int
    portfolio_id: int
    is_active: bool
    triggered_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PortfolioPerformanceBase(BaseModel):
    date: datetime
    total_value: float
    daily_return: Optional[float]
    total_return: Optional[float]
    cash_flow: Optional[float]

class PortfolioPerformance(PortfolioPerformanceBase):
    id: int
    portfolio_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class Portfolio(PortfolioBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    holdings: List[Holding]
    transactions: List[Transaction]
    performance_history: List[PortfolioPerformance]

    class Config:
        orm_mode = True

class PortfolioSummary(BaseModel):
    total_value: float
    total_gain_loss: float
    gain_loss_percentage: float
    allocation: Dict[AssetType, float]
    last_updated: Optional[datetime]

class PerformanceHistory(BaseModel):
    date: datetime
    total_value: float
    daily_return: Optional[float]
    total_return: Optional[float]
