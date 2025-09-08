# Email Server API Reference

## Overview

This document provides a comprehensive API reference for integrating with the Postfix SMTP relay service. The email server provides a simple SMTP interface for sending emails through Gmail Workspace SMTP relay.

## Connection Details

### SMTP Server Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Host** | `postfix-relay.email-server-prod.svc.cluster.local` | SMTP server hostname |
| **Port** | `25` | SMTP server port |
| **Protocol** | `SMTP` | Email protocol |
| **Authentication** | `None` | IP-based authentication |
| **TLS** | `Not Required` | TLS is handled by the relay |

### Alternative Connection Methods

#### Direct Pod Access
- **Host**: `postfix-relay-headless.email-server-prod.svc.cluster.local`
- **Port**: `25`

#### Service Discovery
```bash
# Get service IP
kubectl get svc -n email-server-prod postfix-relay

# Get pod IPs
kubectl get pods -n email-server-prod -o wide
```

## SMTP Commands

### Basic SMTP Flow

```bash
# Connect to server
telnet postfix-relay.email-server-prod.svc.cluster.local 25

# SMTP conversation
220 mail.bionicaisolutions.com ESMTP
EHLO client.example.com
250-mail.bionicaisolutions.com
250-SIZE 10240000
250-VRFY
250-ETRN
250-STARTTLS
250-ENHANCEDSTATUSCODES
250-8BITMIME
250 DSN
MAIL FROM:<sender@bionicaisolutions.com>
250 2.1.0 Ok
RCPT TO:<recipient@example.com>
250 2.1.5 Ok
DATA
354 End data with <CR><LF>.<CR><LF>
Subject: Test Email
From: sender@bionicaisolutions.com
To: recipient@example.com

This is a test email.
.
250 2.0.0 Ok: queued as 1234567890
QUIT
221 2.0.0 Bye
```

### SMTP Response Codes

| Code | Description | Action |
|------|-------------|---------|
| `220` | Service ready | Server is ready to accept commands |
| `250` | Requested action completed | Command was successful |
| `354` | Start mail input | Ready to receive email data |
| `421` | Service not available | Temporary failure, try again later |
| `450` | Requested action not taken | Temporary failure, try again later |
| `451` | Requested action aborted | Temporary failure, try again later |
| `452` | Requested action not taken | Insufficient system storage |
| `500` | Syntax error | Command not recognized |
| `501` | Syntax error in parameters | Parameter syntax error |
| `502` | Command not implemented | Command not supported |
| `503` | Bad sequence of commands | Command out of sequence |
| `504` | Command parameter not implemented | Parameter not supported |
| `550` | Requested action not taken | Mailbox unavailable |
| `551` | User not local | User not local, try forwarding |
| `552` | Requested action not taken | Exceeded storage allocation |
| `553` | Requested action not taken | Mailbox name not allowed |
| `554` | Transaction failed | Transaction failed |

## Programming Language Libraries

### Python

#### smtplib (Built-in)
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Basic usage
server = smtplib.SMTP('postfix-relay.email-server-prod.svc.cluster.local', 25)
server.sendmail('from@example.com', 'to@example.com', 'message')
server.quit()
```

#### Flask-Mail
```python
from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'postfix-relay.email-server-prod.svc.cluster.local'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

@app.route('/send-email')
def send_email():
    msg = Message('Hello', sender='from@example.com', recipients=['to@example.com'])
    msg.body = "This is a test email"
    mail.send(msg)
    return "Email sent!"
```

#### Django Email
```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'postfix-relay.email-server-prod.svc.cluster.local'
EMAIL_PORT = 25
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False

# views.py
from django.core.mail import send_mail

send_mail(
    'Subject',
    'Message body',
    'from@example.com',
    ['to@example.com'],
    fail_silently=False,
)
```

### Node.js

#### Nodemailer
```javascript
const nodemailer = require('nodemailer');

const transporter = nodemailer.createTransporter({
    host: 'postfix-relay.email-server-prod.svc.cluster.local',
    port: 25,
    secure: false,
    auth: {
        // No authentication required
    }
});

const mailOptions = {
    from: 'from@example.com',
    to: 'to@example.com',
    subject: 'Test Email',
    text: 'This is a test email'
};

transporter.sendMail(mailOptions, (error, info) => {
    if (error) {
        console.log(error);
    } else {
        console.log('Email sent: ' + info.response);
    }
});
```

#### Express.js Integration
```javascript
const express = require('express');
const nodemailer = require('nodemailer');

