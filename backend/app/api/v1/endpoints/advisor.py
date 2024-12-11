from fastapi import APIRouter, Depends, HTTPException
from typing import Dict
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.services.ai_advisor_service import AIAdvisorService
from app.models.user import User

router = APIRouter()

@router.get("/insights")
def get_comprehensive_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Get comprehensive financial insights and recommendations."""
    advisor_service = AIAdvisorService(db)
    return advisor_service.get_comprehensive_insights(current_user.id)

@router.get("/spending-analysis")
def get_spending_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Get detailed spending pattern analysis."""
    advisor_service = AIAdvisorService(db)
    return advisor_service._analyze_spending_patterns(current_user.id)

@router.get("/budget-recommendations")
def get_budget_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Get personalized budget recommendations."""
    advisor_service = AIAdvisorService(db)
    return advisor_service._generate_budget_recommendations(current_user.id)

@router.get("/investment-recommendations")
def get_investment_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Get investment recommendations based on portfolio analysis."""
    advisor_service = AIAdvisorService(db)
    return advisor_service._generate_investment_recommendations(current_user.id)

@router.get("/savings-opportunities")
def get_savings_opportunities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Get potential savings opportunities."""
    advisor_service = AIAdvisorService(db)
    return advisor_service._identify_savings_opportunities(current_user.id)

@router.get("/risk-analysis")
def get_risk_analysis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Get financial risk analysis."""
    advisor_service = AIAdvisorService(db)
    return advisor_service._analyze_financial_risks(current_user.id)

@router.get("/financial-goals")
def get_financial_goals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """Get financial goals tracking."""
    advisor_service = AIAdvisorService(db)
    return advisor_service._track_financial_goals(current_user.id)
