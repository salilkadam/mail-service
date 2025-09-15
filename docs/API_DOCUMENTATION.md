# Mail Service API Documentation

## Overview
The Mail Service API provides a secure, JWT-authenticated interface for sending emails with full support for CC, BCC, HTML content, and file attachments.

**Base URL:** `https://mail.bionicaisolutions.com/api/v1`

## Authentication

### Get JWT Token
**Endpoint:** `POST /token`

**Request:**
```bash
curl -X POST https://mail.bionicaisolutions.com/api/v1/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=fedfinan@gmail.com&password=fedfina5@135PD"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Email Sending

### Send Email
**Endpoint:** `POST /send`

**Headers:**
```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

### Request Fields

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `to` | `List[EmailStr]` | ✅ **Yes** | List of recipient email addresses | `["user@example.com", "admin@company.com"]` |
| `subject` | `string` | ✅ **Yes** | Email subject (1-200 chars) | `"Meeting Reminder"` |
| `body` | `string` | ✅ **Yes** | Email body content | `"Don't forget our meeting at 3 PM"` |
| `cc` | `List[EmailStr]` | ❌ Optional | List of CC email addresses | `["manager@company.com"]` |
| `bcc` | `List[EmailStr]` | ❌ Optional | List of BCC email addresses | `["archive@company.com"]` |
| `is_html` | `boolean` | ❌ Optional | Whether body is HTML content | `false` (default) |
| `attachments` | `List[string]` | ❌ Optional | List of attachment file paths | `["/tmp/document.pdf"]` |

### Example Requests

#### Basic Email
```json
{
  "to": ["salil.kadam@gmail.com"],
  "subject": "Test Email",
  "body": "This is a test email.",
  "is_html": false
}
```

#### Email with CC and BCC
```json
{
  "to": ["recipient@example.com"],
  "cc": ["manager@example.com"],
  "bcc": ["archive@example.com"],
  "subject": "Project Update",
  "body": "Please find the project update attached.",
  "is_html": false
}
```

#### HTML Email
```json
{
  "to": ["recipient@example.com"],
  "subject": "HTML Email Test",
  "body": "<h1>Hello</h1><p>This is an <strong>HTML email</strong>.</p>",
  "is_html": true
}
```

#### Email with Attachments
```json
{
  "to": ["recipient@example.com"],
  "subject": "Document Attached",
  "body": "Please find the document attached.",
  "is_html": false,
  "attachments": ["/path/to/document.pdf", "/path/to/image.jpg"]
}
```

#### Complete Email (All Features)
```json
{
  "to": ["recipient@example.com"],
  "cc": ["manager@example.com"],
  "bcc": ["archive@example.com"],
  "subject": "Complete Email Test",
  "body": "<h1>Complete Email</h1><p>This email uses <strong>all features</strong>.</p>",
  "is_html": true,
  "attachments": ["/path/to/document.pdf"]
}
```

### Response Format
```json
{
  "message_id": "unique-message-id-12345",
  "status": "sent",
  "to": ["recipient@example.com"],
  "subject": "Test Email",
  "sent_at": "2025-09-14T23:30:00Z",
  "error_message": null
}
```

## Email History

### Get Email History
**Endpoint:** `GET /history`

**Headers:**
```
Authorization: Bearer <your_jwt_token>
```

**Query Parameters:**
- `limit` (optional): Number of emails to retrieve (default: 50)

**Response:**
```json
[
  {
    "message_id": "unique-message-id-12345",
    "status": "sent",
    "to": ["recipient@example.com"],
    "cc": ["manager@example.com"],
    "bcc": ["archive@example.com"],
    "subject": "Test Email",
    "body": "Email content",
    "is_html": false,
    "sent_at": "2025-09-14T23:30:00Z",
    "error_message": null,
    "created_at": "2025-09-14T23:30:00Z"
  }
]
```

## Health Check

### Get Service Health
**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-09-14T23:30:00Z",
  "kube_mail_connection": true
}
```

## Validation Rules

### Email Addresses
- Must be valid email format
- At least one recipient in `to` field is required
- CC and BCC are optional

### Subject
- Cannot be empty (after trimming whitespace)
- Maximum 200 characters

### Body
- Cannot be empty (after trimming whitespace)
- HTML content supported when `is_html: true`

### Attachments
- File must exist on the server
- Maximum file size: 10MB
- Supported file types:
  - Documents: `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.txt`
  - Images: `.jpg`, `.jpeg`, `.png`, `.gif`

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Incorrect username or password"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": "Email validation error: {'email_validation': ['Invalid email at position 0: invalid-email - The email address is not valid.']}"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to send email: SMTP connection failed"
}
```

## Complete cURL Examples

### 1. Get Token and Send Basic Email
```bash
# Get JWT token
TOKEN=$(curl -s -X POST https://mail.bionicaisolutions.com/api/v1/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=fedfinan@gmail.com&password=fedfina5@135PD" | jq -r '.access_token')

# Send basic email
curl -X POST https://mail.bionicaisolutions.com/api/v1/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["salil.kadam@gmail.com"],
    "subject": "Test Email",
    "body": "This is a test email.",
    "is_html": false
  }'
```

### 2. Send HTML Email with CC and BCC
```bash
curl -X POST https://mail.bionicaisolutions.com/api/v1/send \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["recipient@example.com"],
    "cc": ["manager@example.com"],
    "bcc": ["archive@example.com"],
    "subject": "HTML Email with CC/BCC",
    "body": "<h1>Hello</h1><p>This is an <strong>HTML email</strong> with CC and BCC.</p>",
    "is_html": true
  }'
```

### 3. Get Email History
```bash
curl -X GET https://mail.bionicaisolutions.com/api/v1/history \
  -H "Authorization: Bearer $TOKEN"
```

## Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized (invalid credentials) |
| 404 | Resource not found (attachment files) |
| 413 | Request too large (attachment size) |
| 415 | Unsupported media type (file type) |
| 422 | Validation error |
| 500 | Internal server error |

## Features Summary

✅ **Complete Email Functionality:**
- ✅ To recipients (required)
- ✅ CC recipients (optional)
- ✅ BCC recipients (optional)
- ✅ HTML email support
- ✅ File attachments (up to 10MB)
- ✅ JWT authentication
- ✅ Email history tracking
- ✅ Comprehensive validation
- ✅ Error handling
- ✅ Health monitoring

The Mail Service API is now fully functional with all requested features implemented and tested! 🎉
