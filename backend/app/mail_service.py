"""Mail service for sending emails via kube-mail."""

import asyncio
import logging
from datetime import datetime
from typing import List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import aiosmtplib
import uuid

from .config import settings
from .models import EmailRequest, EmailResponse, EmailStatus, EmailHistory
from .validation import ValidationResult

logger = logging.getLogger(__name__)


class MailService:
    """Service for sending emails through kube-mail."""
    
    def __init__(self):
        self.host = settings.kube_mail_host
        self.port = settings.kube_mail_port
        self.from_email = settings.from_email
        self.from_name = settings.from_name
        self.email_history: List[EmailHistory] = []
    
    async def send_email(self, email_request: EmailRequest) -> EmailResponse:
        """Send an email through kube-mail."""
        message_id = str(uuid.uuid4())
        
        try:
            # Create email history entry
            email_history = EmailHistory(
                message_id=message_id,
                status=EmailStatus.PENDING,
                to=email_request.to,
                cc=email_request.cc,
                bcc=email_request.bcc,
                subject=email_request.subject,
                body=email_request.body,
                is_html=email_request.is_html
            )
            self.email_history.append(email_history)
            
            # Create email message
            message = await self._create_email_message(email_request, message_id)
            
            # Send email through kube-mail
            await self._send_via_kube_mail(message, email_request.to)
            
            # Update status
            email_history.status = EmailStatus.SENT
            email_history.sent_at = datetime.utcnow()
            
            logger.info(f"Email sent successfully. Message ID: {message_id}")
            
            return EmailResponse(
                message_id=message_id,
                status=EmailStatus.SENT,
                to=email_request.to,
                subject=email_request.subject,
                sent_at=email_history.sent_at
            )
            
        except Exception as e:
            # Update status to failed
            if email_history:
                email_history.status = EmailStatus.FAILED
                email_history.error_message = str(e)
            
            logger.error(f"Failed to send email. Message ID: {message_id}. Error: {str(e)}")
            
            return EmailResponse(
                message_id=message_id,
                status=EmailStatus.FAILED,
                to=email_request.to,
                subject=email_request.subject,
                error_message=str(e)
            )
    
    async def _create_email_message(self, email_request: EmailRequest, message_id: str) -> MIMEMultipart:
        """Create email message with proper headers and content."""
        message = MIMEMultipart('alternative')
        
        # Set headers
        message['From'] = f"{self.from_name} <{self.from_email}>"
        message['To'] = ', '.join(email_request.to)
        message['Subject'] = email_request.subject
        message['Message-ID'] = f"<{message_id}@{self.from_email.split('@')[1]}>"
        
        if email_request.cc:
            message['Cc'] = ', '.join(email_request.cc)
        
        # Add body content
        if email_request.is_html:
            html_part = MIMEText(email_request.body, 'html', 'utf-8')
            message.attach(html_part)
        else:
            text_part = MIMEText(email_request.body, 'plain', 'utf-8')
            message.attach(text_part)
        
        # Add attachments if any
        if email_request.attachments:
            await self._add_attachments(message, email_request.attachments)
        
        return message
    
    async def _add_attachments(self, message: MIMEMultipart, attachments: List[str]):
        """Add file attachments to the email message."""
        for file_path in attachments:
            try:
                with open(file_path, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {file_path.split("/")[-1]}'
                )
                message.attach(part)
            except FileNotFoundError:
                logger.warning(f"Attachment file not found: {file_path}")
            except Exception as e:
                logger.error(f"Error adding attachment {file_path}: {str(e)}")
    
    async def _send_via_kube_mail(self, message: MIMEMultipart, recipients: List[str]):
        """Send email through kube-mail SMTP server."""
        try:
            # Connect to kube-mail SMTP server
            smtp = aiosmtplib.SMTP(hostname=self.host, port=self.port)
            await smtp.connect()
            
            # Send email
            await smtp.send_message(message)
            await smtp.quit()
            
            logger.info(f"Email sent to {len(recipients)} recipients via kube-mail")
            
        except Exception as e:
            logger.error(f"Failed to send email via kube-mail: {str(e)}")
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
    
    async def check_kube_mail_connection(self) -> bool:
        """Check if kube-mail service is reachable."""
        try:
            smtp = aiosmtplib.SMTP(hostname=self.host, port=self.port)
            await smtp.connect()
            await smtp.quit()
            return True
        except Exception as e:
            logger.error(f"kube-mail connection check failed: {str(e)}")
            return False


# Global mail service instance
mail_service = MailService()
