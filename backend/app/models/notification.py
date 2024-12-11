from sqlalchemy import Column, Integer, String, JSON, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from .base import TimestampedBase
import enum

class NotificationType(str, Enum):
    TRANSACTION = "transaction"
    SECURITY = "security"
    ACCOUNT = "account"
    COMPLIANCE = "compliance"
    SUSTAINABILITY = "sustainability"
    REGULATORY = "regulatory"
    ETHICAL = "ethical"
    SYSTEM = "system"
    MARKETING = "marketing"

class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    ALL = "all"

class Notification(TimestampedBase):
    __tablename__ = "notifications"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.LOW)
    content = Column(JSON, nullable=False)
    read = Column(Boolean, default=False)
    
    # Optional fields for tracking delivery status
    email_sent = Column(Boolean, default=False)
    sms_sent = Column(Boolean, default=False)
    push_sent = Column(Boolean, default=False)
    
    # Error tracking
    delivery_errors = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification {self.id}: {self.type.value} - {self.priority.value}>"
