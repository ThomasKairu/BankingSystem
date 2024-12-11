import logging
import json
import sys
import time
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path
import structlog
from app.core.config import settings

# Configure logging paths
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Create log files
ACCESS_LOG = LOG_DIR / "access.log"
ERROR_LOG = LOG_DIR / "error.log"
SECURITY_LOG = LOG_DIR / "security.log"
TRANSACTION_LOG = LOG_DIR / "transaction.log"

class CustomLogger:
    def __init__(self):
        self.configure_logging()

    def configure_logging(self):
        """Configure logging with different handlers and formatters"""
        # Configure structlog
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        # Create formatters
        json_formatter = logging.Formatter(
            '{"timestamp":"%(asctime)s", "level":"%(levelname)s", '
            '"logger":"%(name)s", "message":%(message)s}'
        )

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(settings.LOG_LEVEL)

        # Access log handler
        access_handler = logging.FileHandler(ACCESS_LOG)
        access_handler.setFormatter(json_formatter)
        access_handler.setLevel(logging.INFO)

        # Error log handler
        error_handler = logging.FileHandler(ERROR_LOG)
        error_handler.setFormatter(json_formatter)
        error_handler.setLevel(logging.ERROR)

        # Security log handler
        security_handler = logging.FileHandler(SECURITY_LOG)
        security_handler.setFormatter(json_formatter)
        security_handler.setLevel(logging.WARNING)

        # Transaction log handler
        transaction_handler = logging.FileHandler(TRANSACTION_LOG)
        transaction_handler.setFormatter(json_formatter)
        transaction_handler.setLevel(logging.INFO)

        # Add handlers to root logger
        root_logger.addHandler(access_handler)
        root_logger.addHandler(error_handler)
        root_logger.addHandler(security_handler)
        root_logger.addHandler(transaction_handler)

        # Console handler for development
        if settings.ENVIRONMENT == "development":
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(json_formatter)
            root_logger.addHandler(console_handler)

    def get_logger(self, name: str) -> structlog.BoundLogger:
        """Get a logger instance with the given name"""
        return structlog.get_logger(name)

    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        client_ip: str,
        user_id: Optional[int] = None,
        duration_ms: Optional[float] = None,
        extra: Optional[Dict[str, Any]] = None
    ):
        """Log HTTP request details"""
        logger = self.get_logger("access")
        log_data = {
            "method": method,
            "path": path,
            "status_code": status_code,
            "client_ip": client_ip,
            "user_id": user_id,
            "duration_ms": duration_ms
        }
        if extra:
            log_data.update(extra)
        logger.info("http_request", **log_data)

    def log_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None
    ):
        """Log error details"""
        logger = self.get_logger("error")
        log_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "user_id": user_id
        }
        if context:
            log_data.update(context)
        logger.error("application_error", **log_data, exc_info=error)

    def log_security_event(
        self,
        event_type: str,
        client_ip: str,
        details: Dict[str, Any],
        user_id: Optional[int] = None
    ):
        """Log security-related events"""
        logger = self.get_logger("security")
        log_data = {
            "event_type": event_type,
            "client_ip": client_ip,
            "user_id": user_id,
            **details
        }
        logger.warning("security_event", **log_data)

    def log_transaction(
        self,
        transaction_id: str,
        transaction_type: str,
        amount: float,
        status: str,
        user_id: int,
        account_id: int,
        extra: Optional[Dict[str, Any]] = None
    ):
        """Log transaction details"""
        logger = self.get_logger("transaction")
        log_data = {
            "transaction_id": transaction_id,
            "transaction_type": transaction_type,
            "amount": amount,
            "status": status,
            "user_id": user_id,
            "account_id": account_id
        }
        if extra:
            log_data.update(extra)
        logger.info("transaction_event", **log_data)

    def log_audit(
        self,
        action: str,
        resource_type: str,
        resource_id: str,
        user_id: int,
        changes: Optional[Dict[str, Any]] = None
    ):
        """Log audit events"""
        logger = self.get_logger("audit")
        log_data = {
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "user_id": user_id,
            "changes": changes
        }
        logger.info("audit_event", **log_data)

logger = CustomLogger()
