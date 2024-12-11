from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from decimal import Decimal
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.services.account import AccountService
import uuid
import json

class TransactionService:
    @staticmethod
    def get(db: Session, transaction_id: int) -> Optional[Transaction]:
        return db.query(Transaction).filter(Transaction.id == transaction_id).first()

    @staticmethod
    def get_by_reference(db: Session, reference_id: str) -> Optional[Transaction]:
        return db.query(Transaction).filter(Transaction.reference_id == reference_id).first()

    @staticmethod
    def get_account_transactions(
        db: Session,
        account_id: int,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        transaction_type: Optional[TransactionType] = None
    ) -> List[Transaction]:
        query = db.query(Transaction).filter(Transaction.account_id == account_id)
        
        if start_date:
            query = query.filter(Transaction.created_at >= start_date)
        if end_date:
            query = query.filter(Transaction.created_at <= end_date)
        if transaction_type:
            query = query.filter(Transaction.type == transaction_type)
            
        return query.order_by(desc(Transaction.created_at)).offset(skip).limit(limit).all()

    @staticmethod
    def create_transaction(
        db: Session,
        *,
        user_id: int,
        account_id: int,
        amount: Decimal,
        transaction_type: TransactionType,
        description: str,
        metadata: Dict = None,
        ip_address: Optional[str] = None,
        device_info: Optional[Dict] = None,
        location_info: Optional[Dict] = None
    ) -> Transaction:
        reference_id = str(uuid.uuid4())
        
        # Create transaction record
        db_obj = Transaction(
            reference_id=reference_id,
            user_id=user_id,
            account_id=account_id,
            type=transaction_type,
            status=TransactionStatus.PENDING,
            amount=amount,
            description=description,
            metadata=metadata or {},
            ip_address=ip_address,
            device_info=device_info,
            location_info=location_info,
            risk_score=0  # Will be updated by fraud detection service
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj

    @staticmethod
    def process_transaction(
        db: Session,
        *,
        transaction_id: int,
        risk_score: int = 0
    ) -> Transaction:
        transaction = TransactionService.get(db, transaction_id=transaction_id)
        
        try:
            # Update account balance
            operation = "debit" if transaction.type in [
                TransactionType.WITHDRAWAL,
                TransactionType.TRANSFER,
                TransactionType.PAYMENT
            ] else "credit"
            
            AccountService.update_balance(
                db,
                account_id=transaction.account_id,
                amount=transaction.amount,
                operation=operation
            )
            
            # Update transaction status
            transaction.status = TransactionStatus.COMPLETED
            transaction.processed_at = datetime.utcnow()
            transaction.risk_score = risk_score
            
        except Exception as e:
            transaction.status = TransactionStatus.FAILED
            transaction.failure_reason = str(e)
            
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        return transaction

    @staticmethod
    def flag_suspicious_transaction(
        db: Session,
        *,
        transaction_id: int,
        reason: str
    ) -> Transaction:
        transaction = TransactionService.get(db, transaction_id=transaction_id)
        transaction.status = TransactionStatus.FLAGGED
        transaction.metadata = {
            **transaction.metadata,
            "flag_reason": reason,
            "flagged_at": datetime.utcnow().isoformat()
        }
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        return transaction

    @staticmethod
    def get_transaction_statistics(
        db: Session,
        account_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        transactions = TransactionService.get_account_transactions(
            db,
            account_id=account_id,
            start_date=start_date,
            end_date=end_date,
            limit=1000  # Increased limit for statistics
        )
        
        stats = {
            "total_transactions": len(transactions),
            "total_credits": sum(
                t.amount for t in transactions 
                if t.type in [TransactionType.DEPOSIT, TransactionType.INTEREST]
                and t.status == TransactionStatus.COMPLETED
            ),
            "total_debits": sum(
                t.amount for t in transactions
                if t.type in [TransactionType.WITHDRAWAL, TransactionType.PAYMENT]
                and t.status == TransactionStatus.COMPLETED
            ),
            "transaction_types": {},
            "status_distribution": {},
            "average_transaction_size": 0,
            "high_risk_transactions": len([
                t for t in transactions if t.risk_score > 70
            ])
        }
        
        # Calculate type and status distributions
        for t in transactions:
            stats["transaction_types"][t.type.value] = \
                stats["transaction_types"].get(t.type.value, 0) + 1
            stats["status_distribution"][t.status.value] = \
                stats["status_distribution"].get(t.status.value, 0) + 1
        
        # Calculate average transaction size
        if transactions:
            stats["average_transaction_size"] = sum(
                t.amount for t in transactions
            ) / len(transactions)
        
        return stats
