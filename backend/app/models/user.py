from sqlalchemy import Boolean, Column, String, Enum, JSON, Integer, DateTime
from sqlalchemy.orm import relationship
from .base import TimestampedBase
import enum
from datetime import datetime

class UserRole(enum.Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"
    STAFF = "staff"

class User(TimestampedBase):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    date_of_birth = Column(DateTime)
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_staff = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    preferences = Column(JSON, default={})
    risk_profile = Column(String)
    kyc_status = Column(String)
    metadata = Column(JSON)
    
    # Security and authentication
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String, nullable=True)
    biometric_data = Column(JSON, nullable=True)
    security_questions = Column(JSON, nullable=True)
    
    # User preferences and settings
    notification_settings = Column(JSON, default={})
    
    # Risk and compliance
    risk_score = Column(Integer, default=0)
    last_risk_assessment = Column(DateTime, nullable=True)
    
    # Relationships
    accounts = relationship("Account", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    budgets = relationship("Budget", back_populates="user")
    portfolios = relationship("Portfolio", back_populates="user")
    auth_devices = relationship("AuthDevice", back_populates="user")
    mfa_methods = relationship("MFAMethod", back_populates="user")
    auth_sessions = relationship("AuthSession", back_populates="user")
    social_accounts = relationship("SocialAccount", back_populates="user")
    consent_records = relationship("ConsentRecord", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.email}>"
