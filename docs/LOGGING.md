# Enhanced Logging Configuration

This document describes the comprehensive logging system implemented in the mail service, including dynamic configuration options for production debugging.

## Overview

The mail service now includes a sophisticated logging system with the following features:

- **Structured Logging**: JSON and text formats with consistent field structure
- **Request Tracing**: Unique request IDs and correlation IDs for tracking requests across services
- **Performance Monitoring**: Automatic timing and slow request detection
- **Dynamic Configuration**: Environment-based logging configuration that can be changed without code deployment
- **Security Controls**: Configurable sensitive data redaction
- **Contextual Information**: User IDs, request paths, and operation tracking

## Logging Configuration

### Environment Variables

All logging behavior can be controlled via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `LOG_FORMAT` | `json` | Output format (json, text) |
| `LOG_FILE_ENABLED` | `false` | Enable file logging |
| `LOG_FILE_PATH` | `./logs/app.log` | Log file path |
| `LOG_INCLUDE_REQUEST_ID` | `true` | Include request IDs in logs |
| `LOG_INCLUDE_USER_INFO` | `true` | Include user information in logs |
| `LOG_INCLUDE_SENSITIVE_DATA` | `false` | Include sensitive data (passwords, tokens) |
| `LOG_PERFORMANCE_METRICS` | `true` | Include performance timing information |
| `LOG_SMTP_DETAILS` | `false` | Log SMTP connection details |
| `LOG_EMAIL_CONTENT` | `false` | Log email content (be careful with sensitive data) |
| `LOG_CORRELATION_ID` | `true` | Include correlation IDs for distributed tracing |
| `LOG_REQUEST_RESPONSE` | `false` | Log full request/response data |
| `LOG_SLOW_REQUESTS_THRESHOLD` | `1.0` | Log requests slower than this (seconds) |

### Logging Presets

#### Production (Default)
```bash
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_SMTP_DETAILS=false
LOG_EMAIL_CONTENT=false
LOG_REQUEST_RESPONSE=false
LOG_INCLUDE_SENSITIVE_DATA=false
```

#### Debug Mode
```bash
LOG_LEVEL=DEBUG
LOG_SMTP_DETAILS=true
LOG_EMAIL_CONTENT=true
LOG_REQUEST_RESPONSE=true
LOG_INCLUDE_SENSITIVE_DATA=true
```

#### Performance Monitoring
```bash
LOG_LEVEL=INFO
LOG_PERFORMANCE_METRICS=true
LOG_SLOW_REQUESTS_THRESHOLD=0.5
```

#### Security Mode
```bash
LOG_LEVEL=INFO
LOG_INCLUDE_SENSITIVE_DATA=false
LOG_EMAIL_CONTENT=false
LOG_REQUEST_RESPONSE=false
LOG_SMTP_DETAILS=false
```

## Dynamic Configuration

### Kubernetes Production

To enable debug logging in production without code changes:

```bash
# Enable debug logging
kubectl patch configmap mail-service-config -n mail-service-prod --type merge -p '{
  "data": {
    "LOG_LEVEL": "DEBUG",
    "LOG_SMTP_DETAILS": "true",
    "LOG_EMAIL_CONTENT": "true",
    "LOG_REQUEST_RESPONSE": "true",
    "LOG_INCLUDE_SENSITIVE_DATA": "true"
  }
}'

# Restart deployment to apply changes
kubectl rollout restart deployment/backend-deployment -n mail-service-prod
```

### Docker Compose Development

Add to your `docker-compose.yml` environment section:

```yaml
environment:
  - LOG_LEVEL=DEBUG
  - LOG_SMTP_DETAILS=true
  - LOG_EMAIL_CONTENT=true
  - LOG_REQUEST_RESPONSE=true
  - LOG_INCLUDE_SENSITIVE_DATA=true
```

## Log Structure

### JSON Format Example

```json
{
  "timestamp": "2024-01-15T10:30:45",
  "level": "INFO",
  "logger": "app.mail_service",
  "message": "Email sent successfully",
  "module": "mail_service",
  "function": "send_email",
  "line": 110,
  "request_id": "req_12345678",
  "correlation_id": "corr_87654321",
  "user_id": "user@example.com",
  "message_id": "msg_abcdef12",
  "to": ["recipient@example.com"],
  "subject": "Test Email",
  "duration": 0.245,
  "performance_metrics": {
    "duration_seconds": 0.245,
    "duration_ms": 245
  }
}
```

