#!/usr/bin/env python3
"""Script to generate sample data for testing the mail service."""

import asyncio
import sys
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.models import EmailRequest, EmailHistory, EmailStatus
from app.mail_service import mail_service


def generate_sample_email_requests(count: int = 5) -> List[EmailRequest]:
    """Generate sample email requests for testing."""
    sample_requests = [
        EmailRequest(
            to=["john.doe@example.com"],
            cc=["manager@example.com"],
            subject="Project Update - Q4 2024",
            body="Dear John,\n\nI hope this email finds you well. I wanted to provide you with an update on our Q4 2024 project progress.\n\nBest regards,\nTeam Lead",
            is_html=False
        ),
        EmailRequest(
            to=["jane.smith@example.com", "bob.wilson@example.com"],
            subject="Meeting Reminder - Tomorrow at 2 PM",
            body="<h2>Meeting Reminder</h2><p>Hi team,</p><p>This is a reminder about our meeting tomorrow at 2 PM in the conference room.</p><p>Please prepare your quarterly reports.</p><p>Best regards,<br>Project Manager</p>",
            is_html=True
        ),
        EmailRequest(
            to=["client@company.com"],
            subject="Invoice #INV-2024-001",
            body="Dear Valued Client,\n\nPlease find attached your invoice for services rendered in December 2024.\n\nPayment is due within 30 days.\n\nThank you for your business!\n\nBest regards,\nAccounting Department",
            is_html=False
        ),
        EmailRequest(
            to=["support@example.com"],
            subject="Technical Issue Report",
            body="<h3>Technical Issue Report</h3><p><strong>Issue:</strong> Login problems</p><p><strong>Description:</strong> Users are unable to log in to the system.</p><p><strong>Priority:</strong> High</p><p><strong>Reported by:</strong> IT Support Team</p>",
            is_html=True
        ),
        EmailRequest(
            to=["all@company.com"],
            bcc=["hr@company.com"],
            subject="Company Holiday Schedule 2025",
            body="Dear All,\n\nPlease find below the company holiday schedule for 2025:\n\n- New Year's Day: January 1\n- Martin Luther King Jr. Day: January 20\n- Presidents' Day: February 17\n- Memorial Day: May 26\n- Independence Day: July 4\n- Labor Day: September 1\n- Thanksgiving: November 27-28\n- Christmas: December 25-26\n\nBest regards,\nHR Department",
            is_html=False
        )
    ]
    
    # Return the requested number of samples
    return sample_requests[:count]


def generate_sample_email_history(count: int = 10) -> List[EmailHistory]:
    """Generate sample email history for testing."""
    base_time = datetime.utcnow()
    history = []
    
    for i in range(count):
        # Create varied timestamps
        created_at = base_time - timedelta(hours=i*2)
        sent_at = created_at + timedelta(minutes=5) if i % 3 != 0 else None
        
        # Vary the status
        if i % 4 == 0:
            status = EmailStatus.FAILED
            error_message = "SMTP connection timeout"
        elif i % 3 == 0:
            status = EmailStatus.PENDING
            error_message = None
        else:
            status = EmailStatus.SENT
            error_message = None
        
        email_history = EmailHistory(
            message_id=f"msg-{i:03d}-{int(created_at.timestamp())}",
            status=status,
            to=[f"recipient{i}@example.com"],
            cc=[f"cc{i}@example.com"] if i % 2 == 0 else None,
            subject=f"Sample Email {i+1}",
            body=f"This is sample email content {i+1}.\n\nGenerated for testing purposes.",
            is_html=i % 2 == 0,
            sent_at=sent_at,
            error_message=error_message,
            created_at=created_at
        )
        
        history.append(email_history)
    
    return history


async def populate_mail_service_history(history: List[EmailHistory]):
    """Populate the mail service with sample history."""
    print("📧 Populating mail service with sample history...")
    
    for email_history in history:
        mail_service.email_history.append(email_history)
    
    print(f"✅ Added {len(history)} sample emails to history")


async def send_sample_emails(requests: List[EmailRequest], dry_run: bool = True):
    """Send sample emails (or simulate sending in dry run mode)."""
    print(f"📤 {'Simulating' if dry_run else 'Sending'} {len(requests)} sample emails...")
    
    for i, request in enumerate(requests, 1):
        print(f"   Processing email {i}/{len(requests)}: {request.subject}")
        
        if dry_run:
            # Simulate sending
            print(f"   [DRY RUN] Would send to: {', '.join(request.to)}")
        else:
            # Actually send the email
            try:
                response = await mail_service.send_email(request)
                print(f"   ✅ Sent successfully. Status: {response.status}")
            except Exception as e:
                print(f"   ❌ Failed to send: {str(e)}")


def save_sample_data_to_file(data: List[Dict[str, Any]], filename: str):
    """Save sample data to a JSON file."""
    filepath = os.path.join(os.path.dirname(__file__), '..', 'data', filename)
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    print(f"💾 Saved sample data to {filepath}")


async def main():
    """Main function to generate sample data."""
    print("🎯 Mail Service Sample Data Generator")
    print("=" * 50)
    
    # Parse command line arguments
    count = 5
    dry_run = True
    
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            print("❌ Invalid count argument. Using default count of 5.")
    
    if len(sys.argv) > 2 and sys.argv[2].lower() == '--send':
        dry_run = False
        print("⚠️  WARNING: This will actually send emails!")
        response = input("Are you sure you want to continue? (y/N): ")
        if response.lower() != 'y':
            print("❌ Cancelled by user.")
            return
    
    print(f"📊 Generating {count} sample emails...")
    print(f"🔧 Mode: {'Dry Run' if dry_run else 'Live Sending'}")
    print()
    
    # Generate sample data
    sample_requests = generate_sample_email_requests(count)
    sample_history = generate_sample_email_history(count)
    
    # Save to files
    requests_data = [req.dict() for req in sample_requests]
    history_data = [hist.dict() for hist in sample_history]
    
    save_sample_data_to_file(requests_data, 'sample_email_requests.json')
    save_sample_data_to_file(history_data, 'sample_email_history.json')
    
    # Populate mail service history
    await populate_mail_service_history(sample_history)
    
    # Send or simulate sending emails
    await send_sample_emails(sample_requests, dry_run)
    
    print()
    print("✅ Sample data generation completed!")
    print(f"📁 Data files saved in: {os.path.join(os.path.dirname(__file__), '..', 'data')}")
    
    if dry_run:
        print("💡 To actually send emails, run: python generate_sample_data.py <count> --send")


if __name__ == "__main__":
    asyncio.run(main())
