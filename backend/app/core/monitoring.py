from prometheus_client import Counter, Histogram, Gauge, Summary
from typing import Dict, Optional
import time
from app.core.logging import logger

class Monitoring:
    def __init__(self):
        # HTTP Metrics
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status']
        )
        self.http_request_duration_seconds = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint']
        )
        self.http_requests_in_progress = Gauge(
            'http_requests_in_progress',
            'Number of HTTP requests in progress',
            ['method']
        )

        # Business Metrics
        self.transactions_total = Counter(
            'transactions_total',
            'Total number of transactions',
            ['type', 'status']
        )
        self.transaction_amount_total = Counter(
            'transaction_amount_total',
            'Total amount of transactions',
            ['type', 'currency']
        )
        self.transaction_processing_time = Histogram(
            'transaction_processing_time',
            'Time to process transactions',
            ['type']
        )

        # Security Metrics
        self.failed_login_attempts = Counter(
            'failed_login_attempts_total',
            'Total failed login attempts',
            ['ip_address']
        )
        self.suspicious_activities = Counter(
            'suspicious_activities_total',
            'Total suspicious activities detected',
            ['type']
        )
        self.blocked_requests = Counter(
            'blocked_requests_total',
            'Total blocked requests',
            ['reason']
        )

        # System Metrics
        self.database_connections = Gauge(
            'database_connections',
            'Number of active database connections'
        )
        self.api_errors_total = Counter(
            'api_errors_total',
            'Total API errors',
            ['endpoint', 'error_type']
        )
        self.system_memory_usage = Gauge(
            'system_memory_usage',
            'System memory usage in bytes'
        )

        # Performance Metrics
        self.response_time_summary = Summary(
            'response_time_seconds',
            'Response time in seconds',
            ['endpoint']
        )
        self.database_query_duration = Histogram(
            'database_query_duration_seconds',
            'Database query duration',
            ['query_type']
        )

    def track_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float
    ):
        """Track HTTP request metrics"""
        self.http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=status_code
        ).inc()
        
        self.http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)

    def track_transaction(
        self,
        transaction_type: str,
        amount: float,
        currency: str,
        status: str,
        processing_time: float
    ):
        """Track transaction metrics"""
        self.transactions_total.labels(
            type=transaction_type,
            status=status
        ).inc()
        
        self.transaction_amount_total.labels(
            type=transaction_type,
            currency=currency
        ).inc(amount)
        
        self.transaction_processing_time.labels(
            type=transaction_type
        ).observe(processing_time)

    def track_security_event(
        self,
        event_type: str,
        ip_address: Optional[str] = None
    ):
        """Track security-related metrics"""
        if event_type == "failed_login" and ip_address:
            self.failed_login_attempts.labels(
                ip_address=ip_address
            ).inc()
        
        self.suspicious_activities.labels(
            type=event_type
        ).inc()

    def track_blocked_request(self, reason: str):
        """Track blocked requests"""
        self.blocked_requests.labels(reason=reason).inc()

    def update_system_metrics(
        self,
        db_connections: int,
        memory_usage: int
    ):
        """Update system metrics"""
        self.database_connections.set(db_connections)
        self.system_memory_usage.set(memory_usage)

    def track_api_error(
        self,
        endpoint: str,
        error_type: str
    ):
        """Track API errors"""
        self.api_errors_total.labels(
            endpoint=endpoint,
            error_type=error_type
        ).inc()

    @contextlib.contextmanager
    def track_database_query(self, query_type: str):
        """Context manager to track database query duration"""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.database_query_duration.labels(
                query_type=query_type
            ).observe(duration)

    def track_response_time(
        self,
        endpoint: str,
        duration: float
    ):
        """Track API response time"""
        self.response_time_summary.labels(
            endpoint=endpoint
        ).observe(duration)

monitoring = Monitoring()
