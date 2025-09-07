"""Unit tests for the mail service."""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from backend.app.models import EmailRequest, EmailStatus
from backend.app.mail_service import MailService
from backend.app.validation import ValidationResult, validate_email_request, validate_email_addresses


class TestMailService:
    """Test cases for MailService class."""

    @pytest.fixture
    def mail_service(self):
        """Create a MailService instance for testing."""
        return MailService()

    @pytest.fixture
    def sample_email_request(self):
        """Create a sample email request for testing."""
        return EmailRequest(
            to=["test@example.com"],
            subject="Test Subject",
            body="Test body content",
            is_html=False
        )

    @pytest.mark.asyncio
    async def test_send_email_success(self, mail_service, sample_email_request):
        """Test successful email sending."""
        with patch.object(mail_service, '_send_via_kube_mail', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = None
            
            response = await mail_service.send_email(sample_email_request)
            
            assert response.status == EmailStatus.SENT
            assert response.message_id is not None
            assert response.to == sample_email_request.to
            assert response.subject == sample_email_request.subject
            assert response.sent_at is not None
            assert response.error_message is None
            
            mock_send.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_email_failure(self, mail_service, sample_email_request):
        """Test email sending failure."""
        with patch.object(mail_service, '_send_via_kube_mail', new_callable=AsyncMock) as mock_send:
            mock_send.side_effect = Exception("SMTP connection failed")
            
            response = await mail_service.send_email(sample_email_request)
            
            assert response.status == EmailStatus.FAILED
            assert response.message_id is not None
            assert response.error_message == "SMTP connection failed"
            assert response.sent_at is None

    @pytest.mark.asyncio
    async def test_create_email_message(self, mail_service, sample_email_request):
        """Test email message creation."""
        message_id = "test-message-id"
        
        message = await mail_service._create_email_message(sample_email_request, message_id)
        
        assert message['From'] == f"{mail_service.from_name} <{mail_service.from_email}>"
        assert message['To'] == ', '.join(sample_email_request.to)
        assert message['Subject'] == sample_email_request.subject
        assert message['Message-ID'] == f"<{message_id}@{mail_service.from_email.split('@')[1]}>"

    @pytest.mark.asyncio
    async def test_get_email_history(self, mail_service, sample_email_request):
        """Test getting email history."""
        # Send an email first
        with patch.object(mail_service, '_send_via_kube_mail', new_callable=AsyncMock):
            await mail_service.send_email(sample_email_request)
        
        history = await mail_service.get_email_history()
        
        assert len(history) == 1
        assert history[0].to == sample_email_request.to
        assert history[0].subject == sample_email_request.subject

    @pytest.mark.asyncio
    async def test_get_email_by_id(self, mail_service, sample_email_request):
        """Test getting email by message ID."""
        with patch.object(mail_service, '_send_via_kube_mail', new_callable=AsyncMock):
            response = await mail_service.send_email(sample_email_request)
        
        email = await mail_service.get_email_by_id(response.message_id)
        
        assert email is not None
        assert email.message_id == response.message_id
        assert email.to == sample_email_request.to

    @pytest.mark.asyncio
    async def test_get_email_by_id_not_found(self, mail_service):
        """Test getting email by non-existent message ID."""
        email = await mail_service.get_email_by_id("non-existent-id")
        
        assert email is None

    @pytest.mark.asyncio
    async def test_check_kube_mail_connection_success(self, mail_service):
        """Test successful kube-mail connection check."""
        with patch('aiosmtplib.SMTP') as mock_smtp:
            mock_smtp.return_value.__aenter__ = AsyncMock()
            mock_smtp.return_value.__aexit__ = AsyncMock()
            
            result = await mail_service.check_kube_mail_connection()
            
            assert result is True

    @pytest.mark.asyncio
    async def test_check_kube_mail_connection_failure(self, mail_service):
        """Test failed kube-mail connection check."""
        with patch('aiosmtplib.SMTP') as mock_smtp:
            mock_smtp.side_effect = Exception("Connection failed")
            
            result = await mail_service.check_kube_mail_connection()
            
            assert result is False


class TestValidation:
    """Test cases for validation functions."""

    def test_validate_email_request_valid(self):
        """Test validation of valid email request."""
        data = {
            "to": ["test@example.com"],
            "subject": "Test Subject",
            "body": "Test body content"
        }
        
        result = validate_email_request(data)
        
        assert result.is_valid is True
        assert result.errors == {}

    def test_validate_email_request_invalid(self):
        """Test validation of invalid email request."""
        data = {
            "to": [],  # Empty recipients
            "subject": "",  # Empty subject
            "body": ""  # Empty body
        }
        
        result = validate_email_request(data)
        
        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_validate_email_addresses_valid(self):
        """Test validation of valid email addresses."""
        emails = ["test@example.com", "user@domain.org"]
        
        result = validate_email_addresses(emails)
        
        assert result.is_valid is True
        assert result.errors == {}

    def test_validate_email_addresses_invalid(self):
        """Test validation of invalid email addresses."""
        emails = ["invalid-email", "test@example.com", "another-invalid"]
        
        result = validate_email_addresses(emails)
        
        assert result.is_valid is False
        assert "email_validation" in result.errors

    def test_validation_result_raise_if_invalid_success(self):
        """Test ValidationResult.raise_if_invalid with valid result."""
        result = ValidationResult(is_valid=True)
        
        # Should not raise any exception
        result.raise_if_invalid()

    def test_validation_result_raise_if_invalid_failure(self):
        """Test ValidationResult.raise_if_invalid with invalid result."""
        from fastapi import HTTPException
        
        result = ValidationResult(is_valid=False, errors={"email": "Invalid email format"})
        
        with pytest.raises(HTTPException) as exc_info:
            result.raise_if_invalid()
        
        assert exc_info.value.status_code == 422


class TestEmailRequestModel:
    """Test cases for EmailRequest model."""

    def test_valid_email_request(self):
        """Test creating a valid email request."""
        email_request = EmailRequest(
            to=["test@example.com"],
            subject="Test Subject",
            body="Test body content"
        )
        
        assert email_request.to == ["test@example.com"]
        assert email_request.subject == "Test Subject"
        assert email_request.body == "Test body content"
        assert email_request.is_html is False

    def test_email_request_with_cc_and_bcc(self):
        """Test creating email request with CC and BCC."""
        email_request = EmailRequest(
            to=["test@example.com"],
            cc=["cc@example.com"],
            bcc=["bcc@example.com"],
            subject="Test Subject",
            body="Test body content"
        )
        
        assert email_request.cc == ["cc@example.com"]
        assert email_request.bcc == ["bcc@example.com"]

    def test_email_request_html_content(self):
        """Test creating email request with HTML content."""
        email_request = EmailRequest(
            to=["test@example.com"],
            subject="Test Subject",
            body="<h1>Test HTML</h1>",
            is_html=True
        )
        
        assert email_request.is_html is True

    def test_email_request_validation_empty_recipients(self):
        """Test email request validation with empty recipients."""
        with pytest.raises(ValueError, match="At least one recipient must be provided"):
            EmailRequest(
                to=[],
                subject="Test Subject",
                body="Test body content"
            )

    def test_email_request_validation_empty_subject(self):
        """Test email request validation with empty subject."""
        with pytest.raises(ValueError, match="Subject cannot be empty"):
            EmailRequest(
                to=["test@example.com"],
                subject="   ",
                body="Test body content"
            )

    def test_email_request_validation_empty_body(self):
        """Test email request validation with empty body."""
        with pytest.raises(ValueError, match="Body cannot be empty"):
            EmailRequest(
                to=["test@example.com"],
                subject="Test Subject",
                body="   "
            )
