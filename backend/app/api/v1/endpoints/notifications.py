from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_current_active_user, get_db
from app.models.user import User as UserModel
from app.models.notification import Notification, NotificationType
from app.schemas.notification import NotificationResponse, NotificationUpdate, NotificationPreferences

router = APIRouter()

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    *,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    notification_type: Optional[NotificationType] = None,
    unread_only: bool = False
):
    """Get user notifications with optional filters."""
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    
    if notification_type:
        query = query.filter(Notification.type == notification_type)
    if unread_only:
        query = query.filter(Notification.read == False)
    
    notifications = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    return notifications

@router.get("/unread-count")
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get count of unread notifications."""
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.read == False
    ).count()
    return {"unread_count": count}

@router.post("/{notification_id}/mark-read")
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Mark a notification as read."""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.read = True
    db.commit()
    return {"status": "success"}

@router.post("/mark-all-read")
async def mark_all_read(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Mark all notifications as read."""
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.read == False
    ).update({"read": True})
    
    db.commit()
    return {"status": "success"}

@router.put("/preferences", response_model=NotificationPreferences)
async def update_notification_preferences(
    *,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
    preferences: NotificationPreferences
):
    """Update notification preferences."""
    current_user.notification_preferences = preferences.dict()
    db.commit()
    return preferences

@router.get("/preferences", response_model=NotificationPreferences)
async def get_notification_preferences(
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get current notification preferences."""
    return NotificationPreferences(**current_user.notification_preferences)