### Text Format Example

```
2024-01-15 10:30:45 INFO     app.mail_service [req:12345678] [corr:87654321] [user:user@example.com]: Email sent successfully
```

## Request Tracing

Every request receives:
- **Request ID**: Unique identifier for the request
- **Correlation ID**: For distributed tracing across services
- **User ID**: When authenticated

These are included in response headers:
- `X-Request-ID`
- `X-Correlation-ID`

## Performance Monitoring

The system automatically tracks:
- Request duration
- Slow request detection (configurable threshold)
- SMTP connection timing
- Email processing time

## Security Features

### Sensitive Data Protection

When `LOG_INCLUDE_SENSITIVE_DATA=false` (default):
- Passwords and tokens are redacted
- SMTP credentials are hidden
- Email content can be selectively logged

### Audit Trail

All email operations are logged with:
- User identification
- Timestamp
- Operation type
- Success/failure status
- Error details (when applicable)

## Configuration Script

Use the provided script to manage logging configuration:

```bash
# Show current configuration
python scripts/configure_logging.py --current

# Show all configuration options
python scripts/configure_logging.py --all

# Generate kubectl commands for production
python scripts/configure_logging.py --kubectl

# Show logging presets
python scripts/configure_logging.py --presets
```

## Troubleshooting

### Common Issues

1. **Too much logging**: Set `LOG_LEVEL=WARNING` or `LOG_LEVEL=ERROR`
2. **Missing request context**: Ensure `LOG_INCLUDE_REQUEST_ID=true`
3. **Performance impact**: Disable `LOG_PERFORMANCE_METRICS=false`
4. **Sensitive data exposure**: Ensure `LOG_INCLUDE_SENSITIVE_DATA=false`

### Debugging Email Issues

Enable debug logging for email problems:

```bash
# Kubernetes
kubectl patch configmap mail-service-config -n mail-service-prod --type merge -p '{
  "data": {
    "LOG_LEVEL": "DEBUG",
    "LOG_SMTP_DETAILS": "true",
    "LOG_EMAIL_CONTENT": "true"
  }
}'

# Restart deployment
kubectl rollout restart deployment/backend-deployment -n mail-service-prod
```

### Monitoring Slow Requests

```bash
# Set threshold to 0.5 seconds
kubectl patch configmap mail-service-config -n mail-service-prod --type merge -p '{
  "data": {
    "LOG_SLOW_REQUESTS_THRESHOLD": "0.5"
  }
}'
```

## Log Analysis

### Finding Email Issues

```bash
# Search for failed emails
kubectl logs -n mail-service-prod deployment/backend-deployment | jq 'select(.level == "ERROR" and .message | contains("Failed to send email"))'

# Search by request ID
kubectl logs -n mail-service-prod deployment/backend-deployment | jq 'select(.request_id == "req_12345678")'

# Search by user
kubectl logs -n mail-service-prod deployment/backend-deployment | jq 'select(.user_id == "user@example.com")'
```

### Performance Analysis

```bash
# Find slow requests
kubectl logs -n mail-service-prod deployment/backend-deployment | jq 'select(.performance_metrics.duration_seconds > 1.0)'

# SMTP connection issues
kubectl logs -n mail-service-prod deployment/backend-deployment | jq 'select(.message | contains("SMTP"))'
```

## Best Practices

1. **Production**: Use INFO level with minimal sensitive data logging
2. **Debugging**: Temporarily enable DEBUG level and relevant detail flags
3. **Security**: Never enable sensitive data logging in production
4. **Performance**: Monitor slow request thresholds
5. **Monitoring**: Use structured JSON logs for log aggregation systems
6. **Rotation**: Enable log file rotation for file-based logging

## Integration with Monitoring Systems

The structured JSON logs are compatible with:
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Fluentd
- Prometheus + Grafana
- Cloud logging services (AWS CloudWatch, Google Cloud Logging)

Example log aggregation query:
```json
{
  "query": {
    "bool": {
      "must": [
        {"term": {"level": "ERROR"}},
        {"term": {"logger": "app.mail_service"}}
      ]
    }
  }
}
```
