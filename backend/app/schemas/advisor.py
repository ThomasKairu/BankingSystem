from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class GoalStatus(str, Enum):
    ON_TRACK = "on_track"
    AT_RISK = "at_risk"
    BEHIND = "behind"

class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class InsightResponse(BaseModel):
    summary: str
    key_findings: List[str]
    alerts: List[str]

class SpendingTrend(BaseModel):
    month: str
    amount: float

class CategorySpending(BaseModel):
    category: str
    amount: float
    percentage: float

class SpendingAnalysisResponse(BaseModel):
    monthly_trends: List[SpendingTrend]
    category_breakdown: List[CategorySpending]
    insights: List[str]

class BudgetRecommendation(BaseModel):
    category: str
    current_spending: float
    recommended_budget: float
    impact: str
    priority: RiskLevel

class BudgetRecommendationsResponse(BaseModel):
    overview: str
    items: List[BudgetRecommendation]

class InvestmentRecommendation(BaseModel):
    asset_class: str
    current_allocation: float
    recommended_allocation: float
    reasoning: str
    risk: RiskLevel

class InvestmentRecommendationsResponse(BaseModel):
    summary: str
    risk_profile: str
    expected_return: float
    items: List[InvestmentRecommendation]

class SavingsOpportunity(BaseModel):
    category: str
    potential_savings: float
    difficulty: Difficulty
    impact: float
    description: str
    steps: List[str]

class SavingsOpportunitiesResponse(BaseModel):
    total_potential_savings: float
    items: List[SavingsOpportunity]

class RiskFactor(BaseModel):
    category: str
    level: RiskLevel
    description: str
    mitigation: str

class RiskTrend(BaseModel):
    period: str
    risk_score: float

class RiskAnalysisResponse(BaseModel):
    overall_risk: RiskLevel
    summary: str
    factors: List[RiskFactor]
    trends: List[RiskTrend]

class FinancialGoal(BaseModel):
    name: str
    target_amount: float
    current_amount: float
    deadline: str
    progress: float
    status: GoalStatus
    next_steps: List[str]

class FinancialGoalsResponse(BaseModel):
    summary: str
    items: List[FinancialGoal]
