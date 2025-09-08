# Email Server Usage Guide

## Overview

This guide explains how applications can use the Postfix SMTP relay service to send emails. The email server provides a simple, reliable way to send emails through Gmail Workspace SMTP relay.

## Quick Start

### 1. Configure Your Namespace

Add the required label to your application's namespace:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: your-app-namespace
  labels:
    email-server.kubernetes.io/smtp-access: "true"
```

### 2. Connect to the Email Server

Use the following connection details:

- **Host**: `postfix-relay.email-server-prod.svc.cluster.local`
- **Port**: `25`
- **Protocol**: `SMTP`
- **Authentication**: None (IP-based relay)

## Programming Language Examples

### Python

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_email, subject, body, from_email="info@bionicaisolutions.com"):
    # SMTP server configuration
    smtp_host = "postfix-relay.email-server-prod.svc.cluster.local"
    smtp_port = 25
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    # Send email
    try:
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.send_message(msg)
        server.quit()
        print(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

# Usage
send_email(
    to_email="user@example.com",
    subject="Test Email",
    body="This is a test email from our application."
)
```

### Node.js

```javascript
const nodemailer = require('nodemailer');

// Create transporter
const transporter = nodemailer.createTransporter({
    host: 'postfix-relay.email-server-prod.svc.cluster.local',
    port: 25,
    secure: false, // true for 465, false for other ports
    auth: {
        // No authentication required for IP-based relay
    }
});

// Send email
async function sendEmail(to, subject, text, from = 'info@bionicaisolutions.com') {
    try {
        const info = await transporter.sendMail({
            from: from,
            to: to,
            subject: subject,
            text: text
        });
        
        console.log('Email sent successfully:', info.messageId);
        return true;
    } catch (error) {
        console.error('Failed to send email:', error);
        return false;
    }
}

// Usage
sendEmail(
    'user@example.com',
    'Test Email',
    'This is a test email from our application.'
);
```

### Java

```java
import javax.mail.*;
import javax.mail.internet.*;
import java.util.Properties;

public class EmailSender {
    private static final String SMTP_HOST = "postfix-relay.email-server-prod.svc.cluster.local";
    private static final int SMTP_PORT = 25;
    
    public static boolean sendEmail(String to, String subject, String body, String from) {
        Properties props = new Properties();
        props.put("mail.smtp.host", SMTP_HOST);
        props.put("mail.smtp.port", SMTP_PORT);
        props.put("mail.smtp.auth", "false");
        
        Session session = Session.getInstance(props);
        
        try {
            Message message = new MimeMessage(session);
            message.setFrom(new InternetAddress(from));
            message.setRecipients(Message.RecipientType.TO, InternetAddress.parse(to));
            message.setSubject(subject);
            message.setText(body);
            
            Transport.send(message);
            System.out.println("Email sent successfully to " + to);
            return true;
        } catch (MessagingException e) {
            System.err.println("Failed to send email: " + e.getMessage());
            return false;
        }
    }
    
    public static void main(String[] args) {
        sendEmail(
            "user@example.com",
            "Test Email",
            "This is a test email from our application.",
            "info@bionicaisolutions.com"
        );
    }
}
```

### Go

```go
package main

import (
    "fmt"
    "net/smtp"
    "strings"
)

func sendEmail(to, subject, body, from string) error {
    // SMTP server configuration
    smtpHost := "postfix-relay.email-server-prod.svc.cluster.local"
    smtpPort := "25"
    
    // Create message
    msg := []byte(fmt.Sprintf("To: %s\r\nSubject: %s\r\n\r\n%s", to, subject, body))
    
    // Send email
    err := smtp.SendMail(smtpHost+":"+smtpPort, nil, from, []string{to}, msg)
    if err != nil {
        return fmt.Errorf("failed to send email: %v", err)
    }
    
    fmt.Printf("Email sent successfully to %s\n", to)
    return nil
}

func main() {
    err := sendEmail(
        "user@example.com",
        "Test Email",
        "This is a test email from our application.",
        "info@bionicaisolutions.com",
    )
    if err != nil {
        fmt.Printf("Error: %v\n", err)
    }
}
```

## Docker Integration

### Dockerfile Example

```dockerfile
FROM python:3.9-slim

# Install required packages
RUN pip install smtplib

# Copy application code
COPY app.py /app/app.py

# Set working directory
WORKDIR /app

# Run application
CMD ["python", "app.py"]
```

### Docker Compose Example

```yaml
version: '3.8'
services:
  app:
    build: .
    environment:
      - SMTP_HOST=postfix-relay.email-server-prod.svc.cluster.local
      - SMTP_PORT=25
    networks:
      - app-network

networks:
  app-network:
    external: true
```

## Kubernetes Integration

### Deployment Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  namespace: my-app-namespace
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-app
        image: my-app:latest
        env:
        - name: SMTP_HOST
          value: "postfix-relay.email-server-prod.svc.cluster.local"
        - name: SMTP_PORT
          value: "25"
        - name: FROM_EMAIL
          value: "info@bionicaisolutions.com"
```

### Service Account Example

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app-sa
  namespace: my-app-namespace
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: my-app-role
  namespace: my-app-namespace
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: my-app-rolebinding
  namespace: my-app-namespace
subjects:
- kind: ServiceAccount
  name: my-app-sa
  namespace: my-app-namespace
roleRef:
  kind: Role
  name: my-app-role
  apiGroup: rbac.authorization.k8s.io
```

