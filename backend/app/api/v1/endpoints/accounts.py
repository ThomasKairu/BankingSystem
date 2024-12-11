from typing import Any, List
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_current_active_user, get_db
from app.services.account import AccountService
from app.schemas.account import (
    Account,
    AccountCreate,
    AccountUpdate,
    AccountBalance,
    AccountTransaction,
    AccountLimits
)
from app.models.user import User as UserModel
from app.models.account import AccountStatus

router = APIRouter()

@router.post("/", response_model=Account)
def create_account(
    *,
    db: Session = Depends(get_db),
    account_in: AccountCreate,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """
    Create new account for current user.
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=400,
            detail="User must be verified to create an account",
        )
    
    account = AccountService.create(
        db,
        user_id=current_user.id,
        type=account_in.type,
        currency=account_in.currency,
        initial_balance=account_in.initial_balance
    )
    return account

@router.get("/", response_model=List[Account])
def read_accounts(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve accounts.
    """
    accounts = AccountService.get_user_accounts(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return accounts

@router.get("/{account_id}", response_model=Account)
def read_account(
    *,
    db: Session = Depends(get_db),
    account_id: int,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """
    Get account by ID.
    """
    account = AccountService.get(db, account_id=account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if account.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return account

@router.post("/{account_id}/transaction", response_model=Account)
def process_transaction(
    *,
    db: Session = Depends(get_db),
    account_id: int,
    transaction: AccountTransaction,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """
    Process a transaction (credit/debit) for an account.
    """
    account = AccountService.get(db, account_id=account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if account.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    if account.status != AccountStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Account is not active")
    
    try:
        account = AccountService.update_balance(
            db,
            account_id=account_id,
            amount=transaction.amount,
            operation=transaction.operation
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return account

@router.get("/{account_id}/balance", response_model=AccountBalance)
def read_balance(
    *,
    db: Session = Depends(get_db),
    account_id: int,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """
    Get account balance.
    """
    account = AccountService.get(db, account_id=account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if account.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return {"balance": account.balance}

@router.put("/{account_id}/status", response_model=Account)
def update_account_status(
    *,
    db: Session = Depends(get_db),
    account_id: int,
    status: AccountStatus,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """
    Update account status.
    """
    account = AccountService.get(db, account_id=account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if account.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    account = AccountService.update_status(
        db,
        account_id=account_id,
        status=status
    )
    return account

@router.put("/{account_id}/limits", response_model=Account)
def update_account_limits(
    *,
    db: Session = Depends(get_db),
    account_id: int,
    limits: AccountLimits,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """
    Update account limits.
    """
    account = AccountService.get(db, account_id=account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if account.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    account = AccountService.update_limits(
        db,
        account_id=account_id,
        daily_transfer_limit=limits.daily_transfer_limit,
        withdrawal_limit=limits.withdrawal_limit
    )
    return account
