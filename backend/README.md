# Mail Service Backend

A FastAPI-based mail service for sending emails via kube-mail.

## Features

- Send emails with support for HTML and plain text
- Email history tracking
- Health check endpoints
- Integration with kube-mail SMTP server

## API Endpoints

- `POST /api/v1/send` - Send an email
- `GET /api/v1/history` - Get email history
- `GET /api/v1/health` - Health check

## Configuration

The service uses environment variables for configuration:

- `KUBE_MAIL_HOST` - kube-mail server host
- `KUBE_MAIL_PORT` - kube-mail server port
- `FROM_EMAIL` - Default sender email
- `FROM_NAME` - Default sender name
- `DEBUG` - Enable debug mode
- `LOG_LEVEL` - Logging level
- `CORS_ORIGINS` - Allowed CORS origins

