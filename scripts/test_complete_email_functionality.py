#!/usr/bin/env python3
"""
Test script to verify complete email functionality including cc, bcc, is_html, and attachments.
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path

import aiohttp


async def test_complete_email_functionality():
    """Test all email fields and functionality."""
    
    # Create a temporary test file for attachment
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a test attachment file.\nIt contains some sample text for testing.")
        attachment_path = f.name
    
    try:
        base_url = "https://mail.bionicaisolutions.com/api/v1"
        
        # Step 1: Get JWT Token
        print("🔐 Getting JWT token...")
        token_data = {
            "username": "fedfinan@gmail.com",
            "password": "fedfina5@135PD"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{base_url}/token",
                data=token_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            ) as response:
                if response.status == 200:
                    token_response = await response.json()
                    token = token_response["access_token"]
                    print(f"✅ Token obtained: {token[:20]}...")
                else:
                    print(f"❌ Failed to get token: {response.status}")
                    return
            
            # Step 2: Test basic email (to only)
            print("\n📧 Testing basic email (to only)...")
            basic_email = {
                "to": ["salil.kadam@gmail.com"],
                "subject": "Test Basic Email - API Functionality",
                "body": "This is a basic test email with only 'to' recipients.",
                "is_html": False
            }
            
            await send_test_email(session, base_url, token, basic_email, "Basic Email")
            
            # Step 3: Test email with CC
            print("\n📧 Testing email with CC...")
            cc_email = {
                "to": ["salil.kadam@gmail.com"],
                "cc": ["salil.kadam@gmail.com"],  # Using same email for testing
                "subject": "Test Email with CC - API Functionality",
                "body": "This is a test email with CC recipients.",
                "is_html": False
            }
            
            await send_test_email(session, base_url, token, cc_email, "Email with CC")
            
            # Step 4: Test email with BCC
            print("\n📧 Testing email with BCC...")
            bcc_email = {
                "to": ["salil.kadam@gmail.com"],
                "bcc": ["salil.kadam@gmail.com"],  # Using same email for testing
                "subject": "Test Email with BCC - API Functionality",
                "body": "This is a test email with BCC recipients.",
                "is_html": False
            }
            
            await send_test_email(session, base_url, token, bcc_email, "Email with BCC")
            
            # Step 5: Test email with CC and BCC
            print("\n📧 Testing email with CC and BCC...")
            cc_bcc_email = {
                "to": ["salil.kadam@gmail.com"],
                "cc": ["salil.kadam@gmail.com"],
                "bcc": ["salil.kadam@gmail.com"],
                "subject": "Test Email with CC and BCC - API Functionality",
                "body": "This is a test email with both CC and BCC recipients.",
                "is_html": False
            }
            
            await send_test_email(session, base_url, token, cc_bcc_email, "Email with CC and BCC")
            
            # Step 6: Test HTML email
            print("\n📧 Testing HTML email...")
            html_email = {
                "to": ["salil.kadam@gmail.com"],
                "subject": "Test HTML Email - API Functionality",
                "body": """
                <html>
                <body>
                    <h1>HTML Email Test</h1>
                    <p>This is a <strong>test email</strong> with <em>HTML formatting</em>.</p>
                    <ul>
                        <li>Feature 1: HTML support</li>
                        <li>Feature 2: Rich formatting</li>
                        <li>Feature 3: Professional appearance</li>
                    </ul>
                    <p>Best regards,<br>Mail Service API</p>
                </body>
                </html>
                """,
                "is_html": True
            }
            
            await send_test_email(session, base_url, token, html_email, "HTML Email")
            
            # Step 7: Test email with attachment
            print("\n📧 Testing email with attachment...")
            attachment_email = {
                "to": ["salil.kadam@gmail.com"],
                "subject": "Test Email with Attachment - API Functionality",
                "body": "This is a test email with an attachment. Please check the attached file.",
                "is_html": False,
                "attachments": [attachment_path]
            }
            
            await send_test_email(session, base_url, token, attachment_email, "Email with Attachment")
            
            # Step 8: Test complete email (all features)
            print("\n📧 Testing complete email (all features)...")
            complete_email = {
                "to": ["salil.kadam@gmail.com"],
                "cc": ["salil.kadam@gmail.com"],
                "bcc": ["salil.kadam@gmail.com"],
                "subject": "Complete Email Test - All Features - API Functionality",
                "body": """
                <html>
                <body>
                    <h1>Complete Email Functionality Test</h1>
                    <p>This email tests <strong>all features</strong> of the mail service API:</p>
                    <ul>
                        <li>✅ To recipients</li>
                        <li>✅ CC recipients</li>
                        <li>✅ BCC recipients</li>
                        <li>✅ HTML formatting</li>
                        <li>✅ File attachments</li>
                    </ul>
                    <p>If you receive this email with the attachment, all functionality is working correctly!</p>
                    <p>Best regards,<br><em>Mail Service API</em></p>
                </body>
                </html>
                """,
                "is_html": True,
                "attachments": [attachment_path]
            }
            
            await send_test_email(session, base_url, token, complete_email, "Complete Email (All Features)")
            
            # Step 9: Test email history
            print("\n📋 Testing email history...")
            async with session.get(
                f"{base_url}/history",
                headers={"Authorization": f"Bearer {token}"}
            ) as response:
                if response.status == 200:
                    history = await response.json()
                    print(f"✅ Email history retrieved: {len(history)} emails found")
                    if history:
                        latest = history[-1]
                        print(f"   Latest email: {latest['subject']} - Status: {latest['status']}")
                else:
                    print(f"❌ Failed to get email history: {response.status}")
        
        print("\n🎉 All email functionality tests completed!")
        
    finally:
        # Clean up temporary file
        if os.path.exists(attachment_path):
            os.unlink(attachment_path)


async def send_test_email(session, base_url, token, email_data, test_name):
    """Send a test email and report results."""
    try:
        async with session.post(
            f"{base_url}/send",
            json=email_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        ) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ {test_name}: Sent successfully")
                print(f"   Message ID: {result['message_id']}")
                print(f"   Status: {result['status']}")
                print(f"   Recipients: {len(result['to'])}")
            else:
                error_text = await response.text()
                print(f"❌ {test_name}: Failed ({response.status})")
                print(f"   Error: {error_text}")
    except Exception as e:
        print(f"❌ {test_name}: Exception - {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_complete_email_functionality())