const app = express();
const transporter = nodemailer.createTransporter({
    host: 'postfix-relay.email-server-prod.svc.cluster.local',
    port: 25,
    secure: false
});

app.post('/send-email', async (req, res) => {
    try {
        const { to, subject, text } = req.body;
        
        const info = await transporter.sendMail({
            from: 'from@example.com',
            to: to,
            subject: subject,
            text: text
        });
        
        res.json({ success: true, messageId: info.messageId });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});
```

### Java

#### JavaMail API
```java
import javax.mail.*;
import javax.mail.internet.*;
import java.util.Properties;

public class EmailSender {
    public static void sendEmail(String to, String subject, String body) {
        Properties props = new Properties();
        props.put("mail.smtp.host", "postfix-relay.email-server-prod.svc.cluster.local");
        props.put("mail.smtp.port", "25");
        props.put("mail.smtp.auth", "false");
        
        Session session = Session.getInstance(props);
        
        try {
            Message message = new MimeMessage(session);
            message.setFrom(new InternetAddress("from@example.com"));
            message.setRecipients(Message.RecipientType.TO, InternetAddress.parse(to));
            message.setSubject(subject);
            message.setText(body);
            
            Transport.send(message);
            System.out.println("Email sent successfully");
        } catch (MessagingException e) {
            throw new RuntimeException(e);
        }
    }
}
```

#### Spring Boot Integration
```java
@Configuration
@EnableConfigurationProperties
public class EmailConfig {
    
    @Bean
    public JavaMailSender javaMailSender() {
        JavaMailSenderImpl mailSender = new JavaMailSenderImpl();
        mailSender.setHost("postfix-relay.email-server-prod.svc.cluster.local");
        mailSender.setPort(25);
        mailSender.setUsername("");
        mailSender.setPassword("");
        
        Properties props = mailSender.getJavaMailProperties();
        props.put("mail.transport.protocol", "smtp");
        props.put("mail.smtp.auth", "false");
        props.put("mail.smtp.starttls.enable", "false");
        
        return mailSender;
    }
}

@Service
public class EmailService {
    
    @Autowired
    private JavaMailSender mailSender;
    
    public void sendEmail(String to, String subject, String body) {
        SimpleMailMessage message = new SimpleMailMessage();
        message.setTo(to);
        message.setSubject(subject);
        message.setText(body);
        message.setFrom("from@example.com");
        
        mailSender.send(message);
    }
}
```

### Go

#### net/smtp (Built-in)
```go
package main

import (
    "fmt"
    "net/smtp"
)

func sendEmail(to, subject, body string) error {
    from := "from@example.com"
    msg := []byte(fmt.Sprintf("To: %s\r\nSubject: %s\r\n\r\n%s", to, subject, body))
    
    err := smtp.SendMail("postfix-relay.email-server-prod.svc.cluster.local:25", nil, from, []string{to}, msg)
    if err != nil {
        return err
    }
    
    fmt.Println("Email sent successfully")
    return nil
}
```

#### Gin Framework Integration
```go
package main

import (
    "net/http"
    "net/smtp"
    "github.com/gin-gonic/gin"
)

func sendEmailHandler(c *gin.Context) {
    var email struct {
        To      string `json:"to"`
        Subject string `json:"subject"`
        Body    string `json:"body"`
    }
    
    if err := c.ShouldBindJSON(&email); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }
    
    from := "from@example.com"
    msg := []byte(fmt.Sprintf("To: %s\r\nSubject: %s\r\n\r\n%s", email.To, email.Subject, email.Body))
    
    err := smtp.SendMail("postfix-relay.email-server-prod.svc.cluster.local:25", nil, from, []string{email.To}, msg)
    if err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
        return
    }
    
    c.JSON(http.StatusOK, gin.H{"message": "Email sent successfully"})
}

func main() {
    r := gin.Default()
    r.POST("/send-email", sendEmailHandler)
    r.Run(":8080")
}
```

## Error Handling

### Common SMTP Errors

| Error | Description | Solution |
|-------|-------------|----------|
| `Connection refused` | Cannot connect to SMTP server | Check network connectivity and namespace labels |
| `550 5.7.1 Invalid credentials` | IP not whitelisted in Gmail Workspace | Add server IP to Gmail Workspace SMTP relay settings |
| `550 5.7.0 Mail relay denied` | Domain not configured in Gmail Workspace | Configure domain in Gmail Workspace |
| `421 4.7.0 Service not available` | Server temporarily unavailable | Retry after a few minutes |
| `452 4.2.2 Storage allocation exceeded` | Gmail quota exceeded | Check Gmail Workspace quota limits |

### Error Handling Examples

#### Python
```python
import smtplib
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except smtplib.SMTPException as e:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(delay * (2 ** attempt))  # Exponential backoff
            return None
        return wrapper
    return decorator

