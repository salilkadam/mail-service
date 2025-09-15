"""Unit tests for the mail service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.models import EmailRequest, EmailResponse, EmailStatus
from app.mail_service import MailService
from app.config import settings


@pytest.fixture
def mail_service():
    """Create a mail service instance for testing."""
    return MailService()


@pytest.fixture
def valid_email_request():
    """Create a valid email request for testing."""
    return EmailRequest(
        to=["test@example.com"],
        subject="Test Subject",
        body="Test Body",
        is_html=False
    )


@pytest.fixture
def valid_html_email_request():
    """Create a valid HTML email request for testing."""
    return EmailRequest(
        to=["test@example.com"],
        subject="Test HTML Email",
        body="<h1>Test Body</h1>",
        is_html=True
    )


@pytest.fixture
def email_request_with_cc_bcc():
    """Create an email request with CC and BCC recipients."""
    return EmailRequest(
        to=["test@example.com"],
        cc=["cc@example.com"],
        bcc=["bcc@example.com"],
        subject="Test Email with CC/BCC",
        body="Test Body",
        is_html=False
    )


@pytest.fixture
def email_request_with_attachments(tmp_path):
    """Create an email request with attachments."""
    # Create a temporary test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("Test attachment content")
    
    return EmailRequest(
        to=["test@example.com"],
        subject="Test Email with Attachment",
        body="Test Body",
        is_html=False,
        attachments=[str(test_file)]
    )


@pytest.mark.asyncio
async def test_send_email_success(mail_service, valid_email_request):
    """Test successful email sending."""
    # Mock SMTP client
    with patch("aiosmtplib.SMTP") as mock_smtp:
        # Configure mock
        mock_smtp_instance = AsyncMock()
        mock_smtp.return_value = mock_smtp_instance
        
        # Send email
        response = await mail_service.send_email(valid_email_request)
        
        # Verify SMTP calls
        mock_smtp_instance.connect.assert_called_once()
        # Note: starttls and login are not called for postfix relay
        mock_smtp_instance.send_message.assert_called_once()
        mock_smtp_instance.quit.assert_called_once()
        
        # Verify response
        assert isinstance(response, EmailResponse)
        assert response.status == EmailStatus.SENT
        assert response.to == valid_email_request.to
        assert response.subject == valid_email_request.subject
        assert response.sent_at is not None


@pytest.mark.asyncio
async def test_send_email_with_html(mail_service, valid_html_email_request):
    """Test sending HTML email."""
    with patch("aiosmtplib.SMTP") as mock_smtp:
        mock_smtp_instance = AsyncMock()
        mock_smtp.return_value = mock_smtp_instance
        
        response = await mail_service.send_email(valid_html_email_request)
        
        # Verify email was sent
        mock_smtp_instance.send_message.assert_called_once()
        assert response.status == EmailStatus.SENT


@pytest.mark.asyncio
async def test_send_email_with_cc_bcc(mail_service, email_request_with_cc_bcc):
    """Test sending email with CC and BCC recipients."""
    with patch("aiosmtplib.SMTP") as mock_smtp:
        mock_smtp_instance = AsyncMock()
        mock_smtp.return_value = mock_smtp_instance
        
        response = await mail_service.send_email(email_request_with_cc_bcc)
        
        # Verify email was sent
        mock_smtp_instance.send_message.assert_called_once()
        assert response.status == EmailStatus.SENT


@pytest.mark.asyncio
async def test_send_email_with_attachments(mail_service, email_request_with_attachments):
    """Test sending email with attachments."""
    with patch("aiosmtplib.SMTP") as mock_smtp:
        mock_smtp_instance = AsyncMock()
        mock_smtp.return_value = mock_smtp_instance
        
        response = await mail_service.send_email(email_request_with_attachments)
        
        # Verify email was sent
        mock_smtp_instance.send_message.assert_called_once()
        assert response.status == EmailStatus.SENT


@pytest.mark.asyncio
async def test_send_email_smtp_error(mail_service, valid_email_request):
    """Test handling of SMTP errors."""
    with patch("aiosmtplib.SMTP") as mock_smtp:
        # Configure mock to raise an exception
        mock_smtp_instance = AsyncMock()
        mock_smtp_instance.send_message.side_effect = Exception("SMTP error")
        mock_smtp.return_value = mock_smtp_instance
        
        response = await mail_service.send_email(valid_email_request)
        
        # Verify error handling
        assert response.status == EmailStatus.FAILED
        assert "SMTP error" in response.error_message


@pytest.mark.asyncio
async def test_check_smtp_connection_success(mail_service):
    """Test successful SMTP connection check."""
    with patch("aiosmtplib.SMTP") as mock_smtp:
        mock_smtp_instance = AsyncMock()
        mock_smtp.return_value = mock_smtp_instance
        
        result = await mail_service.check_smtp_connection()
        
        assert result is True
        mock_smtp_instance.connect.assert_called_once()
        mock_smtp_instance.quit.assert_called_once()


@pytest.mark.asyncio
async def test_check_smtp_connection_failure(mail_service):
    """Test failed SMTP connection check."""
    with patch("aiosmtplib.SMTP") as mock_smtp:
        mock_smtp_instance = AsyncMock()
        mock_smtp_instance.connect.side_effect = Exception("Connection failed")
        mock_smtp.return_value = mock_smtp_instance
        
        result = await mail_service.check_smtp_connection()
        
        assert result is False


@pytest.mark.asyncio
async def test_get_email_history(mail_service, valid_email_request):
    """Test retrieving email history."""
    # Send a test email to create history
    await mail_service.send_email(valid_email_request)
    
    # Get history
    history = await mail_service.get_email_history()
    
    assert len(history) == 1
    assert history[0].to == valid_email_request.to
    assert history[0].subject == valid_email_request.subject


@pytest.mark.asyncio
async def test_get_email_by_id(mail_service, valid_email_request):
    """Test retrieving specific email by ID."""
    # Send a test email
    response = await mail_service.send_email(valid_email_request)
    
    # Get email by ID
    email = await mail_service.get_email_by_id(response.message_id)
    
    assert email is not None
    assert email.message_id == response.message_id
    assert email.to == valid_email_request.to
    assert email.subject == valid_email_request.subject
