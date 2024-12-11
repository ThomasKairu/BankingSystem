from sqlalchemy import Column, Integer, String, JSON, Enum, ForeignKey, Float
from sqlalchemy.orm import relationship
from .base import TimestampedBase
import enum

class ComplianceStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    FLAGGED = "flagged"
    ERROR = "error"

class RiskLevel(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ComplianceCheck(TimestampedBase):
    __tablename__ = "compliance_checks"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    check_type = Column(String, nullable=False)  # KYC, AML, CTF, etc.
    status = Column(Enum(ComplianceStatus), default=ComplianceStatus.PENDING)
    details = Column(JSON, nullable=True)
    notes = Column(String, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="compliance_checks")

class ComplianceReport(TimestampedBase):
    __tablename__ = "compliance_reports"

    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True)
    report_type = Column(String, nullable=False)
    details = Column(JSON, nullable=False)
    submitted = Column(Boolean, default=False)
    
    # Relationships
    transaction = relationship("Transaction", back_populates="compliance_reports")

class RegulatoryRequirement(TimestampedBase):
    __tablename__ = "regulatory_requirements"

    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    category = Column(String, nullable=False)  # AML, KYC, etc.
    jurisdiction = Column(String, nullable=False)
    requirements = Column(JSON, nullable=False)
    active = Column(Boolean, default=True)

class RiskAssessment(TimestampedBase):
    __tablename__ = "risk_assessments"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    risk_level = Column(Enum(RiskLevel), default=RiskLevel.LOW)
    factors = Column(JSON, nullable=False)
    score = Column(Float, nullable=False)
    next_review_date = Column(DateTime, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="risk_assessments")

class SustainabilityMetric(TimestampedBase):
    __tablename__ = "sustainability_metrics"

    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    carbon_footprint = Column(Float, default=0.0)
    sustainability_score = Column(Float, default=0.0)
    metrics = Column(JSON, nullable=False)
    recommendations = Column(JSON, nullable=True)
    
    # Relationships
    account = relationship("Account", back_populates="sustainability_metrics")
