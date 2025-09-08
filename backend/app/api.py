"""FastAPI routes for the mail service."""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware

from .models import EmailRequest, EmailResponse, EmailHistory, HealthCheck
from .mail_service import mail_service
from .validation import validate_email_request, ValidationResult

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter()


@router.post("/send", response_model=EmailResponse)
async def send_email(email_request: EmailRequest):
    """Send an email through Postfix SMTP relay."""
    try:
        # Validate the request
        validation_result = validate_email_request(email_request.dict())
        validation_result.raise_if_invalid()
        
        # Send email
        response = await mail_service.send_email(email_request)
        
        if response.status.value == "failed":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send email: {response.error_message}"
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error sending email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while sending email"
        )


@router.get("/history", response_model=List[EmailHistory])
async def get_email_history(limit: int = 50):
    """Get email sending history."""
    try:
        if limit < 1 or limit > 1000:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Limit must be between 1 and 1000"
            )
        
        history = await mail_service.get_email_history(limit)
        return history
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving email history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving email history"
        )


@router.get("/history/{message_id}", response_model=EmailHistory)
async def get_email_by_id(message_id: str):
    """Get specific email by message ID."""
    try:
        email = await mail_service.get_email_by_id(message_id)
        if not email:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Email with message ID {message_id} not found"
            )
        
        return email
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving email {message_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving email"
        )


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint."""
    try:
        postfix_connection = await mail_service.check_postfix_connection()
        
        return HealthCheck(
            status="healthy" if postfix_connection else "degraded",
            version="0.1.0",
            kube_mail_connection=postfix_connection
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthCheck(
            status="unhealthy",
            version="0.1.0",
            kube_mail_connection=False
        )


@router.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Mail Service API",
        "version": "0.1.0",
        "from_email": "info@bionicaisolutions.com",
        "endpoints": {
            "send_email": "/send",
            "email_history": "/history",
            "health_check": "/health"
        }
    }
