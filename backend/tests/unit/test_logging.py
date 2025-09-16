"""Tests for enhanced logging functionality."""

import json
import logging
import os
import tempfile
from unittest.mock import patch

import pytest

from app.logging_config import (
    RequestLogger,
    StructuredFormatter,
    clear_request_context,
    generate_correlation_id,
    generate_request_id,
    get_logger,
    log_email_content,
    log_sensitive_data,
    log_smtp_details,
    set_request_context,
    setup_logging,
)


class TestLoggingConfiguration:
    """Test logging configuration and setup."""

    def test_setup_logging(self):
        """Test that logging setup works correctly."""
        # This should not raise any exceptions
        setup_logging()
        
        # Verify logger is created
        logger = get_logger("test_logger")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"

    def test_structured_formatter_json(self):
        """Test JSON formatter."""
        formatter = StructuredFormatter()
        
        # Create a test log record
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Format the record
        formatted = formatter.format(record)
        
        # Should be valid JSON
        log_data = json.loads(formatted)
        assert log_data["level"] == "INFO"
        assert log_data["message"] == "Test message"
        assert log_data["logger"] == "test"

    def test_structured_formatter_text(self):
        """Test text formatter."""
        with patch('app.logging_config.settings') as mock_settings:
            mock_settings.log_format = "text"
            formatter = StructuredFormatter()
            
            # Create a test log record
            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname="test.py",
                lineno=10,
                msg="Test message",
                args=(),
                exc_info=None
            )
            
            # Format the record
            formatted = formatter.format(record)
            
            # Should be human-readable text
            assert "INFO" in formatted
            assert "Test message" in formatted
            assert "test" in formatted


class TestRequestContext:
    """Test request context management."""

    def test_set_and_clear_request_context(self):
        """Test setting and clearing request context."""
        # Set context
        set_request_context(
            request_id="test_req_123",
            user_id="test_user",
            correlation_id="test_corr_456"
        )
        
        # Clear context
        clear_request_context()
        
        # Context should be cleared (we can't easily test the context vars directly)

    def test_generate_request_id(self):
        """Test request ID generation."""
        request_id = generate_request_id()
        assert isinstance(request_id, str)
        assert len(request_id) > 0
        
        # Should generate different IDs
        request_id2 = generate_request_id()
        assert request_id != request_id2

    def test_generate_correlation_id(self):
        """Test correlation ID generation."""
        correlation_id = generate_correlation_id()
        assert isinstance(correlation_id, str)
        assert len(correlation_id) > 0
        
        # Should generate different IDs
        correlation_id2 = generate_correlation_id()
        assert correlation_id != correlation_id2


class TestDataLogging:
    """Test data logging functions."""

    def test_log_sensitive_data_enabled(self):
        """Test sensitive data logging when enabled."""
        with patch('app.logging_config.settings') as mock_settings:
            mock_settings.log_include_sensitive_data = True
            
            result = log_sensitive_data("secret_password", "password")
            assert result == "secret_password"

    def test_log_sensitive_data_disabled(self):
        """Test sensitive data logging when disabled."""
        with patch('app.logging_config.settings') as mock_settings:
            mock_settings.log_include_sensitive_data = False
            
            result = log_sensitive_data("secret_password", "password")
            assert result == "[REDACTED:password]"

    def test_log_email_content_enabled(self):
        """Test email content logging when enabled."""
        with patch('app.logging_config.settings') as mock_settings:
            mock_settings.log_email_content = True
            
            result = log_email_content("Email body content", "email")
            assert result == "Email body content"

    def test_log_email_content_disabled(self):
        """Test email content logging when disabled."""
        with patch('app.logging_config.settings') as mock_settings:
            mock_settings.log_email_content = False
            
            result = log_email_content("Email body content", "email")
            assert result == "[REDACTED:email_content]"

    def test_log_smtp_details_enabled(self):
        """Test SMTP details logging when enabled."""
        with patch('app.logging_config.settings') as mock_settings:
            mock_settings.log_smtp_details = True
            
            details = {"host": "smtp.example.com", "port": 587}
            result = log_smtp_details(details)
            assert result == details

    def test_log_smtp_details_disabled(self):
        """Test SMTP details logging when disabled."""
        with patch('app.logging_config.settings') as mock_settings:
            mock_settings.log_smtp_details = False
            
            details = {"host": "smtp.example.com", "port": 587}
            result = log_smtp_details(details)
            assert result == {"smtp_details": "[REDACTED:SMTP_DETAILS]"}


class TestRequestLogger:
    """Test RequestLogger context manager."""

    def test_request_logger_success(self):
        """Test RequestLogger with successful operation."""
        logger = get_logger("test")
        
        with RequestLogger("test_operation", logger, test_param="test_value") as req_logger:
            # Simulate some work
            pass
        
        # Should not raise any exceptions

    def test_request_logger_exception(self):
        """Test RequestLogger with exception."""
        logger = get_logger("test")
        
        with pytest.raises(ValueError):
            with RequestLogger("test_operation", logger, test_param="test_value") as req_logger:
                # Simulate an error
                raise ValueError("Test error")
        
        # Should not raise any exceptions from the logger itself


class TestLoggingIntegration:
    """Integration tests for logging functionality."""

    def test_logging_with_file_output(self):
        """Test logging with file output."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")
            
            with patch('app.logging_config.settings') as mock_settings:
                mock_settings.log_level = "INFO"
                mock_settings.log_format = "json"
                mock_settings.log_file_enabled = True
                mock_settings.log_file_path = log_file
                mock_settings.log_max_files = 5
                mock_settings.log_max_size = "10m"
                
                # Setup logging
                setup_logging()
                
                # Get logger and log a message
                logger = get_logger("test_integration")
                logger.info("Test integration message", extra={"test_field": "test_value"})
                
                # Check if log file was created and contains the message
                assert os.path.exists(log_file)
                
                with open(log_file, 'r') as f:
                    log_content = f.read()
                    assert "Test integration message" in log_content
                    assert "test_field" in log_content

    def test_logging_performance_metrics(self):
        """Test logging with performance metrics."""
        with patch('app.logging_config.settings') as mock_settings:
            mock_settings.log_performance_metrics = True
            mock_settings.log_format = "json"
            mock_settings.log_level = "INFO"
            mock_settings.log_file_enabled = False
            
            # Get logger
            logger = get_logger("test_performance")
            
            # Create a log record with duration
            record = logging.LogRecord(
                name="test_performance",
                level=logging.INFO,
                pathname="test.py",
                lineno=10,
                msg="Test performance message",
                args=(),
                exc_info=None
            )
            record.duration = 1.5
            
            # Format the record
            formatter = StructuredFormatter()
            formatted = formatter.format(record)
            
            # Should include performance metrics
            log_data = json.loads(formatted)
            assert "duration" in log_data
            assert log_data["duration"] == 1.5
