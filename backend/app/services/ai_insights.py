from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.transaction import Transaction
from app.models.user import User
from app.models.account import Account
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd
from fastapi import HTTPException

class AiInsightsService:
    def __init__(self, db: Session):
        self.db = db

    async def generate_spending_insights(self, user_id: int) -> Dict[str, Any]:
        """Generate AI-powered spending insights for the user"""
        try:
            # Get user's transactions for the last 3 months
            three_months_ago = datetime.utcnow() - timedelta(days=90)
            transactions = (
                self.db.query(Transaction)
                .filter(
                    Transaction.user_id == user_id,
                    Transaction.created_at >= three_months_ago,
                    Transaction.type == "debit"
                )
                .all()
            )

            if not transactions:
                return {
                    "message": "Not enough transaction data to generate insights",
                    "insights": []
                }

            # Prepare data for analysis
            df = pd.DataFrame([
                {
                    "amount": t.amount,
                    "category": t.metadata.get("category", "uncategorized"),
                    "date": t.created_at,
                    "day_of_week": t.created_at.strftime("%A"),
                    "hour": t.created_at.hour
                }
                for t in transactions
            ])

            insights = []

            # Spending patterns by category
            category_spending = df.groupby("category")["amount"].agg(["sum", "count"]).reset_index()
            for _, row in category_spending.iterrows():
                insights.append({
                    "type": "category_insight",
                    "category": row["category"],
                    "total_spent": float(row["sum"]),
                    "transaction_count": int(row["count"]),
                    "message": f"You've spent {row['sum']:.2f} on {row['category']} across {row['count']} transactions"
                })

            # Unusual spending patterns
            category_means = df.groupby("category")["amount"].mean()
            category_stds = df.groupby("category")["amount"].std()
            
            for category in category_means.index:
                unusual_transactions = df[
                    (df["category"] == category) &
                    (df["amount"] > category_means[category] + 2 * category_stds[category])
                ]
                if not unusual_transactions.empty:
                    insights.append({
                        "type": "unusual_spending",
                        "category": category,
                        "transactions": unusual_transactions["amount"].tolist(),
                        "message": f"Found {len(unusual_transactions)} unusually large transactions in {category}"
                    })

            # Spending trends
            monthly_spending = df.set_index("date").resample("M")["amount"].sum()
            if len(monthly_spending) >= 2:
                trend_percentage = ((monthly_spending.iloc[-1] - monthly_spending.iloc[-2]) 
                                 / monthly_spending.iloc[-2] * 100)
                insights.append({
                    "type": "spending_trend",
                    "trend_percentage": float(trend_percentage),
                    "message": f"Your spending has {'increased' if trend_percentage > 0 else 'decreased'} "
                             f"by {abs(trend_percentage):.1f}% compared to last month"
                })

            # Peak spending times
            hourly_spending = df.groupby("hour")["amount"].sum()
            peak_hour = hourly_spending.idxmax()
            insights.append({
                "type": "peak_spending_time",
                "hour": int(peak_hour),
                "amount": float(hourly_spending[peak_hour]),
                "message": f"You tend to spend most around {peak_hour:02d}:00"
            })

            # Spending clusters
            if len(df) >= 5:  # Minimum data points for clustering
                scaler = StandardScaler()
                features = scaler.fit_transform(df[["amount", "hour"]].values)
                kmeans = KMeans(n_clusters=3, random_state=42)
                df["cluster"] = kmeans.fit_predict(features)

                for cluster in range(3):
                    cluster_data = df[df["cluster"] == cluster]
                    if len(cluster_data) > 0:
                        insights.append({
                            "type": "spending_cluster",
                            "cluster_id": int(cluster),
                            "average_amount": float(cluster_data["amount"].mean()),
                            "common_hour": int(cluster_data["hour"].mode()[0]),
                            "transaction_count": len(cluster_data),
                            "message": f"Found a spending pattern: {len(cluster_data)} transactions "
                                     f"averaging {cluster_data['amount'].mean():.2f} "
                                     f"typically around {cluster_data['hour'].mode()[0]:02d}:00"
                        })

            return {
                "message": "Successfully generated insights",
                "insights": insights
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating insights: {str(e)}"
            )

    async def generate_savings_recommendations(self, user_id: int) -> Dict[str, Any]:
        """Generate AI-powered savings recommendations"""
        try:
            # Get user's financial data
            user = self.db.query(User).filter(User.id == user_id).first()
            accounts = self.db.query(Account).filter(Account.user_id == user_id).all()
            
            recommendations = []

            # Analyze spending patterns
            monthly_expenses = await self._calculate_monthly_expenses(user_id)
            monthly_income = await self._calculate_monthly_income(user_id)

            if monthly_income and monthly_expenses:
                # Calculate savings potential
                current_savings_rate = (monthly_income - monthly_expenses) / monthly_income
                recommended_savings_rate = 0.20  # 20% recommended savings rate

                if current_savings_rate < recommended_savings_rate:
                    potential_savings = monthly_income * recommended_savings_rate
                    recommendations.append({
                        "type": "savings_rate",
                        "current_rate": float(current_savings_rate),
                        "recommended_rate": float(recommended_savings_rate),
                        "potential_savings": float(potential_savings),
                        "message": f"You could save {potential_savings:.2f} monthly by saving "
                                 f"{recommended_savings_rate*100}% of your income"
                    })

            # Analyze recurring expenses
            recurring_expenses = await self._identify_recurring_expenses(user_id)
            if recurring_expenses:
                recommendations.append({
                    "type": "recurring_expenses",
                    "expenses": recurring_expenses,
                    "total_amount": sum(expense["amount"] for expense in recurring_expenses),
                    "message": "Consider reviewing these recurring expenses for potential savings"
                })

            # Generate emergency fund recommendation
            total_balance = sum(account.balance for account in accounts)
            recommended_emergency_fund = monthly_expenses * 6  # 6 months of expenses
            
            if total_balance < recommended_emergency_fund:
                recommendations.append({
                    "type": "emergency_fund",
                    "current_balance": float(total_balance),
                    "recommended_balance": float(recommended_emergency_fund),
                    "deficit": float(recommended_emergency_fund - total_balance),
                    "message": f"Consider building an emergency fund of {recommended_emergency_fund:.2f} "
                             f"(6 months of expenses)"
                })

            return {
                "message": "Successfully generated savings recommendations",
                "recommendations": recommendations
            }

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating savings recommendations: {str(e)}"
            )

    async def _calculate_monthly_expenses(self, user_id: int) -> float:
        """Calculate average monthly expenses"""
        one_month_ago = datetime.utcnow() - timedelta(days=30)
        expenses = (
            self.db.query(func.sum(Transaction.amount))
            .filter(
                Transaction.user_id == user_id,
                Transaction.type == "debit",
                Transaction.created_at >= one_month_ago
            )
            .scalar() or 0
        )
        return float(expenses)

    async def _calculate_monthly_income(self, user_id: int) -> float:
        """Calculate average monthly income"""
        one_month_ago = datetime.utcnow() - timedelta(days=30)
        income = (
            self.db.query(func.sum(Transaction.amount))
            .filter(
                Transaction.user_id == user_id,
                Transaction.type == "credit",
                Transaction.created_at >= one_month_ago
            )
            .scalar() or 0
        )
        return float(income)

    async def _identify_recurring_expenses(self, user_id: int) -> List[Dict[str, Any]]:
        """Identify recurring expenses"""
        three_months_ago = datetime.utcnow() - timedelta(days=90)
        transactions = (
            self.db.query(Transaction)
            .filter(
                Transaction.user_id == user_id,
                Transaction.type == "debit",
                Transaction.created_at >= three_months_ago
            )
            .all()
        )

        # Group transactions by description and amount
        transaction_groups = {}
        for t in transactions:
            key = (t.description, t.amount)
            if key not in transaction_groups:
                transaction_groups[key] = []
            transaction_groups[key].append(t)

        recurring_expenses = []
        for (description, amount), group in transaction_groups.items():
            if len(group) >= 3:  # At least 3 occurrences to be considered recurring
                recurring_expenses.append({
                    "description": description,
                    "amount": float(amount),
                    "frequency": len(group),
                    "last_date": max(t.created_at for t in group).isoformat()
                })

        return recurring_expenses
