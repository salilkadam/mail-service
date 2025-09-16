"""Mail service for sending emails via kube-mail."""

import asyncio
import logging
import uuid
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional

import aiosmtplib

from .config import settings
from .logging_config import (
    RequestLogger,
    get_logger,
    log_email_content,
    log_sensitive_data,
    log_smtp_details,
)
from .models import EmailHistory, EmailRequest, EmailResponse, EmailStatus
from .validation import ValidationResult

logger = get_logger(__name__)


class MailService:
    """Service for sending emails through kube-mail."""

    def __init__(self):
        self.host = settings.smtp_host
        self.port = settings.smtp_port
        self.username = settings.smtp_username
        self.password = settings.smtp_password
        self.use_tls = getattr(
            settings, "use_tls", False
        )  # Default to False for postfix relay
        self.from_email = settings.from_email
        self.from_name = settings.from_name
        self.email_history: List[EmailHistory] = []

    async def send_email(self, email_request: EmailRequest) -> EmailResponse:
        """Send an email through kube-mail."""
        message_id = str(uuid.uuid4())
        email_history = None

        with RequestLogger("send_email", logger, message_id=message_id) as req_logger:
            try:
                # Log email request details
                logger.info(
                    "Processing email send request",
                    extra={
                        "message_id": message_id,
                        "to": email_request.to,
                        "cc": email_request.cc,
                        "bcc": email_request.bcc,
                        "subject": email_request.subject,
                        "is_html": email_request.is_html,
                        "has_attachments": bool(email_request.attachments),
                        "attachment_count": len(email_request.attachments) if email_request.attachments else 0,
                        "body_length": len(email_request.body),
                        "body_preview": log_email_content(email_request.body[:100] + "..." if len(email_request.body) > 100 else email_request.body),
                    }
                )

                # Create email history entry
                email_history = EmailHistory(
                    message_id=message_id,
                    status=EmailStatus.PENDING,
                    to=email_request.to,
                    cc=email_request.cc,
                    bcc=email_request.bcc,
                    subject=email_request.subject,
                    body=email_request.body,
                    is_html=email_request.is_html,
                )
                self.email_history.append(email_history)

                # Create email message
                logger.debug("Creating email message", extra={"message_id": message_id})
                message = await self._create_email_message(email_request, message_id)

                # Collect all recipients (to, cc, bcc)
                all_recipients = email_request.to[:]
                if email_request.cc:
                    all_recipients.extend(email_request.cc)
                if email_request.bcc:
                    all_recipients.extend(email_request.bcc)

                logger.info(
                    "Prepared email for sending",
                    extra={
                        "message_id": message_id,
                        "total_recipients": len(all_recipients),
                        "to_count": len(email_request.to),
                        "cc_count": len(email_request.cc) if email_request.cc else 0,
                        "bcc_count": len(email_request.bcc) if email_request.bcc else 0,
                    }
                )

                # Send email through SMTP
                await self._send_via_smtp(message, all_recipients, message_id)

                # Update status
                email_history.status = EmailStatus.SENT
                email_history.sent_at = datetime.utcnow()

                logger.info(
                    "Email sent successfully",
                    extra={
                        "message_id": message_id,
                        "sent_at": email_history.sent_at.isoformat(),
                        "recipients": all_recipients,
                    }
                )

                return EmailResponse(
                    message_id=message_id,
                    status=EmailStatus.SENT,
                    to=email_request.to,
                    subject=email_request.subject,
                    sent_at=email_history.sent_at,
                )

            except Exception as e:
                # Update status to failed
                if email_history:
                    email_history.status = EmailStatus.FAILED
                    email_history.error_message = str(e)

                logger.error(
                    "Failed to send email",
                    extra={
                        "message_id": message_id,
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "to": email_request.to,
                        "subject": email_request.subject,
                    },
                    exc_info=True
                )

                return EmailResponse(
                    message_id=message_id,
                    status=EmailStatus.FAILED,
                    to=email_request.to,
                    subject=email_request.subject,
                    error_message=str(e),
                )

    async def _create_email_message(
        self, email_request: EmailRequest, message_id: str
    ) -> MIMEMultipart:
        """Create email message with proper headers and content."""
        message = MIMEMultipart("alternative")

        # Set headers
        message["From"] = f"{self.from_name} <{self.from_email}>"
        message["To"] = ", ".join(email_request.to)
        message["Subject"] = email_request.subject
        message["Message-ID"] = f"<{message_id}@{self.from_email.split('@')[1]}>"

        if email_request.cc:
            message["Cc"] = ", ".join(email_request.cc)

        # Add body content
        if email_request.is_html:
            html_part = MIMEText(email_request.body, "html", "utf-8")
            message.attach(html_part)
        else:
            text_part = MIMEText(email_request.body, "plain", "utf-8")
            message.attach(text_part)

        # Add attachments if any
        if email_request.attachments:
            await self._add_attachments(message, email_request.attachments)

        return message

    async def _add_attachments(self, message: MIMEMultipart, attachments: List[str]):
        """Add file attachments to the email message."""
        for file_path in attachments:
            try:
                with open(file_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())

                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f'attachment; filename= {file_path.split("/")[-1]}',
                )
                message.attach(part)
            except FileNotFoundError:
                logger.warning(f"Attachment file not found: {file_path}")
            except Exception as e:
                logger.error(f"Error adding attachment {file_path}: {str(e)}")

    async def _send_via_smtp(self, message: MIMEMultipart, recipients: List[str], message_id: str):
        """Send email through SMTP server."""
        with RequestLogger("smtp_send", logger, message_id=message_id) as req_logger:
            try:
                # Log SMTP connection details
                smtp_details = log_smtp_details({
                    "host": self.host,
                    "port": self.port,
                    "use_tls": self.use_tls,
                    "has_credentials": bool(self.username and self.password),
                    "username": log_sensitive_data(self.username, "smtp_username") if self.username else None,
                })
                
                logger.info(
                    "Connecting to SMTP server",
                    extra={
                        "message_id": message_id,
                        "recipients_count": len(recipients),
                        **smtp_details
                    }
                )

                # Connect to SMTP server
                smtp = aiosmtplib.SMTP(
                    hostname=self.host, port=self.port, use_tls=self.use_tls
                )
                await smtp.connect()
                logger.debug("SMTP connection established", extra={"message_id": message_id})

                if self.use_tls:
                    await smtp.starttls()
                    logger.debug("TLS started", extra={"message_id": message_id})

                # Login if credentials are provided (not needed for whitelisted IPs)
                if self.username and self.password:
                    await smtp.login(self.username, self.password)
                    logger.debug("SMTP authentication successful", extra={"message_id": message_id})
                else:
                    logger.debug("Skipping SMTP authentication (no credentials)", extra={"message_id": message_id})

                # Send email to all recipients (to, cc, bcc)
                logger.debug("Sending email message", extra={"message_id": message_id, "recipients": recipients})
                await smtp.send_message(message)
                await smtp.quit()
                logger.debug("SMTP connection closed", extra={"message_id": message_id})

                logger.info(
                    "Email sent successfully via SMTP",
                    extra={
                        "message_id": message_id,
                        "recipients_count": len(recipients),
                        "recipients": recipients,
                    }
                )

            except Exception as e:
                logger.error(
                    "Failed to send email via SMTP",
                    extra={
                        "message_id": message_id,
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "smtp_host": self.host,
                        "smtp_port": self.port,
                        "use_tls": self.use_tls,
                    },
                    exc_info=True
                )
                raise

    async def get_email_history(self, limit: int = 50) -> List[EmailHistory]:
        """Get email history."""
        return self.email_history[-limit:] if self.email_history else []

    async def get_email_by_id(self, message_id: str) -> Optional[EmailHistory]:
        """Get email by message ID."""
        for email in self.email_history:
            if email.message_id == message_id:
                return email
        return None

    async def check_smtp_connection(self) -> bool:
        """Check if SMTP service is reachable."""
        try:
            smtp = aiosmtplib.SMTP(
                hostname=self.host, port=self.port, use_tls=self.use_tls
            )
            await smtp.connect()

            if self.use_tls:
                await smtp.starttls()

            if self.username and self.password:
                await smtp.login(self.username, self.password)

            await smtp.quit()
            return True
        except Exception as e:
            logger.error(f"SMTP connection check failed: {str(e)}")
            return False


# Global mail service instance
mail_service = MailService()
