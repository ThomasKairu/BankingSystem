from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_admin_user
from app.schemas.admin import (
    SystemStats,
    UserStats,
    TransactionStats,
    SecurityStats,
    AdminUserUpdate
)
from app.models.user import User
from app.models.transaction import Transaction
from app.models.account import Account
from app.core.monitoring import monitoring
from app.core.security_middleware import security_middleware
from app.core.rate_limiter import rate_limiter

router = APIRouter()

@router.get("/stats/system", response_model=SystemStats)
async def get_system_stats(
    current_admin: User = Depends(get_current_admin_user)
):
    """Get system-wide statistics"""
    return {
        "active_users": monitoring.get_active_users_count(),
        "requests_per_minute": monitoring.get_requests_per_minute(),
        "error_rate": monitoring.get_error_rate(),
        "average_response_time": monitoring.get_average_response_time()
    }

@router.get("/stats/users", response_model=UserStats)
async def get_user_stats(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
    time_range: str = Query("24h", regex="^(24h|7d|30d)$")
):
    """Get user-related statistics"""
    time_ranges = {
        "24h": timedelta(hours=24),
        "7d": timedelta(days=7),
        "30d": timedelta(days=30)
    }
    since = datetime.utcnow() - time_ranges[time_range]
    
    return {
        "total_users": db.query(User).count(),
        "new_users": db.query(User).filter(User.created_at >= since).count(),
        "active_users": db.query(User).filter(User.last_login >= since).count(),
        "verified_users": db.query(User).filter(User.is_verified == True).count()
    }

@router.get("/stats/transactions", response_model=TransactionStats)
async def get_transaction_stats(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
    time_range: str = Query("24h", regex="^(24h|7d|30d)$")
):
    """Get transaction-related statistics"""
    time_ranges = {
        "24h": timedelta(hours=24),
        "7d": timedelta(days=7),
        "30d": timedelta(days=30)
    }
    since = datetime.utcnow() - time_ranges[time_range]
    
    return {
        "total_transactions": db.query(Transaction).filter(Transaction.created_at >= since).count(),
        "total_volume": db.query(Transaction).filter(Transaction.created_at >= since).with_entities(
            func.sum(Transaction.amount)
        ).scalar() or 0,
        "successful_transactions": db.query(Transaction).filter(
            Transaction.created_at >= since,
            Transaction.status == "completed"
        ).count(),
        "failed_transactions": db.query(Transaction).filter(
            Transaction.created_at >= since,
            Transaction.status == "failed"
        ).count()
    }

@router.get("/stats/security", response_model=SecurityStats)
async def get_security_stats(
    current_admin: User = Depends(get_current_admin_user)
):
    """Get security-related statistics"""
    return {
        "blocked_ips": security_middleware.get_blocked_ips_count(),
        "rate_limited_requests": rate_limiter.get_rate_limited_count(),
        "suspicious_activities": security_middleware.get_suspicious_activities_count(),
        "failed_login_attempts": monitoring.get_failed_login_attempts()
    }

@router.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_update: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Update user details (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

@router.get("/audit-logs")
async def get_audit_logs(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
    skip: int = 0,
    limit: int = 100
):
    """Get system audit logs"""
    return monitoring.get_audit_logs(skip=skip, limit=limit)

@router.post("/users/{user_id}/block")
async def block_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Block a user account"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = False
    db.commit()
    return {"message": "User blocked successfully"}

@router.post("/users/{user_id}/unblock")
async def unblock_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Unblock a user account"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = True
    db.commit()
    return {"message": "User unblocked successfully"}
