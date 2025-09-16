"""FastAPI routes for the mail service."""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

from .auth import (
    Token,
    User,
    create_access_token,
    get_current_active_user,
    get_password_hash,
    verify_password,
)
from .logging_config import RequestLogger, get_logger, set_request_context
from .mail_service import mail_service
from .models import EmailHistory, EmailRequest, EmailResponse, HealthCheck
from .validation import ValidationResult, validate_email_request

logger = get_logger(__name__)

# Create API router
router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Get access token for authentication."""
    # In a real application, validate against a database
    # For this example, we'll use a mock user
    if form_data.username != "fedfinan@gmail.com" or form_data.password != "fedfina5@135PD":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/send", response_model=EmailResponse)
async def send_email(
    email_request: EmailRequest, current_user: User = Depends(get_current_active_user)
):
    """Send an email through kube-mail."""
    with RequestLogger("api_send_email", logger, user_id=current_user.email) as req_logger:
        try:
            # Set user context for logging
            set_request_context(user_id=current_user.email)
            
            logger.info(
                "Received email send request",
                extra={
                    "user_id": current_user.email,
                    "to": email_request.to,
                    "subject": email_request.subject,
                    "has_attachments": bool(email_request.attachments),
                }
            )

            # Validate the request
            logger.debug("Validating email request", extra={"user_id": current_user.email})
            validation_result = validate_email_request(email_request.dict())
            validation_result.raise_if_invalid()
            logger.debug("Email request validation successful", extra={"user_id": current_user.email})

            # Send email
            logger.info("Sending email via mail service", extra={"user_id": current_user.email})
            response = await mail_service.send_email(email_request)

            if response.status.value == "failed":
                logger.error(
                    "Email sending failed",
                    extra={
                        "user_id": current_user.email,
                        "message_id": response.message_id,
                        "error_message": response.error_message,
                        "to": email_request.to,
                        "subject": email_request.subject,
                    }
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to send email: {response.error_message}",
                )

            logger.info(
                "Email sent successfully via API",
                extra={
                    "user_id": current_user.email,
                    "message_id": response.message_id,
                    "to": email_request.to,
                    "subject": email_request.subject,
                    "sent_at": response.sent_at.isoformat() if response.sent_at else None,
                }
            )

            return response

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Unexpected error in send_email API",
                extra={
                    "user_id": current_user.email,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "to": email_request.to,
                    "subject": email_request.subject,
                },
                exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error while sending email",
            )


@router.get("/history", response_model=List[EmailHistory])
async def get_email_history(
    limit: int = 50, current_user: User = Depends(get_current_active_user)
):
    """Get email sending history."""
    try:
        if limit < 1 or limit > 1000:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Limit must be between 1 and 1000",
            )

        history = await mail_service.get_email_history(limit)
        return history

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving email history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving email history",
        )


@router.get("/history/{message_id}", response_model=EmailHistory)
async def get_email_by_id(
    message_id: str, current_user: User = Depends(get_current_active_user)
):
    """Get specific email by message ID."""
    try:
        email = await mail_service.get_email_by_id(message_id)
        if not email:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Email with message ID {message_id} not found",
            )

        return email

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving email {message_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving email",
        )


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint."""
    try:
        smtp_connection = await mail_service.check_smtp_connection()

        return HealthCheck(
            status="healthy" if smtp_connection else "degraded",
            version="0.1.0",
            kube_mail_connection=smtp_connection,  # Keeping the field name for backward compatibility
        )

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthCheck(
            status="unhealthy", version="0.1.0", kube_mail_connection=False
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
            "health_check": "/health",
        },
    }
