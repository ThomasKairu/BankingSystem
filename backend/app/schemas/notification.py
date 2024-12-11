from typing import Dict, Optional, List, Any
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.notification import NotificationType, NotificationPriority, NotificationChannel

class NotificationBase(BaseModel):
    type: NotificationType
    priority: NotificationPriority
    content: Dict[str, Any]
    read: bool = False
    channel: Optional[NotificationChannel] = NotificationChannel.ALL

class NotificationCreate(NotificationBase):
    user_id: int

class NotificationUpdate(BaseModel):
    read: Optional[bool] = None
    channel_preferences: Optional[List[NotificationChannel]] = None

class Notification(NotificationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ComplianceNotification(NotificationBase):
    alert_type: str
    details: Dict[str, Any]
    recommendations: Optional[List[str]]

class SustainabilityNotification(NotificationBase):
    metrics: Dict[str, Any]
    impact_level: str
    recommendations: List[str]

class EthicalComplianceNotification(NotificationBase):
    violation_type: Optional[str]
    industry_check: Dict[str, Any]
    environmental_impact: Dict[str, Any]
    social_responsibility: Dict[str, Any]

class NotificationPreferences(BaseModel):
    email_enabled: bool = True
    sms_enabled: bool = True
    push_enabled: bool = True
    compliance_alerts: bool = True
    sustainability_updates: bool = True
    ethical_alerts: bool = True
    minimum_priority: NotificationPriority = NotificationPriority.LOW
    transaction_alerts: bool = Field(True, description="Receive transaction notifications")
    security_alerts: bool = Field(True, description="Receive security alerts")
    marketing_notifications: bool = Field(False, description="Receive marketing notifications")
    minimum_amount: float = Field(0.0, description="Minimum amount for transaction notifications")
    quiet_hours_start: int = Field(22, ge=0, le=23, description="Start of quiet hours (24h format)")
    quiet_hours_end: int = Field(7, ge=0, le=23, description="End of quiet hours (24h format)")
    
    class Config:
        schema_extra = {
            "example": {
                "email_enabled": True,
                "sms_enabled": True,
                "push_enabled": True,
                "compliance_alerts": True,
                "sustainability_updates": True,
                "ethical_alerts": True,
                "minimum_priority": NotificationPriority.LOW,
                "transaction_alerts": True,
                "security_alerts": True,
                "marketing_notifications": False,
                "minimum_amount": 100.0,
                "quiet_hours_start": 22,
                "quiet_hours_end": 7
            }
        }
