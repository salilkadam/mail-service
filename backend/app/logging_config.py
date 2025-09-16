"""Enhanced logging configuration for the mail service."""

import json
import logging
import logging.handlers
import os
import time
import uuid
from contextvars import ContextVar
from typing import Any, Dict, Optional

from .config import settings

# Context variables for request tracking
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured data."""
        if settings.log_format == "json":
            return self._format_json(record)
        else:
            return self._format_text(record)
    
    def _format_json(self, record: logging.LogRecord) -> str:
        """Format as JSON."""
        log_data = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add request tracking information
        if settings.log_include_request_id and request_id_var.get():
            log_data["request_id"] = request_id_var.get()
        
        if settings.log_correlation_id and correlation_id_var.get():
            log_data["correlation_id"] = correlation_id_var.get()
        
        if settings.log_include_user_info and user_id_var.get():
            log_data["user_id"] = user_id_var.get()
        
        # Add exception information
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from the record
        for key, value in record.__dict__.items():
            if key not in {
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename',
                'module', 'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                'thread', 'threadName', 'processName', 'process', 'getMessage',
                'exc_info', 'exc_text', 'stack_info'
            }:
                log_data[key] = value
        
        return json.dumps(log_data, default=str)
    
    def _format_text(self, record: logging.LogRecord) -> str:
        """Format as human-readable text."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(record.created))
        level = record.levelname.ljust(8)
        logger_name = record.name
        
        # Build request info
        request_info = ""
        if settings.log_include_request_id and request_id_var.get():
            request_info += f" [req:{request_id_var.get()[:8]}]"
        if settings.log_correlation_id and correlation_id_var.get():
            request_info += f" [corr:{correlation_id_var.get()[:8]}]"
        if settings.log_include_user_info and user_id_var.get():
            request_info += f" [user:{user_id_var.get()}]"
        
        message = record.getMessage()
        
        return f"{timestamp} {level} {logger_name}{request_info}: {message}"


class PerformanceFilter(logging.Filter):
    """Filter to add performance metrics to log records."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add performance metrics if enabled."""
        if settings.log_performance_metrics and hasattr(record, 'duration'):
            record.performance_metrics = {
                "duration_seconds": record.duration,
                "duration_ms": record.duration * 1000
            }
        return True


def setup_logging():
    """Set up enhanced logging configuration."""
    # Create logs directory if it doesn't exist
    if settings.log_file_enabled:
        log_dir = os.path.dirname(settings.log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = StructuredFormatter()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.addFilter(PerformanceFilter())
    root_logger.addHandler(console_handler)
    
    # File handler (if enabled)
    if settings.log_file_enabled:
        # Parse max size (e.g., "10m" -> 10 * 1024 * 1024)
        max_bytes = _parse_size(settings.log_max_size)
        
        file_handler = logging.handlers.RotatingFileHandler(
            settings.log_file_path,
            maxBytes=max_bytes,
            backupCount=settings.log_max_files
        )
        file_handler.setFormatter(formatter)
        file_handler.addFilter(PerformanceFilter())
        root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    # Log startup information
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized", extra={
        "log_level": settings.log_level,
        "log_format": settings.log_format,
        "log_file_enabled": settings.log_file_enabled,
        "log_file_path": settings.log_file_path if settings.log_file_enabled else None,
        "log_performance_metrics": settings.log_performance_metrics,
        "log_smtp_details": settings.log_smtp_details,
        "log_email_content": settings.log_email_content,
    })


def _parse_size(size_str: str) -> int:
    """Parse size string like '10m' to bytes."""
    size_str = size_str.lower().strip()
    if size_str.endswith('k'):
        return int(size_str[:-1]) * 1024
    elif size_str.endswith('m'):
        return int(size_str[:-1]) * 1024 * 1024
    elif size_str.endswith('g'):
        return int(size_str[:-1]) * 1024 * 1024 * 1024
    else:
        return int(size_str)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with enhanced capabilities."""
    return logging.getLogger(name)


def set_request_context(request_id: str = None, user_id: str = None, correlation_id: str = None):
    """Set request context for logging."""
    if request_id:
        request_id_var.set(request_id)
    if user_id:
        user_id_var.set(user_id)
    if correlation_id:
        correlation_id_var.set(correlation_id)


def clear_request_context():
    """Clear request context."""
    request_id_var.set(None)
    user_id_var.set(None)
    correlation_id_var.set(None)


def generate_request_id() -> str:
    """Generate a unique request ID."""
    return str(uuid.uuid4())


def generate_correlation_id() -> str:
    """Generate a unique correlation ID."""
    return str(uuid.uuid4())


def log_sensitive_data(data: Any, field_name: str = "data") -> Any:
    """Log sensitive data only if enabled in settings."""
    if settings.log_include_sensitive_data:
        return data
    else:
        return f"[REDACTED:{field_name}]"


def log_email_content(content: str, content_type: str = "email") -> str:
    """Log email content only if enabled in settings."""
    if settings.log_email_content:
        return content
    else:
        return f"[REDACTED:{content_type}_content]"


def log_smtp_details(details: Dict[str, Any]) -> Dict[str, Any]:
    """Log SMTP details only if enabled in settings."""
    if settings.log_smtp_details:
        return details
    else:
        return {"smtp_details": "[REDACTED:SMTP_DETAILS]"}


class RequestLogger:
    """Context manager for request logging with performance tracking."""
    
    def __init__(self, operation: str, logger: logging.Logger, **extra_data):
        self.operation = operation
        self.logger = logger
        self.extra_data = extra_data
        self.start_time = None
        self.request_id = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.request_id = generate_request_id()
        set_request_context(request_id=self.request_id)
        
        self.logger.info(
            f"Starting {self.operation}",
            extra={
                "operation": self.operation,
                "request_id": self.request_id,
                **self.extra_data
            }
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if exc_type is None:
            # Success
            self.logger.info(
                f"Completed {self.operation}",
                extra={
                    "operation": self.operation,
                    "request_id": self.request_id,
                    "duration": duration,
                    "status": "success",
                    **self.extra_data
                }
            )
        else:
            # Error
            self.logger.error(
                f"Failed {self.operation}",
                extra={
                    "operation": self.operation,
                    "request_id": self.request_id,
                    "duration": duration,
                    "status": "error",
                    "error_type": exc_type.__name__,
                    "error_message": str(exc_val),
                    **self.extra_data
                },
                exc_info=exc_type
            )
        
        # Log slow requests
        if duration > settings.log_slow_requests_threshold:
            self.logger.warning(
                f"Slow request detected: {self.operation}",
                extra={
                    "operation": self.operation,
                    "request_id": self.request_id,
                    "duration": duration,
                    "threshold": settings.log_slow_requests_threshold,
                    "status": "slow_request",
                    **self.extra_data
                }
            )
        
        clear_request_context()
