from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.user import User
from app.models.transaction import Transaction, TransactionStatus
from app.core.config import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    async def send_notification(
        user: User,
        notification_type: str,
        data: Dict,
        channels: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """Send notification through specified channels"""
        if channels is None:
            channels = ["email"] if user.notification_settings.get("email", True) else []
            if user.notification_settings.get("sms", False):
                channels.append("sms")
            if user.notification_settings.get("push", False):
                channels.append("push")

        results = {}
        
        for channel in channels:
            try:
                if channel == "email":
                    results["email"] = NotificationService._send_email(
                        user.email,
                        notification_type,
                        data
                    )
                elif channel == "sms":
                    results["sms"] = NotificationService._send_sms(
                        user.phone,  # Assuming phone field exists
                        notification_type,
                        data
                    )
                elif channel == "push":
                    results["push"] = NotificationService._send_push(
                        user.device_tokens,  # Assuming device_tokens field exists
                        notification_type,
                        data
                    )
            except Exception as e:
                logger.error(f"Failed to send {channel} notification: {str(e)}")
                results[channel] = False

        return results

    @staticmethod
    def _send_email(
        email: str,
        notification_type: str,
        data: Dict
    ) -> bool:
        """Send email notification"""
        try:
            subject = NotificationService._get_email_subject(notification_type)
            body = NotificationService._get_email_template(notification_type, data)

            msg = MIMEMultipart()
            msg["From"] = settings.SMTP_SENDER
            msg["To"] = email
            msg["Subject"] = subject

            msg.attach(MIMEText(body, "html"))

            # TODO: Replace with actual SMTP configuration
            # with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            #     server.starttls()
            #     server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            #     server.send_message(msg)

            logger.info(f"Email notification sent to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    @staticmethod
    def _send_sms(phone: str, notification_type: str, data: Dict) -> bool:
        """Send SMS notification"""
        try:
            message = NotificationService._get_sms_template(notification_type, data)
            
            # TODO: Implement SMS service integration
            # Example: Twilio integration
            # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            # message = client.messages.create(
            #     body=message,
            #     from_=settings.TWILIO_PHONE_NUMBER,
            #     to=phone
            # )
            
            logger.info(f"SMS notification sent to {phone}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS: {str(e)}")
            return False

    @staticmethod
    def _send_push(device_tokens: List[str], notification_type: str, data: Dict) -> bool:
        """Send push notification"""
        try:
            notification = NotificationService._get_push_template(notification_type, data)
            
            # TODO: Implement push notification service integration
            # Example: Firebase Cloud Messaging
            # message = messaging.MulticastMessage(
            #     tokens=device_tokens,
            #     notification=messaging.Notification(
            #         title=notification["title"],
            #         body=notification["body"]
            #     ),
            #     data=notification["data"]
            # )
            # response = messaging.send_multicast(message)
            
            logger.info(f"Push notification sent to {len(device_tokens)} devices")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send push notification: {str(e)}")
            return False

    @staticmethod
    def _get_email_subject(notification_type: str) -> str:
        """Get email subject based on notification type"""
        subjects = {
            "transaction_success": "Transaction Successful",
            "transaction_failed": "Transaction Failed",
            "suspicious_activity": "Suspicious Activity Detected",
            "account_locked": "Account Locked",
            "password_changed": "Password Changed Successfully",
            "login_attempt": "New Login Attempt",
            "balance_low": "Low Balance Alert",
            "kyc_update": "KYC Status Update"
        }
        return subjects.get(notification_type, "Banking Notification")

    @staticmethod
    def _get_email_template(notification_type: str, data: Dict) -> str:
        """Get email template based on notification type"""
        # In a real application, these would be proper HTML templates
        templates = {
            "transaction_success": """
                <h2>Transaction Successful</h2>
                <p>Amount: ${amount}</p>
                <p>Transaction ID: {transaction_id}</p>
                <p>Date: {date}</p>
            """,
            "suspicious_activity": """
                <h2>Suspicious Activity Detected</h2>
                <p>We detected suspicious activity on your account.</p>
                <p>Details:</p>
                <ul>
                    <li>Activity Type: {activity_type}</li>
                    <li>Location: {location}</li>
                    <li>Time: {time}</li>
                </ul>
            """
        }
        template = templates.get(notification_type, "")
        return template.format(**data)

    @staticmethod
    def _get_sms_template(notification_type: str, data: Dict) -> str:
        """Get SMS template based on notification type"""
        templates = {
            "transaction_success": "Transaction successful: ${amount}. ID: {transaction_id}",
            "suspicious_activity": "Suspicious activity detected on your account. Location: {location}"
        }
        template = templates.get(notification_type, "")
        return template.format(**data)

    @staticmethod
    def _get_push_template(notification_type: str, data: Dict) -> Dict:
        """Get push notification template based on notification type"""
        templates = {
            "transaction_success": {
                "title": "Transaction Successful",
                "body": "Amount: ${amount}",
                "data": data
            },
            "suspicious_activity": {
                "title": "Security Alert",
                "body": "Suspicious activity detected on your account",
                "data": data
            }
        }
        return templates.get(notification_type, {
            "title": "Banking Notification",
            "body": "You have a new notification",
            "data": data
        })
