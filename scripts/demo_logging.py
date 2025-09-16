#!/usr/bin/env python3
"""Demonstration script for the enhanced logging functionality."""

import os
import sys
import time

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.logging_config import (
    RequestLogger,
    get_logger,
    set_request_context,
    setup_logging,
)
from app.config import settings


def demo_basic_logging():
    """Demonstrate basic logging functionality."""
    print("=== Basic Logging Demo ===")
    
    # Setup logging
    setup_logging()
    logger = get_logger("demo")
    
    # Basic log messages
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Log with extra data
    logger.info("User action performed", extra={
        "user_id": "demo_user",
        "action": "login",
        "ip_address": "192.168.1.1"
    })


def demo_request_context():
    """Demonstrate request context logging."""
    print("\n=== Request Context Demo ===")
    
    logger = get_logger("demo_context")
    
    # Set request context
    set_request_context(
        request_id="req_demo_123",
        user_id="demo_user@example.com",
        correlation_id="corr_demo_456"
    )
    
    # Log messages with context
    logger.info("Processing user request")
    logger.info("Validating input data")
    logger.info("Request completed successfully")


def demo_performance_logging():
    """Demonstrate performance logging."""
    print("\n=== Performance Logging Demo ===")
    
    logger = get_logger("demo_performance")
    
    # Simulate a slow operation
    with RequestLogger("demo_operation", logger, operation_type="email_send") as req_logger:
        logger.info("Starting email processing")
        time.sleep(0.1)  # Simulate work
        logger.info("Email processed successfully")


def demo_structured_logging():
    """Demonstrate structured logging with different formats."""
    print("\n=== Structured Logging Demo ===")
    
    logger = get_logger("demo_structured")
    
    # Log structured data
    logger.info("Email sent", extra={
        "message_id": "msg_12345",
        "to": ["user@example.com"],
        "subject": "Test Email",
        "status": "sent",
        "duration": 0.245,
        "smtp_server": "smtp.example.com",
        "retry_count": 0
    })


def demo_error_logging():
    """Demonstrate error logging with stack traces."""
    print("\n=== Error Logging Demo ===")
    
    logger = get_logger("demo_error")
    
    try:
        # Simulate an error
        raise ValueError("This is a simulated error for demonstration")
    except Exception as e:
        logger.error(
            "Failed to process email",
            extra={
                "error_type": type(e).__name__,
                "error_message": str(e),
                "message_id": "msg_error_123"
            },
            exc_info=True
        )


def demo_configuration_options():
    """Demonstrate different configuration options."""
    print("\n=== Configuration Options Demo ===")
    
    print("Current logging configuration:")
    print(f"  Log Level: {settings.log_level}")
    print(f"  Log Format: {settings.log_format}")
    print(f"  File Logging: {settings.log_file_enabled}")
    print(f"  Performance Metrics: {settings.log_performance_metrics}")
    print(f"  SMTP Details: {settings.log_smtp_details}")
    print(f"  Email Content: {settings.log_email_content}")
    print(f"  Sensitive Data: {settings.log_include_sensitive_data}")


def main():
    """Run all demonstrations."""
    print("Enhanced Logging System Demonstration")
    print("=" * 50)
    
    demo_configuration_options()
    demo_basic_logging()
    demo_request_context()
    demo_performance_logging()
    demo_structured_logging()
    demo_error_logging()
    
    print("\n" + "=" * 50)
    print("Demo completed! Check the output above to see the logging in action.")
    print("\nTo enable debug logging, set these environment variables:")
    print("  export LOG_LEVEL=DEBUG")
    print("  export LOG_SMTP_DETAILS=true")
    print("  export LOG_EMAIL_CONTENT=true")
    print("  export LOG_INCLUDE_SENSITIVE_DATA=true")
    print("\nThen run this script again to see more detailed logging.")


if __name__ == "__main__":
    main()
