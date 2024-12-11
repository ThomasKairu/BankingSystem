from typing import Dict, Optional, List, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy import func
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.models.user import User
from app.models.auth import AuthDevice
import json
from decimal import Decimal

class FraudDetectionService:
    def __init__(self, db: Session):
        self.db = db

    async def analyze_transaction(
        self,
        user_id: int,
        amount: Decimal,
        transaction_type: TransactionType,
        device_info: Dict[str, Any]
    ) -> float:
        """
        Analyze a transaction for potential fraud.
        Returns a risk score between 0 and 1.
        """
        risk_factors = []
        risk_score = 0.0
        
        # Get user's transaction history
        recent_transactions = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.created_at >= datetime.utcnow() - timedelta(days=30)
        ).all()
        
        # 1. Amount Analysis (30% of total score)
        risk_score += self._analyze_amount(amount, recent_transactions) * 0.3
        
        # 2. Frequency Analysis (20% of total score)
        risk_score += self._analyze_frequency(user_id) * 0.2
        
        # 3. Device Analysis (25% of total score)
        risk_score += self._analyze_device(user_id, device_info) * 0.25
        
        # 4. Pattern Analysis (25% of total score)
        risk_score += self._analyze_patterns(
            user_id, amount, transaction_type, recent_transactions
        ) * 0.25
        
        return min(risk_score, 1.0)

    def _analyze_amount(self, amount: Decimal, history: List[Transaction]) -> float:
        """Analyze transaction amount against user history."""
        if not history:
            return 0.5  # Moderate risk for new users
        
        avg_amount = sum(t.amount for t in history) / len(history)
        max_amount = max(t.amount for t in history)
        
        # Calculate how many standard deviations from mean
        if len(history) > 1:
            std_dev = (sum((t.amount - avg_amount) ** 2 for t in history) / (len(history) - 1)) ** 0.5
            z_score = (amount - avg_amount) / std_dev if std_dev > 0 else 0
        else:
            z_score = 0
        
        # Risk increases with amount deviation
        if amount > max_amount:
            return min(1.0, (amount / max_amount) * 0.8)
        elif z_score > 2:  # More than 2 standard deviations
            return min(1.0, z_score * 0.2)
        
        return 0.0

    def _analyze_frequency(self, user_id: int) -> float:
        """Analyze transaction frequency."""
        # Count transactions in the last hour
        recent_count = self.db.query(func.count(Transaction.id)).filter(
            Transaction.user_id == user_id,
            Transaction.created_at >= datetime.utcnow() - timedelta(hours=1)
        ).scalar()
        
        # Get user's typical hourly frequency
        typical_count = self.db.query(func.count(Transaction.id)).filter(
            Transaction.user_id == user_id,
            Transaction.created_at >= datetime.utcnow() - timedelta(days=7)
        ).scalar() / (24 * 7)  # Average per hour
        
        if typical_count == 0:
            return 0.5 if recent_count > 3 else 0.0
        
        frequency_ratio = recent_count / typical_count
        return min(1.0, frequency_ratio * 0.2)

    def _analyze_device(self, user_id: int, device_info: Dict[str, Any]) -> float:
        """Analyze device information."""
        # Check if device is known
        known_device = self.db.query(AuthDevice).filter(
            AuthDevice.user_id == user_id,
            AuthDevice.device_id == device_info.get("device_id")
        ).first()
        
        if not known_device:
            return 0.8  # High risk for unknown devices
        
        # Check if device fingerprint matches
        if known_device.fingerprint != device_info.get("fingerprint"):
            return 0.9  # Very high risk for mismatched fingerprint
        
        # Check last use of device
        if datetime.utcnow() - known_device.last_used > timedelta(days=30):
            return 0.4  # Moderate risk for long-unused devices
        
        return 0.0

    def _analyze_patterns(
        self,
        user_id: int,
        amount: Decimal,
        transaction_type: TransactionType,
        history: List[Transaction]
    ) -> float:
        """Analyze transaction patterns."""
        risk_score = 0.0
        
        # Check for rapid successive transactions
        recent_similar = [
            t for t in history
            if t.type == transaction_type
            and t.created_at >= datetime.utcnow() - timedelta(minutes=5)
        ]
        
        if len(recent_similar) > 2:
            risk_score += 0.3
        
        # Check for unusual transaction type frequency
        type_frequency = {}
        for t in history:
            type_frequency[t.type] = type_frequency.get(t.type, 0) + 1
        
        total_transactions = len(history) if history else 1
        type_ratio = type_frequency.get(transaction_type, 0) / total_transactions
        
        if type_ratio < 0.1:  # Unusual transaction type
            risk_score += 0.2
        
        # Check for round amounts (often associated with fraud)
        if amount % 100 == 0 and amount > 1000:
            risk_score += 0.1
        
        return min(risk_score, 1.0)

    async def get_user_risk_profile(self, user_id: int) -> Dict[str, Any]:
        """Get a user's risk profile based on their transaction history."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"risk_level": "unknown"}
        
        # Get transaction history
        transactions = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.created_at >= datetime.utcnow() - timedelta(days=90)
        ).all()
        
        if not transactions:
            return {"risk_level": "new_user"}
        
        # Calculate risk metrics
        total_transactions = len(transactions)
        failed_transactions = len([t for t in transactions if t.status == TransactionStatus.FAILED])
        high_risk_transactions = len([
            t for t in transactions
            if getattr(t, "risk_score", 0) > 0.7
        ])
        
        # Calculate risk level
        risk_ratio = (failed_transactions + high_risk_transactions) / total_transactions
        
        if risk_ratio > 0.2:
            risk_level = "high"
        elif risk_ratio > 0.1:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "risk_level": risk_level,
            "total_transactions": total_transactions,
            "failed_transactions": failed_transactions,
            "high_risk_transactions": high_risk_transactions,
            "risk_ratio": risk_ratio,
            "last_analysis": datetime.utcnow().isoformat()
        }
