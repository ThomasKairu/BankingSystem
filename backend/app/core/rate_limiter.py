from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
from collections import defaultdict
from typing import Dict, Tuple, DefaultDict
import asyncio
from app.core.config import settings

class RateLimiter:
    def __init__(self):
        self.requests: DefaultDict[str, list] = defaultdict(list)
        self.blocked_ips: Dict[str, float] = {}
        
        # Different rate limits for different endpoints
        self.limits = {
            "default": (100, 60),  # 100 requests per minute
            "auth": (5, 60),       # 5 login attempts per minute
            "transactions": (20, 60),  # 20 transactions per minute
            "high_value": (5, 300),    # 5 high-value transactions per 5 minutes
        }
        
        # Start cleanup task
        asyncio.create_task(self._cleanup_old_requests())

    async def _cleanup_old_requests(self):
        while True:
            current_time = time.time()
            # Clean up requests older than 1 hour
            for ip in list(self.requests.keys()):
                self.requests[ip] = [
                    req_time for req_time in self.requests[ip]
                    if current_time - req_time < 3600
                ]
                if not self.requests[ip]:
                    del self.requests[ip]
            
            # Clean up blocked IPs
            for ip in list(self.blocked_ips.keys()):
                if current_time - self.blocked_ips[ip] > 3600:  # Unblock after 1 hour
                    del self.blocked_ips[ip]
            
            await asyncio.sleep(300)  # Run cleanup every 5 minutes

    def _get_limit(self, path: str) -> Tuple[int, int]:
        """Get rate limit for a specific path"""
        if path.startswith("/api/v1/auth"):
            return self.limits["auth"]
        elif path.startswith("/api/v1/transactions"):
            return self.limits["transactions"]
        elif "high-value" in path:
            return self.limits["high_value"]
        return self.limits["default"]

    async def check_rate_limit(self, request: Request) -> None:
        if settings.ENVIRONMENT == "development":
            return
            
        client_ip = request.client.host
        current_time = time.time()
        
        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            block_time = self.blocked_ips[client_ip]
            if current_time - block_time < 3600:  # Block for 1 hour
                raise HTTPException(
                    status_code=429,
                    detail={
                        "message": "Too many requests. Please try again later.",
                        "blocked_until": block_time + 3600
                    }
                )
            else:
                del self.blocked_ips[client_ip]
        
        # Get rate limit for the path
        max_requests, window = self._get_limit(request.url.path)
        
        # Clean old requests for this IP
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < window
        ]
        
        # Check rate limit
        if len(self.requests[client_ip]) >= max_requests:
            # If consistently hitting rate limit, block the IP
            if len(self.requests[client_ip]) >= max_requests * 2:
                self.blocked_ips[client_ip] = current_time
                raise HTTPException(
                    status_code=429,
                    detail={
                        "message": "Rate limit exceeded. Your IP has been blocked.",
                        "blocked_until": current_time + 3600
                    }
                )
            
            raise HTTPException(
                status_code=429,
                detail={
                    "message": "Rate limit exceeded",
                    "retry_after": window - (current_time - self.requests[client_ip][0])
                }
            )
        
        # Add current request
        self.requests[client_ip].append(current_time)

rate_limiter = RateLimiter()
