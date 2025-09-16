"""Main FastAPI application for the mail service."""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from .api import router
from .config import settings
from .logging_config import (
    RequestLogger,
    clear_request_context,
    generate_correlation_id,
    generate_request_id,
    get_logger,
    set_request_context,
    setup_logging,
)

# Set up enhanced logging
setup_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    with RequestLogger("application_startup", logger):
        logger.info("Starting mail service", extra={
            "app_name": settings.app_name,
            "app_version": settings.app_version,
            "smtp_host": settings.smtp_host,
            "smtp_port": settings.smtp_port,
            "from_email": settings.from_email,
            "use_tls": settings.use_tls,
            "log_level": settings.log_level,
            "debug": settings.debug,
        })
    
    yield
    
    # Shutdown
    with RequestLogger("application_shutdown", logger):
        logger.info("Shutting down mail service", extra={
            "app_name": settings.app_name,
            "app_version": settings.app_version,
        })


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Mail service for sending emails via SMTP",
    debug=settings.debug,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Middleware for request/response logging."""
    start_time = time.time()
    request_id = generate_request_id()
    correlation_id = generate_correlation_id()
    
    # Set request context
    set_request_context(
        request_id=request_id,
        correlation_id=correlation_id
    )
    
    # Log request
    logger.info(
        "Incoming request",
        extra={
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers) if settings.log_request_response else "[REDACTED:HEADERS]",
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }
    )
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log response
    logger.info(
        "Request completed",
        extra={
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "status_code": response.status_code,
            "duration": duration,
            "response_headers": dict(response.headers) if settings.log_request_response else "[REDACTED:RESPONSE_HEADERS]",
        }
    )
    
    # Add request ID to response headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Correlation-ID"] = correlation_id
    
    # Clear request context
    clear_request_context()
    
    return response


# Include API routes
app.include_router(router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