## Best Practices

### 1. Error Handling

Always implement proper error handling:

```python
import smtplib
import logging
from email.mime.text import MIMEText

def send_email_with_retry(to_email, subject, body, max_retries=3):
    for attempt in range(max_retries):
        try:
            # Send email logic here
            return send_email(to_email, subject, body)
        except smtplib.SMTPException as e:
            logging.warning(f"SMTP error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                logging.error(f"Failed to send email after {max_retries} attempts")
                return False
            time.sleep(2 ** attempt)  # Exponential backoff
    return False
```

### 2. Rate Limiting

Implement rate limiting to avoid overwhelming the email server:

```python
import time
from functools import wraps

def rate_limit(calls_per_minute=60):
    def decorator(func):
        last_called = [0.0]
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = 60.0 / calls_per_minute - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

@rate_limit(calls_per_minute=30)
def send_email(to_email, subject, body):
    # Send email logic here
    pass
```

### 3. Email Validation

Validate email addresses before sending:

```python
import re
from email_validator import validate_email, EmailNotValidError

def validate_email_address(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

def send_validated_email(to_email, subject, body):
    if not validate_email_address(to_email):
        raise ValueError(f"Invalid email address: {to_email}")
    
    return send_email(to_email, subject, body)
```

### 4. Logging

Implement comprehensive logging:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def send_email_with_logging(to_email, subject, body):
    logger.info(f"Attempting to send email to {to_email}")
    
    try:
        result = send_email(to_email, subject, body)
        if result:
            logger.info(f"Email sent successfully to {to_email}")
        else:
            logger.error(f"Failed to send email to {to_email}")
        return result
    except Exception as e:
        logger.error(f"Exception while sending email to {to_email}: {e}")
        return False
```

## Testing

### Unit Tests

```python
import unittest
from unittest.mock import patch, MagicMock
import smtplib

class TestEmailSender(unittest.TestCase):
    
    @patch('smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Test sending email
        result = send_email("test@example.com", "Test", "Test body")
        
        # Assertions
        self.assertTrue(result)
        mock_smtp.assert_called_once()
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_email_failure(self, mock_smtp):
        # Mock SMTP server to raise exception
        mock_smtp.side_effect = smtplib.SMTPException("Connection failed")
        
        # Test sending email
        result = send_email("test@example.com", "Test", "Test body")
        
        # Assertions
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
```

### Integration Tests

```python
import pytest
import smtplib

@pytest.mark.integration
def test_email_server_connection():
    """Test that we can connect to the email server."""
    try:
        server = smtplib.SMTP("postfix-relay.email-server-prod.svc.cluster.local", 25)
        server.quit()
        assert True
    except smtplib.SMTPException:
        pytest.fail("Could not connect to email server")

@pytest.mark.integration
def test_send_test_email():
    """Test sending a real email."""
    result = send_email(
        "test@example.com",
        "Integration Test",
        "This is an integration test email."
    )
    assert result is True
```

## Monitoring

### Health Checks

```python
import smtplib
import time

def check_email_server_health():
    """Check if the email server is healthy."""
    try:
        server = smtplib.SMTP("postfix-relay.email-server-prod.svc.cluster.local", 25)
        server.quit()
        return True
    except smtplib.SMTPException:
        return False

def health_check_endpoint():
    """Health check endpoint for monitoring."""
    if check_email_server_health():
        return {"status": "healthy", "timestamp": time.time()}
    else:
        return {"status": "unhealthy", "timestamp": time.time()}
```

### Metrics

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics
email_sent_total = Counter('emails_sent_total', 'Total emails sent', ['status'])
email_send_duration = Histogram('email_send_duration_seconds', 'Time spent sending emails')
email_queue_size = Gauge('email_queue_size', 'Current email queue size')

def send_email_with_metrics(to_email, subject, body):
    """Send email with metrics collection."""
    start_time = time.time()
    
    try:
        result = send_email(to_email, subject, body)
        email_sent_total.labels(status='success').inc()
        return result
    except Exception as e:
        email_sent_total.labels(status='error').inc()
        raise
    finally:
        email_send_duration.observe(time.time() - start_time)
```

## Troubleshooting

### Common Issues

1. **Connection Refused**:
   - Check if your namespace has the required label
   - Verify network policies are applied
   - Check if the email server is running

2. **Email Not Delivered**:
   - Check Postfix logs for error messages
   - Verify Gmail Workspace configuration
   - Check if the recipient email address is valid

3. **Slow Email Delivery**:
   - Check email server metrics
   - Verify network connectivity
   - Check Gmail Workspace quota limits

### Debug Commands

```bash
# Test SMTP connection
telnet postfix-relay.email-server-prod.svc.cluster.local 25

# Check email server logs
kubectl logs -n email-server-prod deployment/postfix-relay

# Check network policies
kubectl get networkpolicy -n email-server-prod

# Check service endpoints
kubectl get endpoints -n email-server-prod postfix-relay
```

## Security Considerations

1. **Network Access**: Only namespaces with the correct label can access the email server
2. **No Authentication**: The email server uses IP-based authentication
3. **TLS**: All communication with Gmail SMTP relay uses TLS
4. **Rate Limiting**: Implement rate limiting in your application
5. **Input Validation**: Always validate email addresses and content

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review email server logs
3. Verify network connectivity
4. Check Gmail Workspace configuration
