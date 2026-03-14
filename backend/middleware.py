"""Custom middleware for the application."""
import time
import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from typing import Callable

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests and responses."""
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Process request and log details."""
        request_start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            
            # Calculate processing time
            request_processing_time = time.time() - request_start_time
            response.headers["X-Process-Time"] = str(request_processing_time)
            
            # Log response
            logger.info(
                f"Response: {request.method} {request.url.path} "
                f"Status: {response.status_code} Time: {request_processing_time:.4f}s"
            )
            
            return response
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"}
            )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware."""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = {}
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Check rate limits and process request."""
        client_ip = request.client.host
        current_timestamp = time.time()
        
        # Clean old entries
        self.clients = {
            client_address: request_timestamps for client_address, request_timestamps in self.clients.items()
            if any(timestamp > current_timestamp - self.period for timestamp in request_timestamps)
        }
        
        # Get client's request times
        if client_ip not in self.clients:
            self.clients[client_ip] = []
        
        # Filter times within period
        self.clients[client_ip] = [
            timestamp for timestamp in self.clients[client_ip]
            if timestamp > current_timestamp - self.period
        ]
        
        # Check rate limit
        if len(self.clients[client_ip]) >= self.calls:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Too many requests"}
            )
        
        # Add current request time
        self.clients[client_ip].append(current_timestamp)
        
        return await call_next(request)


def setup_cors(app):
    """Setup CORS middleware."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify exact origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
