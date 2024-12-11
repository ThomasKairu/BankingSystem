from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
from app.core.config import settings
from app.models.user import User
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.models.notification import Notification, NotificationType, NotificationPriority
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

class NotificationService:
    def __init__(self):
        self.email_sender = settings.SMTP_SENDER
        self.email_password = settings.SMTP_PASSWORD
        self.sms_api_key = settings.SMS_API_KEY
        self.push_api_key = settings.PUSH_API_KEY

    async def send_transaction_notification(
        self,
        transaction: Transaction,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> None:
        """Send notification for transaction events."""
        user = transaction.user

        # Prepare notification content
        content = self._prepare_transaction_content(transaction)
        
        # Determine notification priority
        priority = self._determine_priority(transaction)
        
        # Create notification record
        notification = Notification(
            user_id=user.id,
            type=NotificationType.TRANSACTION,
            priority=priority,
            content=content,
            read=False
        )
        
        # Send notifications based on user preferences
        if background_tasks:
            background_tasks.add_task(self._send_notifications, user, notification)
        else:
            await self._send_notifications(user, notification)

    async def send_security_alert(
        self,
        user: User,
        alert_type: str,
        details: Dict[str, Any],
        background_tasks: Optional[BackgroundTasks] = None
    ) -> None:
        """Send security-related notifications."""
        content = self._prepare_security_content(alert_type, details)
        
        notification = Notification(
            user_id=user.id,
            type=NotificationType.SECURITY,
            priority=NotificationPriority.HIGH,
            content=content,
            read=False
        )
        
        if background_tasks:
            background_tasks.add_task(self._send_notifications, user, notification)
        else:
            await self._send_notifications(user, notification)

    async def send_account_notification(
        self,
        user: User,
        notification_type: str,
        details: Dict[str, Any],
        background_tasks: Optional[BackgroundTasks] = None
    ) -> None:
        """Send account-related notifications."""
        content = self._prepare_account_content(notification_type, details)
        
        notification = Notification(
            user_id=user.id,
            type=NotificationType.ACCOUNT,
            priority=NotificationPriority.MEDIUM,
            content=content,
            read=False
        )
        
        if background_tasks:
            background_tasks.add_task(self._send_notifications, user, notification)
        else:
            await self._send_notifications(user, notification)

    async def send_compliance_alert(
        self,
        user: User,
        alert_type: str,
        details: Dict[str, Any],
        priority: NotificationPriority = NotificationPriority.HIGH,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> None:
        """Send compliance-related alerts."""
        content = self._prepare_compliance_content(alert_type, details)
        
        notification = Notification(
            user_id=user.id,
            type=NotificationType.COMPLIANCE,
            priority=priority,
            content=content,
            read=False
        )
        
        if background_tasks:
            background_tasks.add_task(self._send_notifications, user, notification)
        else:
            await self._send_notifications(user, notification)

    async def send_sustainability_update(
        self,
        user: User,
        metrics: Dict[str, Any],
        background_tasks: Optional[BackgroundTasks] = None
    ) -> None:
        """Send sustainability metrics updates."""
        content = self._prepare_sustainability_content(metrics)
        
        notification = Notification(
            user_id=user.id,
            type=NotificationType.SUSTAINABILITY,
            priority=NotificationPriority.MEDIUM,
            content=content,
            read=False
        )
        
        if background_tasks:
            background_tasks.add_task(self._send_notifications, user, notification)
        else:
            await self._send_notifications(user, notification)

    def _prepare_transaction_content(self, transaction: Transaction) -> Dict[str, Any]:
        """Prepare content for transaction notifications."""
        amount_str = f"{transaction.amount} {transaction.currency}"
        
        content = {
            "title": f"Transaction {transaction.status.value}",
            "transaction_id": transaction.reference_id,
            "amount": amount_str,
            "type": transaction.type.value,
            "status": transaction.status.value,
            "timestamp": transaction.created_at.isoformat(),
            "description": transaction.description
        }
        
        if transaction.type == TransactionType.TRANSFER:
            content["recipient"] = transaction.recipient_account
            
        if transaction.merchant_info:
            content["merchant"] = transaction.merchant_info
            
        return content

    def _prepare_security_content(self, alert_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare content for security notifications."""
        return {
            "title": f"Security Alert: {alert_type}",
            "type": alert_type,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
            "action_required": True
        }

    def _prepare_account_content(self, notification_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare content for account notifications."""
        return {
            "title": f"Account Update: {notification_type}",
            "type": notification_type,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }

    def _prepare_compliance_content(self, alert_type: str, details: Dict[str, Any]) -> str:
        """Prepare compliance alert content."""
        templates = {
            "kyc_required": "Action Required: Please complete your KYC verification. {details}",
            "kyc_approved": "Your KYC verification has been approved.",
            "kyc_rejected": "Your KYC verification was not approved. Reason: {reason}",
            "risk_level_change": "Your account risk level has changed to {level}. {details}",
            "suspicious_activity": "Suspicious activity detected on your account. {details}",
            "regulatory_update": "Important regulatory update: {details}",
        }
        
        template = templates.get(alert_type, "Compliance Update: {details}")
        return template.format(**details)

    def _prepare_sustainability_content(self, metrics: Dict[str, Any]) -> str:
        """Prepare sustainability metrics content."""
        return (
            f"Sustainability Update:\n"
            f"- Carbon Footprint: {metrics.get('carbon_footprint', 'N/A')} CO2e\n"
            f"- Green Investment Ratio: {metrics.get('green_ratio', 'N/A')}%\n"
            f"- Environmental Impact Score: {metrics.get('impact_score', 'N/A')}/100\n"
            f"{metrics.get('recommendations', '')}"
        )

    def _determine_priority(self, transaction: Transaction) -> NotificationPriority:
        """Determine notification priority based on transaction details."""
        if transaction.status == TransactionStatus.FAILED:
            return NotificationPriority.HIGH
        elif transaction.status == TransactionStatus.FLAGGED:
            return NotificationPriority.HIGH
        elif transaction.amount > 1000:  # High value transaction
            return NotificationPriority.HIGH
        elif transaction.type in [TransactionType.WITHDRAWAL, TransactionType.TRANSFER]:
            return NotificationPriority.MEDIUM
        return NotificationPriority.LOW

    async def _send_notifications(self, user: User, notification: Notification) -> None:
        """Send notifications through all enabled channels."""
        tasks = []
        
        # Check user preferences and send accordingly
        if user.notification_preferences.get("email", True):
            tasks.append(self._send_email(user.email, notification))
            
        if user.notification_preferences.get("sms", False) and user.phone:
            tasks.append(self._send_sms(user.phone, notification))
            
        if user.notification_preferences.get("push", True):
            tasks.append(self._send_push(user.device_tokens, notification))
        
        # Execute all notification tasks
        for task in tasks:
            try:
                await task
            except Exception as e:
                # Log error but don't stop other notifications
                print(f"Notification error: {str(e)}")

    async def _send_email(self, email: str, notification: Notification) -> None:
        """Send email notification."""
        msg = MIMEMultipart()
        msg['From'] = self.email_sender
        msg['To'] = email
        msg['Subject'] = notification.content['title']
        
        # Create HTML content
        html = self._create_email_template(notification)
        msg.attach(MIMEText(html, 'html'))
        
        # Send email
        with smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.login(self.email_sender, self.email_password)
            server.send_message(msg)

    async def _send_sms(self, phone: str, notification: Notification) -> None:
        """Send SMS notification."""
        message = self._create_sms_content(notification)
        
        # Use SMS provider's API
        response = requests.post(
            settings.SMS_API_URL,
            headers={"Authorization": f"Bearer {self.sms_api_key}"},
            json={
                "phone": phone,
                "message": message
            }
        )
        response.raise_for_status()

    async def _send_push(self, device_tokens: List[str], notification: Notification) -> None:
        """Send push notification."""
        if not device_tokens:
            return
            
        payload = self._create_push_payload(notification)
        
        # Use push notification service API
        response = requests.post(
            settings.PUSH_API_URL,
            headers={"Authorization": f"Bearer {self.push_api_key}"},
            json={
                "tokens": device_tokens,
                "payload": payload
            }
        )
        response.raise_for_status()

    def _create_email_template(self, notification: Notification) -> str:
        """Create HTML email template."""
        # This would typically use a proper template engine
        return f"""
        <html>
            <body>
                <h2>{notification.content['title']}</h2>
                <p>Time: {notification.content['timestamp']}</p>
                <div>{str(notification.content['details'])}</div>
                <hr>
                <small>This is a secure notification from your banking system.</small>
            </body>
        </html>
        """

    def _create_sms_content(self, notification: Notification) -> str:
        """Create SMS content."""
        return f"{notification.content['title']}: {str(notification.content['details'])[:100]}"

    def _create_push_payload(self, notification: Notification) -> Dict[str, Any]:
        """Create push notification payload."""
        return {
            "title": notification.content['title'],
            "body": str(notification.content['details']),
            "priority": notification.priority.value,
            "data": {
                "type": notification.type.value,
                "id": str(notification.id)
            }
        }
