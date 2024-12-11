from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from app.models.account import Account, AccountType, AccountStatus
from app.models.user import User
import uuid
from decimal import Decimal

class AccountService:
    @staticmethod
    def get(db: Session, account_id: int) -> Optional[Account]:
        return db.query(Account).filter(Account.id == account_id).first()

    @staticmethod
    def get_by_account_number(db: Session, account_number: str) -> Optional[Account]:
        return db.query(Account).filter(Account.account_number == account_number).first()

    @staticmethod
    def get_user_accounts(
        db: Session, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Account]:
        return (
            db.query(Account)
            .filter(Account.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def create(
        db: Session,
        *,
        user_id: int,
        type: AccountType,
        currency: str = "USD",
        initial_balance: Decimal = Decimal("0")
    ) -> Account:
        account_number = str(uuid.uuid4().int)[:12]
        db_obj = Account(
            account_number=account_number,
            user_id=user_id,
            type=type,
            status=AccountStatus.ACTIVE,
            balance=initial_balance,
            currency=currency,
            daily_transfer_limit=Decimal("10000"),
            withdrawal_limit=Decimal("5000"),
            interest_rate=Decimal("0.01"),
            features={
                "debit_card": True,
                "online_banking": True,
                "mobile_banking": True
            },
            metadata={
                "created_through": "api",
                "risk_assessment": "low"
            }
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def update_balance(
        db: Session,
        *,
        account_id: int,
        amount: Decimal,
        operation: str
    ) -> Account:
        account = AccountService.get(db, account_id=account_id)
        if operation == "credit":
            account.balance += amount
        elif operation == "debit":
            if account.balance < amount:
                raise ValueError("Insufficient funds")
            account.balance -= amount
        
        db.add(account)
        db.commit()
        db.refresh(account)
        return account

    @staticmethod
    def update_status(
        db: Session,
        *,
        account_id: int,
        status: AccountStatus
    ) -> Account:
        account = AccountService.get(db, account_id=account_id)
        account.status = status
        db.add(account)
        db.commit()
        db.refresh(account)
        return account

    @staticmethod
    def update_limits(
        db: Session,
        *,
        account_id: int,
        daily_transfer_limit: Optional[Decimal] = None,
        withdrawal_limit: Optional[Decimal] = None
    ) -> Account:
        account = AccountService.get(db, account_id=account_id)
        
        if daily_transfer_limit is not None:
            account.daily_transfer_limit = daily_transfer_limit
        if withdrawal_limit is not None:
            account.withdrawal_limit = withdrawal_limit
            
        db.add(account)
        db.commit()
        db.refresh(account)
        return account

    @staticmethod
    def delete(db: Session, *, account_id: int) -> Account:
        obj = db.query(Account).get(account_id)
        db.delete(obj)
        db.commit()
        return obj
