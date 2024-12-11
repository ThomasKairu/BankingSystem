from sqlalchemy import Column, String, Enum, Numeric, ForeignKey, JSON, Integer, DateTime
from sqlalchemy.orm import relationship
from .base import TimestampedBase
import enum

class TransactionType(enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    PAYMENT = "payment"
    FEE = "fee"
    INTEREST = "interest"
    INVESTMENT = "investment"
    CRYPTO = "crypto"

class TransactionStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REVERSED = "reversed"
    FLAGGED = "flagged"

class Transaction(TimestampedBase):
    __tablename__ = "transactions"

    reference_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    amount = Column(Numeric(precision=18, scale=2), nullable=False)
    currency = Column(String, default="USD")
    
    # Transaction details
    description = Column(String)
    merchant_info = Column(JSON, nullable=True)
    category = Column(String)
    
    # For transfers
    recipient_account = Column(String, nullable=True)
    recipient_bank = Column(String, nullable=True)
    
    # Security and compliance
    ip_address = Column(String, nullable=True)
    device_info = Column(JSON, nullable=True)
    location_info = Column(JSON, nullable=True)
    risk_score = Column(Integer, default=0)
    
    # Processing details
    processed_at = Column(DateTime, nullable=True)
    failure_reason = Column(String, nullable=True)
    metadata = Column(JSON, default={})
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction {self.reference_id}>"
