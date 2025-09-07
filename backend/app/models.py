"""Pydantic models for the mail service."""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum


class EmailStatus(str, Enum):
    """Email status enumeration."""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"


class EmailRequest(BaseModel):
    """Request model for sending an email."""
    
    to: List[EmailStr] = Field(..., description="List of recipient email addresses")
    cc: Optional[List[EmailStr]] = Field(None, description="List of CC email addresses")
    bcc: Optional[List[EmailStr]] = Field(None, description="List of BCC email addresses")
    subject: str = Field(..., min_length=1, max_length=200, description="Email subject")
    body: str = Field(..., min_length=1, description="Email body content")
    is_html: bool = Field(False, description="Whether the body is HTML content")
    attachments: Optional[List[str]] = Field(None, description="List of attachment file paths")
    
    @validator('to')
    def validate_recipients(cls, v):
        """Validate that at least one recipient is provided."""
        if not v or len(v) == 0:
            raise ValueError('At least one recipient must be provided')
        return v
    
    @validator('subject')
    def validate_subject(cls, v):
        """Validate subject is not empty after stripping."""
        if not v.strip():
            raise ValueError('Subject cannot be empty')
        return v.strip()
    
    @validator('body')
    def validate_body(cls, v):
        """Validate body is not empty after stripping."""
        if not v.strip():
            raise ValueError('Body cannot be empty')
        return v.strip()


class EmailResponse(BaseModel):
    """Response model for email operations."""
    
    message_id: str = Field(..., description="Unique message identifier")
    status: EmailStatus = Field(..., description="Current email status")
    to: List[str] = Field(..., description="List of recipient email addresses")
    subject: str = Field(..., description="Email subject")
    sent_at: Optional[datetime] = Field(None, description="Timestamp when email was sent")
    error_message: Optional[str] = Field(None, description="Error message if sending failed")


class EmailHistory(BaseModel):
    """Model for email history entry."""
    
    message_id: str
    status: EmailStatus
    to: List[str]
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    subject: str
    body: str
    is_html: bool
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class HealthCheck(BaseModel):
    """Health check response model."""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    kube_mail_connection: bool = Field(..., description="kube-mail connection status")
