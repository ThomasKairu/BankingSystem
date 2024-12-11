from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer
from typing import Dict, Optional, List
import time
import re
import json
from app.core.config import settings
import logging
import ipaddress

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    def __init__(self):
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": self._generate_csp(),
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
        
        self.allowed_hosts = settings.ALLOWED_HOSTS
        self.trusted_ips = settings.TRUSTED_IPS
        self.blocked_ips: Dict[str, float] = {}
        self.suspicious_patterns = [
            r"(?i)(?:union|select|insert|delete|from|drop table|update|having)",  # SQL Injection
            r"(?i)<script|javascript:|vbscript:|expression\(|<iframe",  # XSS
            r"(?i)../../|\.\.\/|%2e%2e%2f|%252e%252e%252f",  # Path Traversal
            r"(?:[^a-zA-Z0-9]|^)(exec|system|passthru)\s*\(",  # Command Injection
        ]
        
    def _generate_csp(self) -> str:
        """Generate Content Security Policy"""
        return "; ".join([
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self'",
            "frame-src 'none'",
            "object-src 'none'",
            "base-uri 'self'"
        ])

    def _is_trusted_ip(self, ip: str) -> bool:
        """Check if IP is in trusted range"""
        try:
            client_ip = ipaddress.ip_address(ip)
            return any(
                client_ip in ipaddress.ip_network(trusted_range)
                for trusted_range in self.trusted_ips
            )
        except ValueError:
            return False

    def _check_host(self, host: str) -> bool:
        """Validate Host header"""
        return host in self.allowed_hosts

    def _check_payload_size(self, content_length: int) -> bool:
        """Check if payload size is within limits"""
        max_size = 10 * 1024 * 1024  # 10MB
        return content_length <= max_size

    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Sanitize potentially dangerous headers"""
        sanitized = headers.copy()
        dangerous_headers = ['X-Forwarded-Host', 'X-Forwarded-Proto']
        for header in dangerous_headers:
            if header in sanitized:
                del sanitized[header]
        return sanitized

    async def _check_request_body(self, body: bytes) -> Optional[str]:
        """Check request body for suspicious patterns"""
        try:
            body_str = body.decode()
            for pattern in self.suspicious_patterns:
                if re.search(pattern, body_str):
                    return f"Suspicious pattern detected: {pattern}"
        except UnicodeDecodeError:
            return "Invalid request body encoding"
        return None

    async def process_request(self, request: Request) -> None:
        """Process and validate incoming request"""
        client_ip = request.client.host
        current_time = time.time()

        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            if current_time - self.blocked_ips[client_ip] < 3600:
                raise HTTPException(
                    status_code=403,
                    detail="Your IP is blocked due to suspicious activity"
                )
            del self.blocked_ips[client_ip]

        # Validate Host header
        if not self._check_host(request.headers.get("host", "")):
            self._log_security_event(client_ip, "Invalid Host header")
            raise HTTPException(status_code=400, detail="Invalid Host header")

        # Check content length
        content_length = request.headers.get("content-length", 0)
        if content_length and not self._check_payload_size(int(content_length)):
            self._log_security_event(client_ip, "Payload too large")
            raise HTTPException(status_code=413, detail="Payload too large")

        # Check request body for suspicious patterns
        body = await request.body()
        if body:
            suspicious = await self._check_request_body(body)
            if suspicious:
                self._log_security_event(client_ip, suspicious)
                self.blocked_ips[client_ip] = current_time
                raise HTTPException(
                    status_code=400,
                    detail="Request contains suspicious patterns"
                )

    def process_response(self, response: dict) -> dict:
        """Process and modify response"""
        # Add security headers
        response.headers.update(self.security_headers)
        
        # Remove sensitive headers
        sensitive_headers = ["Server", "X-Powered-By"]
        for header in sensitive_headers:
            response.headers.pop(header, None)
            
        return response

    def _log_security_event(self, ip: str, event: str):
        """Log security events"""
        logger.warning(f"Security event from {ip}: {event}")
        # In a real system, you might want to store these events in a database
        # or send them to a security monitoring system

security_middleware = SecurityMiddleware()
