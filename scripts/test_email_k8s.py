#!/usr/bin/env python3
"""Test script to send email from Kubernetes pod."""

import asyncio
import sys
import os
sys.path.append('/app')

from app.mail_service import mail_service
from app.models import EmailRequest


async def test_email_sending():
    """Test sending an email."""
    print("Testing email sending from Kubernetes pod...")
    
    # Create test email request
    email_request = EmailRequest(
        to=["Salil.Kadam@gmail.com"],
        subject="Test Email from Kubernetes Pod via Postfix Relay",
        body="""Hello Salil,

This is a test email sent from the mail service running in Kubernetes.

The email service is configured to use the postfix relay which forwards to Gmail SMTP with the whitelisted IP address.

Best regards,
Mail Service Team""",
        is_html=False
    )
    
    try:
        # Send email
        print("Sending email...")
        response = await mail_service.send_email(email_request)
        
        if response.status.value == "sent":
            print(f"✅ Email sent successfully!")
            print(f"Message ID: {response.message_id}")
            print(f"Recipients: {', '.join(response.to)}")
            print(f"Subject: {response.subject}")
            print(f"Sent at: {response.sent_at}")
        else:
            print(f"❌ Email sending failed!")
            print(f"Status: {response.status}")
            print(f"Error: {response.error_message}")
            
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")


async def test_smtp_connection():
    """Test SMTP connection."""
    print("Testing SMTP connection...")
    
    try:
        is_connected = await mail_service.check_smtp_connection()
        if is_connected:
            print("✅ SMTP connection successful!")
        else:
            print("❌ SMTP connection failed!")
    except Exception as e:
        print(f"❌ Error testing SMTP connection: {str(e)}")


async def main():
    """Main test function."""
    print("=" * 50)
    print("Mail Service Test - Kubernetes Pod")
    print("=" * 50)
    
    # Test SMTP connection first
    await test_smtp_connection()
    print()
    
    # Test email sending
    await test_email_sending()
    print()
    
    print("Test completed!")


if __name__ == "__main__":
    asyncio.run(main())
