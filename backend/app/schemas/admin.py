from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class SystemStats(BaseModel):
    active_users: int
    requests_per_minute: float
    error_rate: float
    average_response_time: float

class UserStats(BaseModel):
    total_users: int
    new_users: int
    active_users: int
    verified_users: int

class TransactionStats(BaseModel):
    total_transactions: int
    total_volume: float
    successful_transactions: int
    failed_transactions: int

class SecurityStats(BaseModel):
    blocked_ips: int
    rate_limited_requests: int
    suspicious_activities: int
    failed_login_attempts: int

class AdminUserUpdate(BaseModel):
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    role: Optional[str] = None
    email: Optional[str] = None
    
    class Config:
        from_attributes = True

class AuditLog(BaseModel):
    id: int
    timestamp: datetime
    user_id: Optional[int]
    action: str
    details: str
    ip_address: Optional[str]
    
    class Config:
        from_attributes = True
