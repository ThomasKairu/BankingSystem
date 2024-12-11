from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.models.compliance import ComplianceStatus, RiskLevel

class ComplianceCheckBase(BaseModel):
    check_type: str
    status: ComplianceStatus
    details: Optional[Dict] = None
    notes: Optional[str] = None

class ComplianceCheckResponse(ComplianceCheckBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class RiskAssessmentBase(BaseModel):
    risk_level: RiskLevel
    factors: Dict
    score: float
    next_review_date: datetime

class RiskAssessmentResponse(RiskAssessmentBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class ComplianceReportBase(BaseModel):
    report_type: str
    details: Dict
    submitted: bool = False

class ComplianceReportResponse(ComplianceReportBase):
    id: int
    transaction_id: Optional[int]
    created_at: datetime
    
    class Config:
        orm_mode = True

class SustainabilityMetricBase(BaseModel):
    carbon_footprint: float
    sustainability_score: float
    metrics: Dict
    recommendations: Optional[List[str]] = None

class SustainabilityResponse(SustainabilityMetricBase):
    id: int
    account_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class RegulatoryRequirementBase(BaseModel):
    name: str
    description: str
    category: str
    jurisdiction: str
    requirements: Dict
    active: bool = True

class RegulatoryRequirementResponse(RegulatoryRequirementBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True
