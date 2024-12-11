from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
from typing import Optional
from app.core.rate_limiter import rate_limiter
from app.core.security_middleware import security_middleware
from app.core.logging import logger
from app.core.monitoring import monitoring
import json
import traceback

class APIMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        request_id = self._generate_request_id()
        path = request.url.path
        method = request.method
        client_ip = request.client.host

        # Add request ID to request state
        request.state.request_id = request_id
        
        try:
            # Rate limiting check
            await rate_limiter.check_rate_limit(request)
            
            # Security checks
            await security_middleware.process_request(request)
            
            # Track request start
            with monitoring.http_requests_in_progress.labels(method=method).track_inprogress():
                # Process request
                response = await call_next(request)
                
                # Add security headers
                response = security_middleware.process_response(response)
                
                # Calculate request duration
                duration = time.time() - start_time
                
                # Log successful request
                self._log_request(
                    request_id,
                    method,
                    path,
                    response.status_code,
                    client_ip,
                    duration,
                    request.state.user_id if hasattr(request.state, "user_id") else None
                )
                
                # Track metrics
                monitoring.track_request(
                    method,
                    path,
                    response.status_code,
                    duration
                )
                
                return response
                
        except Exception as e:
            # Handle exceptions
            duration = time.time() - start_time
            
            # Log error
            self._log_error(
                request_id,
                e,
                method,
                path,
                client_ip,
                request.state.user_id if hasattr(request.state, "user_id") else None
            )
            
            # Track error metrics
            monitoring.track_api_error(path, type(e).__name__)
            
            # Return error response
            error_response = self._create_error_response(e)
            return error_response

    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        import uuid
        return str(uuid.uuid4())

    def _log_request(
        self,
        request_id: str,
        method: str,
        path: str,
        status_code: int,
        client_ip: str,
        duration: float,
        user_id: Optional[int]
    ):
        """Log request details"""
        logger.log_request(
            method=method,
            path=path,
            status_code=status_code,
            client_ip=client_ip,
            user_id=user_id,
            duration_ms=duration * 1000,
            extra={
                "request_id": request_id
            }
        )

    def _log_error(
        self,
        request_id: str,
        error: Exception,
        method: str,
        path: str,
        client_ip: str,
        user_id: Optional[int]
    ):
        """Log error details"""
        logger.log_error(
            error=error,
            context={
                "request_id": request_id,
                "method": method,
                "path": path,
                "client_ip": client_ip
            },
            user_id=user_id
        )

    def _create_error_response(self, error: Exception) -> Response:
        """Create appropriate error response"""
        from fastapi import HTTPException
        from fastapi.responses import JSONResponse
        
        if isinstance(error, HTTPException):
            return JSONResponse(
                status_code=error.status_code,
                content={"detail": error.detail}
            )
            
        # For unexpected errors, return 500
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error"
            }
        )
