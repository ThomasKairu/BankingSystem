from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.transaction import Transaction
from app.models.user import User
from app.models.account import Account
import pandas as pd
import json
from fastapi import HTTPException
from app.core.security_middleware import security_middleware
from app.core.monitoring import monitoring

class ReportingService:
    def __init__(self, db: Session):
        self.db = db

    async def generate_transaction_report(
        self,
        start_date: datetime,
        end_date: datetime,
        report_type: str,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate transaction report based on specified parameters"""
        query = self.db.query(Transaction)
        
        # Apply date filters
        query = query.filter(
            and_(
                Transaction.created_at >= start_date,
                Transaction.created_at <= end_date
            )
        )
        
        # Apply user filter if specified
        if user_id:
            query = query.filter(Transaction.user_id == user_id)
        
        transactions = query.all()
        
        if report_type == "summary":
            return self._generate_summary_report(transactions)
        elif report_type == "detailed":
            return self._generate_detailed_report(transactions)
        else:
            raise HTTPException(status_code=400, detail="Invalid report type")

    def _generate_summary_report(self, transactions: List[Transaction]) -> Dict[str, Any]:
        """Generate summary report from transactions"""
        total_amount = sum(t.amount for t in transactions)
        successful_count = len([t for t in transactions if t.status == "completed"])
        failed_count = len([t for t in transactions if t.status == "failed"])
        
        # Group by transaction type
        type_distribution = {}
        for t in transactions:
            type_distribution[t.type] = type_distribution.get(t.type, 0) + 1
        
        # Calculate hourly distribution
        hourly_distribution = {}
        for t in transactions:
            hour = t.created_at.hour
            hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1
        
        return {
            "total_transactions": len(transactions),
            "total_amount": total_amount,
            "successful_transactions": successful_count,
            "failed_transactions": failed_count,
            "success_rate": (successful_count / len(transactions)) if transactions else 0,
            "type_distribution": type_distribution,
            "hourly_distribution": hourly_distribution,
            "average_amount": total_amount / len(transactions) if transactions else 0
        }

    def _generate_detailed_report(self, transactions: List[Transaction]) -> Dict[str, Any]:
        """Generate detailed report from transactions"""
        transaction_details = []
        
        for t in transactions:
            transaction_details.append({
                "id": t.id,
                "user_id": t.user_id,
                "type": t.type,
                "amount": t.amount,
                "status": t.status,
                "created_at": t.created_at.isoformat(),
                "source_account": t.source_account_id,
                "destination_account": t.destination_account_id,
                "metadata": t.metadata
            })
        
        return {
            "transactions": transaction_details,
            "total_count": len(transaction_details)
        }

    async def generate_user_activity_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate user activity report"""
        # Get user registrations
        new_users = self.db.query(User).filter(
            and_(
                User.created_at >= start_date,
                User.created_at <= end_date
            )
        ).count()
        
        # Get active users
        active_users = self.db.query(User).filter(
            and_(
                User.last_login >= start_date,
                User.last_login <= end_date
            )
        ).count()
        
        # Get security events
        security_events = security_middleware.get_security_events(
            start_date,
            end_date
        )
        
        # Get user engagement metrics
        engagement_metrics = monitoring.get_user_engagement_metrics(
            start_date,
            end_date
        )
        
        return {
            "new_users": new_users,
            "active_users": active_users,
            "security_events": security_events,
            "engagement_metrics": engagement_metrics
        }

    async def export_report_to_csv(
        self,
        report_data: Dict[str, Any],
        report_type: str
    ) -> str:
        """Export report data to CSV format"""
        if report_type == "transactions_summary":
            df = pd.DataFrame([report_data])
            df = df.drop(['type_distribution', 'hourly_distribution'], axis=1)
        elif report_type == "transactions_detailed":
            df = pd.DataFrame(report_data['transactions'])
        elif report_type == "user_activity":
            df = pd.DataFrame([{
                'new_users': report_data['new_users'],
                'active_users': report_data['active_users'],
                'security_events_count': len(report_data['security_events']),
                'engagement_score': report_data['engagement_metrics'].get('engagement_score', 0)
            }])
        else:
            raise HTTPException(status_code=400, detail="Invalid report type for export")
        
        # Convert to CSV
        return df.to_csv(index=False)

    async def get_report_metrics(
        self,
        report_type: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get metrics for different report types"""
        if report_type == "transactions":
            return await self._get_transaction_metrics(start_date, end_date)
        elif report_type == "user_activity":
            return await self._get_user_activity_metrics(start_date, end_date)
        else:
            raise HTTPException(status_code=400, detail="Invalid report type")

    async def _get_transaction_metrics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get transaction-related metrics"""
        # Get transaction counts by type
        type_counts = (
            self.db.query(
                Transaction.type,
                func.count(Transaction.id).label('count')
            )
            .filter(
                and_(
                    Transaction.created_at >= start_date,
                    Transaction.created_at <= end_date
                )
            )
            .group_by(Transaction.type)
            .all()
        )
        
        # Get average transaction amounts by type
        avg_amounts = (
            self.db.query(
                Transaction.type,
                func.avg(Transaction.amount).label('average')
            )
            .filter(
                and_(
                    Transaction.created_at >= start_date,
                    Transaction.created_at <= end_date
                )
            )
            .group_by(Transaction.type)
            .all()
        )
        
        return {
            "type_counts": dict(type_counts),
            "average_amounts": {t: float(avg) for t, avg in avg_amounts}
        }

    async def _get_user_activity_metrics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get user activity metrics"""
        # Get daily active users
        daily_active = (
            self.db.query(
                func.date(User.last_login).label('date'),
                func.count(User.id).label('count')
            )
            .filter(
                and_(
                    User.last_login >= start_date,
                    User.last_login <= end_date
                )
            )
            .group_by(func.date(User.last_login))
            .all()
        )
        
        return {
            "daily_active_users": {
                str(date): count for date, count in daily_active
            }
        }
