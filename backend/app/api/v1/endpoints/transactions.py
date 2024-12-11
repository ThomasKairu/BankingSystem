from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.core.deps import get_current_active_user, get_db
from app.services.transaction_service import TransactionService
from app.services.fraud_detection import FraudDetectionService
from app.services.notification_service import NotificationService
from app.models.user import User as UserModel
from app.models.transaction import TransactionType, TransactionStatus, Transaction
from app.schemas.transaction import TransactionCreate, TransactionResponse, TransactionStatistics
from decimal import Decimal

router = APIRouter()

@router.post("/", response_model=TransactionResponse)
async def create_transaction(
    *,
    db: Session = Depends(get_db),
    transaction_in: TransactionCreate,
    current_user: UserModel = Depends(get_current_active_user),
    request: Request
) -> Any:
    """
    Create new transaction.
    """
    # Get device info from request
    device_info = {
        "ip_address": request.client.host,
        "user_agent": request.headers.get("User-Agent"),
        "device_id": request.headers.get("X-Device-ID"),
        "device_type": request.headers.get("X-Device-Type")
    }
    
    # Initialize services
    transaction_service = TransactionService(db)
    fraud_service = FraudDetectionService(db)
    
    # Perform fraud check
    fraud_score = await fraud_service.analyze_transaction(
        user_id=current_user.id,
        amount=transaction_in.amount,
        transaction_type=transaction_in.transaction_type,
        device_info=device_info
    )
    
    if fraud_score > 0.8:  # High risk threshold
        raise HTTPException(
            status_code=400,
            detail="Transaction flagged as potentially fraudulent"
        )
    
    # Create transaction
    transaction = await transaction_service.create_transaction(
        transaction_data=transaction_in,
        user_id=current_user.id,
        device_info=device_info
    )
    
    return transaction

@router.get("/account/{account_id}", response_model=List[TransactionResponse])
async def read_account_transactions(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    transaction_type: Optional[TransactionType] = None,
) -> Any:
    """
    Retrieve account transactions with optional filters.
    """
    transaction_service = TransactionService(db)
    transactions = await transaction_service.get_user_transactions(
        user_id=current_user.id,
        account_id=account_id,
        skip=skip,
        limit=limit,
        transaction_type=transaction_type,
        start_date=start_date,
        end_date=end_date
    )
    return transactions

@router.get("/statistics/{account_id}", response_model=TransactionStatistics)
async def get_transaction_statistics(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
    days: int = Query(default=30, ge=1, le=365)
) -> Any:
    """
    Get transaction statistics for an account.
    """
    transaction_service = TransactionService(db)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    transactions = await transaction_service.get_user_transactions(
        user_id=current_user.id,
        account_id=account_id,
        start_date=start_date
    )
    
    # Calculate statistics
    total_transactions = len(transactions)
    total_deposits = sum(t.amount for t in transactions if t.type == TransactionType.DEPOSIT)
    total_withdrawals = sum(t.amount for t in transactions if t.type == TransactionType.WITHDRAWAL)
    total_transfers = sum(t.amount for t in transactions if t.type == TransactionType.TRANSFER)
    
    return {
        "total_transactions": total_transactions,
        "total_deposits": total_deposits,
        "total_withdrawals": total_withdrawals,
        "total_transfers": total_transfers,
        "net_flow": total_deposits - total_withdrawals,
        "period_days": days
    }

@router.post("/{transaction_id}/cancel")
async def cancel_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
) -> Any:
    """
    Cancel a pending transaction.
    """
    transaction_service = TransactionService(db)
    return await transaction_service.cancel_transaction(
        transaction_id=transaction_id,
        user_id=current_user.id
    )

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
) -> Any:
    """
    Get specific transaction details.
    """
    transaction_service = TransactionService(db)
    return await transaction_service.get_transaction(
        transaction_id=transaction_id,
        user_id=current_user.id
    )
