from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.deps import get_current_active_user, get_db, get_current_active_superuser
from app.services.compliance_service import ComplianceService
from app.models.user import User as UserModel
from app.schemas.compliance import (
    ComplianceCheckResponse,
    RiskAssessmentResponse,
    ComplianceReportResponse,
    SustainabilityResponse
)

router = APIRouter()

@router.post("/kyc/verify/{user_id}", response_model=ComplianceCheckResponse)
async def verify_kyc(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_superuser)
):
    """
    Perform KYC verification for a user.
    Only accessible by admin users.
    """
    compliance_service = ComplianceService(db)
    result = await compliance_service.perform_kyc_verification(user_id)
    return result

@router.get("/risk-assessment", response_model=RiskAssessmentResponse)
async def get_risk_assessment(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get risk assessment for the current user.
    """
    compliance_service = ComplianceService(db)
    assessment = await compliance_service.get_user_risk_assessment(current_user.id)
    return assessment

@router.get("/reports", response_model=List[ComplianceReportResponse])
async def get_compliance_reports(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_superuser),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """
    Get compliance reports.
    Only accessible by admin users.
    """
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
        
    compliance_service = ComplianceService(db)
    reports = await compliance_service.generate_regulatory_reports(start_date, end_date)
    return reports

@router.get("/sustainability/{account_id}", response_model=SustainabilityResponse)
async def get_sustainability_metrics(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get sustainability metrics for an account.
    """
    # Verify account ownership
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    compliance_service = ComplianceService(db)
    metrics = await compliance_service.assess_environmental_impact(account_id)
    return metrics

@router.post("/verify-ethical/{transaction_id}")
async def verify_ethical_compliance(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Verify ethical compliance for a transaction.
    """
    # Verify transaction ownership
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    compliance_service = ComplianceService(db)
    result = await compliance_service.verify_ethical_compliance(transaction)
    return result

@router.get("/requirements")
async def get_regulatory_requirements(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
    jurisdiction: Optional[str] = None
):
    """
    Get applicable regulatory requirements.
    """
    query = db.query(RegulatoryRequirement).filter(
        RegulatoryRequirement.active == True
    )
    
    if jurisdiction:
        query = query.filter(RegulatoryRequirement.jurisdiction == jurisdiction)
    
    requirements = query.all()
    return requirements