@retry_on_failure(max_retries=3, delay=1)
def send_email_with_retry(to, subject, body):
    server = smtplib.SMTP('postfix-relay.email-server-prod.svc.cluster.local', 25)
    try:
        server.sendmail('from@example.com', to, f'Subject: {subject}\n\n{body}')
    finally:
        server.quit()
```

#### Node.js
```javascript
const retry = require('async-retry');

async function sendEmailWithRetry(to, subject, body) {
    return await retry(async (bail) => {
        try {
            const info = await transporter.sendMail({
                from: 'from@example.com',
                to: to,
                subject: subject,
                text: body
            });
            return info;
        } catch (error) {
            if (error.responseCode === 550) {
                bail(error); // Don't retry on permanent failures
            }
            throw error; // Retry on temporary failures
        }
    }, {
        retries: 3,
        factor: 2,
        minTimeout: 1000,
        maxTimeout: 5000
    });
}
```

## Performance Considerations

### Connection Pooling

#### Python
```python
import smtplib
from threading import Lock

class SMTPConnectionPool:
    def __init__(self, host, port, max_connections=10):
        self.host = host
        self.port = port
        self.max_connections = max_connections
        self.connections = []
        self.lock = Lock()
    
    def get_connection(self):
        with self.lock:
            if self.connections:
                return self.connections.pop()
            else:
                return smtplib.SMTP(self.host, self.port)
    
    def return_connection(self, connection):
        with self.lock:
            if len(self.connections) < self.max_connections:
                self.connections.append(connection)
            else:
                connection.quit()
    
    def send_email(self, from_addr, to_addrs, msg):
        connection = self.get_connection()
        try:
            connection.sendmail(from_addr, to_addrs, msg)
        finally:
            self.return_connection(connection)
```

#### Node.js
```javascript
const nodemailer = require('nodemailer');

class EmailPool {
    constructor(maxConnections = 10) {
        this.maxConnections = maxConnections;
        this.connections = [];
        this.busyConnections = new Set();
    }
    
    async getConnection() {
        if (this.connections.length > 0) {
            const connection = this.connections.pop();
            this.busyConnections.add(connection);
            return connection;
        }
        
        const connection = nodemailer.createTransporter({
            host: 'postfix-relay.email-server-prod.svc.cluster.local',
            port: 25,
            secure: false,
            pool: true,
            maxConnections: this.maxConnections
        });
        
        this.busyConnections.add(connection);
        return connection;
    }
    
    async returnConnection(connection) {
        this.busyConnections.delete(connection);
        if (this.connections.length < this.maxConnections) {
            this.connections.push(connection);
        } else {
            connection.close();
        }
    }
    
    async sendEmail(to, subject, body) {
        const connection = await this.getConnection();
        try {
            const info = await connection.sendMail({
                from: 'from@example.com',
                to: to,
                subject: subject,
                text: body
            });
            return info;
        } finally {
            await this.returnConnection(connection);
        }
    }
}
```

### Rate Limiting

#### Python
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
def send_email(to, subject, body):
    # Send email logic here
    pass
```

#### Node.js
```javascript
const rateLimit = require('express-rate-limit');

const emailLimiter = rateLimit({
    windowMs: 60 * 1000, // 1 minute
    max: 30, // limit each IP to 30 requests per windowMs
    message: 'Too many emails sent, please try again later'
});

app.post('/send-email', emailLimiter, sendEmailHandler);
```

## Testing

### Unit Tests

#### Python
```python
import unittest
from unittest.mock import patch, MagicMock
import smtplib

class TestEmailSender(unittest.TestCase):
    
    @patch('smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        result = send_email("test@example.com", "Test", "Test body")
        
        self.assertTrue(result)
        mock_smtp.assert_called_once()
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_email_failure(self, mock_smtp):
        mock_smtp.side_effect = smtplib.SMTPException("Connection failed")
        
        result = send_email("test@example.com", "Test", "Test body")
        
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
```

