from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.services.ai_insights import AiInsightsService
from app.models.user import User
from typing import Dict, Any

router = APIRouter()

@router.get("/spending")
async def get_spending_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get AI-powered spending insights"""
    insights_service = AiInsightsService(db)
    return await insights_service.generate_spending_insights(current_user.id)

@router.get("/savings")
async def get_savings_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get AI-powered savings recommendations"""
    insights_service = AiInsightsService(db)
    return await insights_service.generate_savings_recommendations(current_user.id)

@router.get("/summary")
async def get_financial_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get comprehensive financial summary with insights"""
    insights_service = AiInsightsService(db)
    
    # Get both spending insights and savings recommendations
    spending_insights = await insights_service.generate_spending_insights(current_user.id)
    savings_recommendations = await insights_service.generate_savings_recommendations(current_user.id)
    
    # Combine insights and add priority levels
    all_insights = []
    
    # Add spending insights
    for insight in spending_insights.get("insights", []):
        priority = "high" if insight["type"] in ["unusual_spending", "spending_trend"] else "medium"
        all_insights.append({
            **insight,
            "priority": priority,
            "category": "spending"
        })
    
    # Add savings recommendations
    for recommendation in savings_recommendations.get("recommendations", []):
        priority = "high" if recommendation["type"] in ["emergency_fund", "savings_rate"] else "medium"
        all_insights.append({
            **recommendation,
            "priority": priority,
            "category": "savings"
        })
    
    # Sort insights by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    all_insights.sort(key=lambda x: priority_order[x["priority"]])
    
    return {
        "message": "Financial summary generated successfully",
        "insights": all_insights,
        "spending_overview": spending_insights.get("message"),
        "savings_overview": savings_recommendations.get("message")
    }
