"""Validation utilities for the mail service."""

import os
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from pydantic import ValidationError

# Constants for attachment validation
MAX_ATTACHMENT_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_MIME_TYPES = {
    ".pdf": "application/pdf",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xls": "application/vnd.ms-excel",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".txt": "text/plain",
}


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
                    detail=f"Email validation error: {self.errors}",
                )
            elif "not found" in str(self.errors).lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Resource not found: {self.errors}",
                )
            elif (
                "unauthorized" in str(self.errors).lower()
                or "forbidden" in str(self.errors).lower()
            ):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Authorization error: {self.errors}",
                )
            elif (
                "too large" in str(self.errors).lower()
                or "size" in str(self.errors).lower()
            ):
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Request too large: {self.errors}",
                )
            elif (
                "unsupported" in str(self.errors).lower()
                or "media type" in str(self.errors).lower()
            ):
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail=f"Unsupported media type: {self.errors}",
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Validation error: {self.errors}",
                )


def validate_email_request(data: Dict[str, Any]) -> ValidationResult:
    """Validate email request data."""
    try:
        from .models import EmailRequest

        # Validate basic structure
        email_request = EmailRequest(**data)

        # Validate email addresses
        all_emails = email_request.to[:]
        if email_request.cc:
            all_emails.extend(email_request.cc)
        if email_request.bcc:
            all_emails.extend(email_request.bcc)

        email_validation = validate_email_addresses(all_emails)
        if not email_validation.is_valid:
            return email_validation

        # Validate attachments if present
        if email_request.attachments:
            attachment_validation = validate_attachments(email_request.attachments)
            if not attachment_validation.is_valid:
                return attachment_validation

        return ValidationResult(is_valid=True)

    except ValidationError as e:
        return ValidationResult(is_valid=False, errors=e.errors())


def validate_email_addresses(emails: List[str]) -> ValidationResult:
    """Validate list of email addresses."""
    try:
        from email_validator import EmailNotValidError, validate_email
    except ImportError:
        # If email-validator is not available, skip validation
        return ValidationResult(is_valid=True)

    errors = []
    for i, email in enumerate(emails):
        try:
            # Use check_deliverability=False to avoid checking if domain accepts email
            validate_email(email, check_deliverability=False)
        except EmailNotValidError as e:
            errors.append(f"Invalid email at position {i}: {email} - {str(e)}")

    if errors:
        return ValidationResult(is_valid=False, errors={"email_validation": errors})

    return ValidationResult(is_valid=True)


def validate_attachments(attachments: List[str]) -> ValidationResult:
    """Validate email attachments."""
    errors = []

    for attachment_path in attachments:
        try:
            # Check if file exists
            if not os.path.exists(attachment_path):
                errors.append(f"Attachment not found: {attachment_path}")
                continue

            # Check file size
            file_size = os.path.getsize(attachment_path)
            if file_size > MAX_ATTACHMENT_SIZE:
                errors.append(
                    f"Attachment too large: {attachment_path} "
                    f"({file_size / 1024 / 1024:.1f}MB > {MAX_ATTACHMENT_SIZE / 1024 / 1024:.1f}MB)"
                )

            # Check file type
            _, ext = os.path.splitext(attachment_path.lower())
            if ext not in ALLOWED_MIME_TYPES:
                errors.append(f"Unsupported file type: {ext} for {attachment_path}")

        except Exception as e:
            errors.append(f"Error validating attachment {attachment_path}: {str(e)}")

    if errors:
        return ValidationResult(
            is_valid=False, errors={"attachment_validation": errors}
        )

    return ValidationResult(is_valid=True)
