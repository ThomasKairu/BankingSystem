from sqlalchemy import Column, String, Enum, Numeric, ForeignKey, JSON, Integer
from sqlalchemy.orm import relationship
from .base import TimestampedBase
import enum

class AccountType(enum.Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
    INVESTMENT = "investment"
    CRYPTO = "crypto"
    BUSINESS = "business"
    STUDENT = "student"
    JOINT = "joint"

class AccountStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FROZEN = "frozen"
    CLOSED = "closed"

class Account(TimestampedBase):
    __tablename__ = "accounts"

    account_number = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(AccountType), nullable=False)
    status = Column(Enum(AccountStatus), default=AccountStatus.ACTIVE)
    balance = Column(Numeric(precision=18, scale=2), default=0)
    currency = Column(String, default="USD")
    
    # Account features and limits
    daily_transfer_limit = Column(Numeric(precision=18, scale=2))
    withdrawal_limit = Column(Numeric(precision=18, scale=2))
    interest_rate = Column(Numeric(precision=5, scale=2))
    
    # Additional features
    features = Column(JSON, default={})
    metadata = Column(JSON, default={})
    
    # Risk and compliance
    risk_level = Column(String, default="low")
    last_activity = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")
    
    def __repr__(self):
        return f"<Account {self.account_number}>"
