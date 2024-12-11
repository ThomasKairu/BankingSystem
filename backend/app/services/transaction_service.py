from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from fastapi import HTTPException
import uuid

from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.models.account import Account, AccountStatus
from app.services.notification_service import NotificationService
from app.core.security import get_current_user_id
from app.schemas.transaction import TransactionCreate, TransactionResponse

class TransactionService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService()

    async def create_transaction(
        self,
        transaction_data: TransactionCreate,
        user_id: int,
        device_info: Dict
    ) -> Transaction:
        # Validate account
        account = self.db.query(Account).filter(
            Account.id == transaction_data.account_id,
            Account.user_id == user_id
        ).first()
        
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        if account.status != AccountStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="Account is not active")

        # Create transaction
        transaction = Transaction(
            reference_id=str(uuid.uuid4()),
            user_id=user_id,
            account_id=transaction_data.account_id,
            type=transaction_data.type,
            amount=transaction_data.amount,
            currency=account.currency,
            description=transaction_data.description,
            category=transaction_data.category,
            recipient_account=transaction_data.recipient_account,
            recipient_bank=transaction_data.recipient_bank,
            device_info=device_info,
            merchant_info=transaction_data.merchant_info
        )

        # Validate transaction limits
        self._validate_transaction_limits(account, transaction)
        
        # Process based on transaction type
        if transaction.type == TransactionType.WITHDRAWAL:
            await self._process_withdrawal(transaction, account)
        elif transaction.type == TransactionType.DEPOSIT:
            await self._process_deposit(transaction, account)
        elif transaction.type == TransactionType.TRANSFER:
            await self._process_transfer(transaction, account)
        
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        
        # Send notification
        await self.notification_service.send_transaction_notification(transaction)
        
        return transaction

    def _validate_transaction_limits(self, account: Account, transaction: Transaction):
        """Validate transaction against account limits."""
        if transaction.type == TransactionType.WITHDRAWAL:
            if transaction.amount > account.withdrawal_limit:
                raise HTTPException(
                    status_code=400,
                    detail=f"Amount exceeds withdrawal limit of {account.withdrawal_limit}"
                )
            
        # Check daily transfer limit
        if transaction.type == TransactionType.TRANSFER:
            today_transfers = self.db.query(Transaction).filter(
                Transaction.account_id == account.id,
                Transaction.type == TransactionType.TRANSFER,
                Transaction.created_at >= datetime.now().date()
            ).all()
            
            total_transfers = sum(t.amount for t in today_transfers)
            if total_transfers + transaction.amount > account.daily_transfer_limit:
                raise HTTPException(
                    status_code=400,
                    detail=f"Amount exceeds daily transfer limit of {account.daily_transfer_limit}"
                )

    async def _process_withdrawal(self, transaction: Transaction, account: Account):
        """Process a withdrawal transaction."""
        if account.balance < transaction.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        
        account.balance -= transaction.amount
        transaction.status = TransactionStatus.COMPLETED
        transaction.processed_at = datetime.utcnow()

    async def _process_deposit(self, transaction: Transaction, account: Account):
        """Process a deposit transaction."""
        account.balance += transaction.amount
        transaction.status = TransactionStatus.COMPLETED
        transaction.processed_at = datetime.utcnow()

    async def _process_transfer(self, transaction: Transaction, account: Account):
        """Process a transfer transaction."""
        if account.balance < transaction.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        
        # Find recipient account
        recipient_account = self.db.query(Account).filter(
            Account.account_number == transaction.recipient_account
        ).first()
        
        if not recipient_account:
            raise HTTPException(status_code=404, detail="Recipient account not found")
        
        if recipient_account.status != AccountStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="Recipient account is not active")
        
        # Process transfer
        account.balance -= transaction.amount
        recipient_account.balance += transaction.amount
        transaction.status = TransactionStatus.COMPLETED
        transaction.processed_at = datetime.utcnow()

    async def get_transaction(self, transaction_id: str, user_id: int) -> Transaction:
        """Get a specific transaction."""
        transaction = self.db.query(Transaction).filter(
            Transaction.reference_id == transaction_id,
            Transaction.user_id == user_id
        ).first()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        return transaction

    async def get_user_transactions(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        account_id: Optional[int] = None,
        transaction_type: Optional[TransactionType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Transaction]:
        """Get user transactions with optional filters."""
        query = self.db.query(Transaction).filter(Transaction.user_id == user_id)
        
        if account_id:
            query = query.filter(Transaction.account_id == account_id)
        if transaction_type:
            query = query.filter(Transaction.type == transaction_type)
        if start_date:
            query = query.filter(Transaction.created_at >= start_date)
        if end_date:
            query = query.filter(Transaction.created_at <= end_date)
        
        return query.order_by(Transaction.created_at.desc()).offset(skip).limit(limit).all()

    async def cancel_transaction(self, transaction_id: str, user_id: int) -> Transaction:
        """Cancel a pending transaction."""
        transaction = await self.get_transaction(transaction_id, user_id)
        
        if transaction.status != TransactionStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail="Only pending transactions can be cancelled"
            )
        
        transaction.status = TransactionStatus.CANCELLED
        self.db.commit()
        self.db.refresh(transaction)
        
        await self.notification_service.send_transaction_notification(transaction)
        
        return transaction
