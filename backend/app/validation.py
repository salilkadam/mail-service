"""Validation utilities for the mail service."""

from typing import Any, Dict, List, Optional
from pydantic import ValidationError
from fastapi import HTTPException, status


class ValidationResult:
    """Validation result container with error handling."""
    
    def __init__(self, is_valid: bool = True, errors: Optional[Dict[str, Any]] = None):
        self.is_valid = is_valid
        self.errors = errors or {}
    
    def raise_if_invalid(self):
        """Raise HTTPException if validation failed."""
        if not self.is_valid:
            # Map validation errors to appropriate HTTP status codes
            if "email" in str(self.errors).lower():
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Email validation error: {self.errors}"
                )
            elif "not found" in str(self.errors).lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Resource not found: {self.errors}"
                )
            elif "unauthorized" in str(self.errors).lower() or "forbidden" in str(self.errors).lower():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Authorization error: {self.errors}"
                )
            elif "too large" in str(self.errors).lower() or "size" in str(self.errors).lower():
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Request too large: {self.errors}"
                )
            elif "unsupported" in str(self.errors).lower() or "media type" in str(self.errors).lower():
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail=f"Unsupported media type: {self.errors}"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Validation error: {self.errors}"
                )


def validate_email_request(data: Dict[str, Any]) -> ValidationResult:
    """Validate email request data."""
    try:
        from .models import EmailRequest
        EmailRequest(**data)
        return ValidationResult(is_valid=True)
    except ValidationError as e:
        return ValidationResult(is_valid=False, errors=e.errors())


def validate_email_addresses(emails: List[str]) -> ValidationResult:
    """Validate list of email addresses."""
    from email_validator import validate_email, EmailNotValidError
    
    errors = []
    for i, email in enumerate(emails):
        try:
            validate_email(email)
        except EmailNotValidError as e:
            errors.append(f"Invalid email at position {i}: {email} - {str(e)}")
    
    if errors:
        return ValidationResult(is_valid=False, errors={"email_validation": errors})
    
    return ValidationResult(is_valid=True)
