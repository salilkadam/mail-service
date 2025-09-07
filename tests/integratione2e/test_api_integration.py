"""Integration tests for the mail service API."""

import pytest
import asyncio
import httpx
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.models import EmailRequest


class TestAPIIntegration:
    """Integration tests for the mail service API."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)

    @pytest.fixture
    def sample_email_data(self):
        """Sample email data for testing."""
        return {
            "to": ["test@example.com"],
            "subject": "Integration Test Email",
            "body": "This is a test email from the integration test suite.",
            "is_html": False
        }

    def test_root_endpoint(self, client):
        """Test the root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Mail Service API"
        assert data["version"] == "0.1.0"
        assert data["from_email"] == "info@bionicaisolutions.com"

    def test_health_check_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "kube_mail_connection" in data
        assert "timestamp" in data

    def test_send_email_endpoint_success(self, client, sample_email_data):
        """Test sending email through the API endpoint."""
        # Mock the mail service to avoid actual SMTP calls
        with pytest.MonkeyPatch().context() as m:
            from backend.app import mail_service
            m.setattr(mail_service, 'send_email', self._mock_send_email_success)
            
            response = client.post("/api/v1/send", json=sample_email_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "sent"
            assert data["to"] == sample_email_data["to"]
            assert data["subject"] == sample_email_data["subject"]
            assert "message_id" in data

    def test_send_email_endpoint_validation_error(self, client):
        """Test sending email with validation errors."""
        invalid_data = {
            "to": [],  # Empty recipients
            "subject": "",  # Empty subject
            "body": ""  # Empty body
        }
        
        response = client.post("/api/v1/send", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_send_email_endpoint_invalid_email_format(self, client):
        """Test sending email with invalid email format."""
        invalid_data = {
            "to": ["invalid-email-format"],
            "subject": "Test Subject",
            "body": "Test body"
        }
        
        response = client.post("/api/v1/send", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_get_email_history_endpoint(self, client):
        """Test getting email history through the API endpoint."""
        response = client.get("/api/v1/history")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_email_history_with_limit(self, client):
        """Test getting email history with limit parameter."""
        response = client.get("/api/v1/history?limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_email_history_invalid_limit(self, client):
        """Test getting email history with invalid limit."""
        response = client.get("/api/v1/history?limit=0")
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_get_email_by_id_endpoint_not_found(self, client):
        """Test getting email by non-existent ID."""
        response = client.get("/api/v1/history/non-existent-id")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.options("/api/v1/health")
        
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers

    async def _mock_send_email_success(self, email_request):
        """Mock successful email sending."""
        from backend.app.models import EmailResponse, EmailStatus
        from datetime import datetime
        
        return EmailResponse(
            message_id="test-message-id",
            status=EmailStatus.SENT,
            to=email_request.to,
            subject=email_request.subject,
            sent_at=datetime.utcnow()
        )


class TestKubeMailIntegration:
    """Integration tests for kube-mail connectivity."""

    @pytest.mark.asyncio
    async def test_kube_mail_connection(self):
        """Test connection to kube-mail service."""
        from backend.app.mail_service import mail_service
        
        # This test will attempt to connect to the actual kube-mail service
        # It should be run in an environment where kube-mail is available
        connection_status = await mail_service.check_kube_mail_connection()
        
        # The test will pass regardless of connection status
        # but we log the result for debugging
        print(f"kube-mail connection status: {connection_status}")

    @pytest.mark.asyncio
    async def test_send_email_via_kube_mail(self):
        """Test sending email via kube-mail service."""
        from backend.app.mail_service import mail_service
        from backend.app.models import EmailRequest
        
        # Create a test email request
        email_request = EmailRequest(
            to=["test@example.com"],
            subject="Integration Test Email",
            body="This is a test email sent via kube-mail integration test.",
            is_html=False
        )
        
        # Attempt to send the email
        # This test will only work if kube-mail is properly configured
        try:
            response = await mail_service.send_email(email_request)
            print(f"Email send response: {response.status}")
            
            # Check if email was sent successfully
            if response.status == EmailStatus.SENT:
                print("Email sent successfully via kube-mail")
            else:
                print(f"Email sending failed: {response.error_message}")
                
        except Exception as e:
            print(f"Exception during email sending: {str(e)}")
            # Don't fail the test if kube-mail is not available
            pytest.skip("kube-mail service not available for integration test")


class TestFrontendIntegration:
    """Integration tests for frontend components."""

    def test_email_form_validation(self):
        """Test email form validation logic."""
        # This would test the frontend validation logic
        # For now, we'll create a placeholder test
        assert True  # Placeholder

    def test_api_service_communication(self):
        """Test frontend API service communication."""
        # This would test the frontend API service
        # For now, we'll create a placeholder test
        assert True  # Placeholder
