"""Unit tests for validation utilities."""

import os
import pytest
from fastapi import HTTPException
from app.validation import (
    ValidationResult,
    validate_email_request,
    validate_email_addresses,
    validate_attachments,
    MAX_ATTACHMENT_SIZE
)


def test_validation_result_init():
    """Test ValidationResult initialization."""
    # Test default initialization
    result = ValidationResult()
    assert result.is_valid is True
    assert result.errors == {}
    
    # Test with custom values
    result = ValidationResult(is_valid=False, errors={"test": "error"})
    assert result.is_valid is False
    assert result.errors == {"test": "error"}


def test_validation_result_raise_if_invalid():
    """Test ValidationResult error raising."""
    # Test valid case
    result = ValidationResult(is_valid=True)
    result.raise_if_invalid()  # Should not raise
    
    # Test email validation error
    result = ValidationResult(is_valid=False, errors={"email": "invalid"})
    with pytest.raises(HTTPException) as exc:
        result.raise_if_invalid()
    assert exc.value.status_code == 422
    
    # Test not found error
    result = ValidationResult(is_valid=False, errors={"error": "not found"})
    with pytest.raises(HTTPException) as exc:
        result.raise_if_invalid()
    assert exc.value.status_code == 404
    
    # Test unauthorized error
    result = ValidationResult(is_valid=False, errors={"error": "unauthorized"})
    with pytest.raises(HTTPException) as exc:
        result.raise_if_invalid()
    assert exc.value.status_code == 401
    
    # Test file too large error
    result = ValidationResult(is_valid=False, errors={"error": "file too large"})
    with pytest.raises(HTTPException) as exc:
        result.raise_if_invalid()
    assert exc.value.status_code == 413
    
    # Test unsupported media type error
    result = ValidationResult(is_valid=False, errors={"error": "unsupported media type"})
    with pytest.raises(HTTPException) as exc:
        result.raise_if_invalid()
    assert exc.value.status_code == 415


def test_validate_email_request():
    """Test email request validation."""
    # Test valid request
    valid_data = {
        "to": ["test@example.com"],
        "subject": "Test Subject",
        "body": "Test Body",
        "is_html": False
    }
    result = validate_email_request(valid_data)
    assert result.is_valid is True
    
    # Test invalid email
    invalid_data = {
        "to": ["invalid-email"],
        "subject": "Test",
        "body": "Test"
    }
    result = validate_email_request(invalid_data)
    assert result.is_valid is False
    
    # Test missing required field
    invalid_data = {
        "to": ["test@example.com"],
        "body": "Test"
        # Missing subject
    }
    result = validate_email_request(invalid_data)
    assert result.is_valid is False


def test_validate_email_addresses():
    """Test email address validation."""
    # Test valid emails
    valid_emails = ["test@example.com", "user@domain.com"]
    result = validate_email_addresses(valid_emails)
    assert result.is_valid is True
    
    # Test invalid emails
    invalid_emails = ["invalid-email", "test@", "@domain.com"]
    result = validate_email_addresses(invalid_emails)
    assert result.is_valid is False
    assert len(result.errors["email_validation"]) == len(invalid_emails)


def test_validate_attachments(tmp_path):
    """Test attachment validation."""
    # Create test files
    valid_file = tmp_path / "test.pdf"
    valid_file.write_bytes(b"Test content")
    
    large_file = tmp_path / "large.pdf"
    large_file.write_bytes(b"0" * (MAX_ATTACHMENT_SIZE + 1))
    
    invalid_type = tmp_path / "test.invalid"
    invalid_type.write_bytes(b"Test content")
    
    # Test valid attachment
    result = validate_attachments([str(valid_file)])
    assert result.is_valid is True
    
    # Test file too large
    result = validate_attachments([str(large_file)])
    assert result.is_valid is False
    assert "too large" in str(result.errors)
    
    # Test invalid file type
    result = validate_attachments([str(invalid_type)])
    assert result.is_valid is False
    assert "Unsupported file type" in str(result.errors)
    
    # Test non-existent file
    result = validate_attachments(["/nonexistent/file.pdf"])
    assert result.is_valid is False
    assert "not found" in str(result.errors)