#### Node.js
```javascript
const assert = require('assert');
const sinon = require('sinon');

describe('Email Sender', () => {
    let sandbox;
    
    beforeEach(() => {
        sandbox = sinon.createSandbox();
    });
    
    afterEach(() => {
        sandbox.restore();
    });
    
    it('should send email successfully', async () => {
        const mockTransporter = {
            sendMail: sandbox.stub().resolves({ messageId: 'test-id' })
        };
        
        sandbox.stub(nodemailer, 'createTransporter').returns(mockTransporter);
        
        const result = await sendEmail('test@example.com', 'Test', 'Test body');
        
        assert(result.success);
        assert(mockTransporter.sendMail.calledOnce);
    });
    
    it('should handle email sending failure', async () => {
        const mockTransporter = {
            sendMail: sandbox.stub().rejects(new Error('SMTP Error'))
        };
        
        sandbox.stub(nodemailer, 'createTransporter').returns(mockTransporter);
        
        const result = await sendEmail('test@example.com', 'Test', 'Test body');
        
        assert(!result.success);
        assert(result.error);
    });
});
```

### Integration Tests

#### Python
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

#### Node.js
```javascript
const request = require('supertest');
const app = require('../app');

describe('Email API Integration Tests', () => {
    it('should send email via API', async () => {
        const response = await request(app)
            .post('/send-email')
            .send({
                to: 'test@example.com',
                subject: 'Integration Test',
                body: 'This is an integration test email.'
            })
            .expect(200);
        
        assert(response.body.success);
        assert(response.body.messageId);
    });
    
    it('should handle invalid email address', async () => {
        const response = await request(app)
            .post('/send-email')
            .send({
                to: 'invalid-email',
                subject: 'Test',
                body: 'Test body'
            })
            .expect(400);
        
        assert(!response.body.success);
        assert(response.body.error);
    });
});
```

## Monitoring and Observability

### Health Checks

#### Python
```python
import smtplib
import time
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health_check():
    try:
        server = smtplib.SMTP("postfix-relay.email-server-prod.svc.cluster.local", 25)
        server.quit()
        return jsonify({
            "status": "healthy",
            "timestamp": time.time(),
            "service": "email-server"
        })
    except smtplib.SMTPException as e:
        return jsonify({
            "status": "unhealthy",
            "timestamp": time.time(),
            "service": "email-server",
            "error": str(e)
        }), 503
```

#### Node.js
```javascript
const express = require('express');
const smtp = require('smtp');
const app = express();

app.get('/health', async (req, res) => {
    try {
        const connection = smtp.createConnection({
            host: 'postfix-relay.email-server-prod.svc.cluster.local',
            port: 25
        });
        
        await connection.connect();
        connection.close();
        
        res.json({
            status: 'healthy',
            timestamp: Date.now(),
            service: 'email-server'
        });
    } catch (error) {
        res.status(503).json({
            status: 'unhealthy',
            timestamp: Date.now(),
            service: 'email-server',
            error: error.message
        });
    }
});
```

### Metrics

#### Python
```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics
email_sent_total = Counter('emails_sent_total', 'Total emails sent', ['status'])
email_send_duration = Histogram('email_send_duration_seconds', 'Time spent sending emails')
email_queue_size = Gauge('email_queue_size', 'Current email queue size')

def send_email_with_metrics(to_email, subject, body):
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

#### Node.js
```javascript
const prometheus = require('prom-client');

// Metrics
const emailSentTotal = new prometheus.Counter({
    name: 'emails_sent_total',
    help: 'Total emails sent',
    labelNames: ['status']
});

const emailSendDuration = new prometheus.Histogram({
    name: 'email_send_duration_seconds',
    help: 'Time spent sending emails'
});

async function sendEmailWithMetrics(to, subject, body) {
    const timer = emailSendDuration.startTimer();
    
    try {
        const result = await sendEmail(to, subject, body);
        emailSentTotal.labels({ status: 'success' }).inc();
        return result;
    } catch (error) {
        emailSentTotal.labels({ status: 'error' }).inc();
        throw error;
    } finally {
        timer();
    }
}
```

## Security Best Practices

1. **Input Validation**: Always validate email addresses and content
2. **Rate Limiting**: Implement rate limiting to prevent abuse
3. **Error Handling**: Don't expose sensitive information in error messages
4. **Logging**: Log all email sending attempts for audit purposes
5. **Monitoring**: Monitor for unusual patterns or abuse

## Support

For issues or questions:

1. Check the troubleshooting section in the usage guide
2. Review email server logs
3. Verify network connectivity
4. Check Gmail Workspace configuration
5. Contact the infrastructure team
