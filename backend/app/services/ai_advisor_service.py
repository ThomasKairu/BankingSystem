from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
from app.schemas.advisor import *
from app.models.transaction import Transaction
from app.models.budget import Budget, BudgetExpense
from app.models.investment import Portfolio, Holding, InvestmentTransaction
from app.services.budget_service import BudgetService
from app.services.investment_service import InvestmentService

class AIAdvisorService:
    def __init__(self, db: Session):
        self.db = db
        self.budget_service = BudgetService(db)
        self.investment_service = InvestmentService(db)

    def get_comprehensive_insights(self, user_id: int) -> InsightResponse:
        # Analyze recent transactions, budgets, and investments
        transactions_df = self._get_user_transactions_df(user_id)
        budget_analysis = self._analyze_budget_performance(user_id)
        investment_analysis = self._analyze_investment_performance(user_id)
        
        # Generate key findings and alerts
        key_findings = self._generate_key_findings(
            transactions_df, 
            budget_analysis, 
            investment_analysis
        )
        alerts = self._generate_alerts(
            transactions_df, 
            budget_analysis, 
            investment_analysis
        )
        
        return InsightResponse(
            summary=self._generate_summary(key_findings),
            key_findings=key_findings,
            alerts=alerts
        )

    def _analyze_spending_patterns(self, user_id: int) -> SpendingAnalysisResponse:
        # Get transaction data
        transactions_df = self._get_user_transactions_df(user_id)
        
        # Calculate monthly trends
        monthly_trends = self._calculate_monthly_trends(transactions_df)
        
        # Calculate category breakdown
        category_breakdown = self._calculate_category_breakdown(transactions_df)
        
        # Generate spending insights
        insights = self._generate_spending_insights(transactions_df)
        
        return SpendingAnalysisResponse(
            monthly_trends=monthly_trends,
            category_breakdown=category_breakdown,
            insights=insights
        )

    def _generate_budget_recommendations(self, user_id: int) -> BudgetRecommendationsResponse:
        # Analyze current spending patterns
        transactions_df = self._get_user_transactions_df(user_id)
        current_budgets = self.budget_service.get_user_budgets(user_id)
        
        # Generate recommendations based on spending patterns and financial goals
        recommendations = self._calculate_budget_recommendations(
            transactions_df, 
            current_budgets
        )
        
        return BudgetRecommendationsResponse(
            overview=self._generate_budget_overview(recommendations),
            items=recommendations
        )

    def _generate_investment_recommendations(self, user_id: int) -> InvestmentRecommendationsResponse:
        # Analyze current portfolio
        portfolio = self.investment_service.get_user_portfolios(user_id)
        risk_profile = self._determine_risk_profile(user_id)
        
        # Generate recommendations based on risk profile and market conditions
        recommendations = self._calculate_investment_recommendations(
            portfolio, 
            risk_profile
        )
        
        return InvestmentRecommendationsResponse(
            summary=self._generate_investment_summary(recommendations),
            risk_profile=risk_profile,
            expected_return=self._calculate_expected_return(recommendations),
            items=recommendations
        )

    def _identify_savings_opportunities(self, user_id: int) -> SavingsOpportunitiesResponse:
        # Analyze spending patterns and recurring expenses
        transactions_df = self._get_user_transactions_df(user_id)
        
        # Identify potential savings opportunities
        opportunities = self._find_savings_opportunities(transactions_df)
        total_savings = sum(opp.potential_savings for opp in opportunities)
        
        return SavingsOpportunitiesResponse(
            total_potential_savings=total_savings,
            items=opportunities
        )

    def _analyze_financial_risks(self, user_id: int) -> RiskAnalysisResponse:
        # Analyze various risk factors
        budget_risk = self._analyze_budget_risk(user_id)
        investment_risk = self._analyze_investment_risk(user_id)
        debt_risk = self._analyze_debt_risk(user_id)
        
        # Calculate overall risk level
        risk_factors = self._compile_risk_factors(
            budget_risk, 
            investment_risk, 
            debt_risk
        )
        overall_risk = self._calculate_overall_risk(risk_factors)
        
        return RiskAnalysisResponse(
            overall_risk=overall_risk,
            summary=self._generate_risk_summary(risk_factors),
            factors=risk_factors,
            trends=self._calculate_risk_trends(user_id)
        )

    def _track_financial_goals(self, user_id: int) -> FinancialGoalsResponse:
        # Get user's financial goals and track progress
        goals = self._get_user_goals(user_id)
        tracked_goals = self._track_goals_progress(goals)
        
        return FinancialGoalsResponse(
            summary=self._generate_goals_summary(tracked_goals),
            items=tracked_goals
        )

    # Helper methods for data processing and analysis
    def _get_user_transactions_df(self, user_id: int) -> pd.DataFrame:
        transactions = self.db.query(Transaction).filter(
            Transaction.user_id == user_id
        ).all()
        
        return pd.DataFrame([{
            'date': t.date,
            'amount': t.amount,
            'category': t.category,
            'type': t.type,
            'description': t.description
        } for t in transactions])

    def _calculate_monthly_trends(self, df: pd.DataFrame) -> List[SpendingTrend]:
        monthly = df.groupby(df['date'].dt.strftime('%Y-%m'))[['amount']].sum()
        return [
            SpendingTrend(month=month, amount=float(amount))
            for month, amount in monthly.itertuples()
        ]

    def _calculate_category_breakdown(self, df: pd.DataFrame) -> List[CategorySpending]:
        category_totals = df.groupby('category')['amount'].sum()
        total_spending = category_totals.sum()
        
        return [
            CategorySpending(
                category=category,
                amount=float(amount),
                percentage=float(amount / total_spending * 100)
            )
            for category, amount in category_totals.items()
        ]

    def _determine_risk_profile(self, user_id: int) -> str:
        # Analyze various factors to determine risk profile
        # This is a simplified version - in reality, would use more sophisticated analysis
        investment_history = self.investment_service.get_investment_history(user_id)
        transaction_history = self._get_user_transactions_df(user_id)
        
        # Calculate risk metrics
        volatility = self._calculate_portfolio_volatility(investment_history)
        income_stability = self._analyze_income_stability(transaction_history)
        debt_ratio = self._calculate_debt_ratio(user_id)
        
        # Determine risk profile based on combined metrics
        risk_score = self._calculate_risk_score(volatility, income_stability, debt_ratio)
        
        if risk_score < 0.3:
            return "Conservative"
        elif risk_score < 0.7:
            return "Moderate"
        else:
            return "Aggressive"

    def _generate_key_findings(
        self, 
        transactions_df: pd.DataFrame, 
        budget_analysis: Dict, 
        investment_analysis: Dict
    ) -> List[str]:
        findings = []
        
        # Analyze spending patterns
        if not transactions_df.empty:
            recent_spending = transactions_df['amount'].sum()
            avg_spending = transactions_df['amount'].mean()
            
            if recent_spending > avg_spending * 1.2:
                findings.append("Spending has increased by 20% compared to your average")
        
        # Analyze budget performance
        for category, performance in budget_analysis.items():
            if performance['percentage'] > 90:
                findings.append(f"You're close to exceeding your {category} budget")
        
        # Analyze investment performance
        for asset, performance in investment_analysis.items():
            if performance['return'] > 10:
                findings.append(f"Your {asset} investments are performing well")
        
        return findings

    def _generate_alerts(
        self, 
        transactions_df: pd.DataFrame, 
        budget_analysis: Dict, 
        investment_analysis: Dict
    ) -> List[str]:
        alerts = []
        
        # Check for unusual transactions
        recent_transactions = transactions_df[
            transactions_df['date'] >= datetime.now() - timedelta(days=7)
        ]
        
        for _, transaction in recent_transactions.iterrows():
            if transaction['amount'] > 1000:  # Threshold for large transactions
                alerts.append(f"Large transaction detected: ${transaction['amount']} on {transaction['date']}")
        
        # Check budget overruns
        for category, performance in budget_analysis.items():
            if performance['percentage'] > 100:
                alerts.append(f"Budget exceeded for {category}")
        
        # Check investment alerts
        for asset, performance in investment_analysis.items():
            if performance['volatility'] > 0.2:  # High volatility threshold
                alerts.append(f"High volatility detected in {asset} investments")
        
        return alerts

    def _generate_spending_insights(self, df: pd.DataFrame) -> List[str]:
        insights = []
        
        # Analyze spending trends
        monthly_spending = df.groupby(df['date'].dt.strftime('%Y-%m'))['amount'].sum()
        if len(monthly_spending) >= 2:
            current_month = monthly_spending.iloc[-1]
            previous_month = monthly_spending.iloc[-2]
            change = (current_month - previous_month) / previous_month * 100
            
            if abs(change) > 10:
                insights.append(
                    f"Your spending has {'increased' if change > 0 else 'decreased'} "
                    f"by {abs(change):.1f}% compared to last month"
                )
        
        # Analyze category patterns
        category_spending = df.groupby('category')['amount'].sum()
        top_category = category_spending.idxmax()
        top_amount = category_spending.max()
        
        insights.append(
            f"Your highest spending category is {top_category} "
            f"at ${top_amount:.2f}"
        )
        
        return insights

    def _calculate_budget_recommendations(
        self, 
        transactions_df: pd.DataFrame, 
        current_budgets: List[Budget]
    ) -> List[BudgetRecommendation]:
        recommendations = []
        
        for budget in current_budgets:
            category_spending = transactions_df[
                transactions_df['category'] == budget.category
            ]['amount'].sum()
            
            if category_spending > budget.amount * 1.1:  # Over budget by 10%
                recommendations.append(
                    BudgetRecommendation(
                        category=budget.category,
                        current_spending=float(category_spending),
                        recommended_budget=float(budget.amount * 1.2),
                        impact="High impact on monthly savings",
                        priority=RiskLevel.HIGH
                    )
                )
            elif category_spending < budget.amount * 0.8:  # Under budget by 20%
                recommendations.append(
                    BudgetRecommendation(
                        category=budget.category,
                        current_spending=float(category_spending),
                        recommended_budget=float(budget.amount * 0.9),
                        impact="Potential for reallocation to savings",
                        priority=RiskLevel.LOW
                    )
                )
        
        return recommendations

    def _find_savings_opportunities(self, df: pd.DataFrame) -> List[SavingsOpportunity]:
        opportunities = []
        
        # Analyze recurring expenses
        recurring = self._identify_recurring_expenses(df)
        for category, amount in recurring.items():
            if amount > 100:  # Significant recurring expense
                opportunities.append(
                    SavingsOpportunity(
                        category=category,
                        potential_savings=float(amount * 0.2),  # Assume 20% potential savings
                        difficulty=Difficulty.MEDIUM,
                        impact=20.0,
                        description=f"Potential savings in recurring {category} expenses",
                        steps=[
                            f"Review current {category} services",
                            "Compare with alternative providers",
                            "Negotiate better rates with current provider"
                        ]
                    )
                )
        
        return opportunities

    def _identify_recurring_expenses(self, df: pd.DataFrame) -> Dict[str, float]:
        # Group by category and description
        grouped = df.groupby(['category', 'description'])
        
        recurring = {}
        for (category, description), group in grouped:
            if len(group) >= 3:  # At least 3 occurrences
                amounts = group['amount'].tolist()
                if len(set(amounts)) <= 2:  # Similar amounts
                    recurring[category] = sum(amounts) / len(amounts)
        
        return recurring

    def _calculate_risk_score(
        self, 
        volatility: float, 
        income_stability: float, 
        debt_ratio: float
    ) -> float:
        # Weighted average of risk factors
        weights = {
            'volatility': 0.4,
            'income_stability': 0.3,
            'debt_ratio': 0.3
        }
        
        return (
            volatility * weights['volatility'] +
            (1 - income_stability) * weights['income_stability'] +
            debt_ratio * weights['debt_ratio']
        )
