# Mail Service

A comprehensive mail service application for sending emails via Postfix SMTP relay with sender address `info@bionicaisolutions.com`.

## Features

- **Backend API**: FastAPI-based REST API for email operations
- **Frontend UI**: React-based web interface for composing and sending emails
- **Postfix SMTP Relay**: Production-ready SMTP relay service for reliable email delivery
- **Gmail Workspace Integration**: Seamless integration with Gmail Workspace SMTP relay
- **Email History**: Track and view email sending history
- **Health Monitoring**: Real-time health checks and service status
- **Docker Support**: Containerized deployment with Docker and Docker Compose
- **Kubernetes Ready**: Complete Kubernetes manifests for production deployment
- **Helm Charts**: Easy deployment and management with Helm
- **Monitoring**: Prometheus metrics and alerting support

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │  Postfix SMTP   │    │  Gmail Workspace│
│   (React)       │◄──►│   (FastAPI)     │◄──►│     Relay       │◄──►│  SMTP Relay     │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 25      │    │   Port: 587     │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Email Server Infrastructure

This project includes a complete email server infrastructure with:

- **Postfix SMTP Relay**: High-availability SMTP relay service
- **Network Policies**: Secure network access control
- **Monitoring**: Prometheus metrics and alerting
- **Helm Charts**: Easy deployment and management
- **Documentation**: Comprehensive setup and usage guides

See [README-EMAIL-SERVER.md](README-EMAIL-SERVER.md) for detailed email server documentation.

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Kubernetes cluster (for kube-mail integration)
- Python 3.9+ (for local development)
- Node.js 18+ (for frontend development)

### Local Development with Docker

1. **Clone and navigate to the project:**
   ```bash
   cd /workspace/mail
   ```

2. **Start the services:**
   ```bash
   docker-compose up -d
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Kubernetes Deployment

1. **Deploy the email server infrastructure:**
   ```bash
   # Using Helm (recommended)
   helm install email-server ./helm/email-server \
     --namespace email-server-prod \
     --create-namespace
   
   # Or using Kustomize
   kubectl apply -k k8s/email-server/
   ```

2. **Deploy the mail service:**
   ```bash
   kubectl apply -f k8s/
   ```

3. **Configure namespace access:**
   ```bash
   # Add label to allow SMTP access
   kubectl label namespace mail-service-prod email-server.kubernetes.io/smtp-access=true
   ```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTFIX_HOST` | Postfix SMTP relay hostname | `postfix-relay.email-server-prod.svc.cluster.local` |
| `POSTFIX_PORT` | Postfix SMTP relay port | `25` |
| `FROM_EMAIL` | Default sender email | `info@bionicaisolutions.com` |
| `FROM_NAME` | Default sender name | `Bionic AI Solutions` |
| `DEBUG` | Enable debug mode | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Email Server Configuration

The email server is configured to use Gmail Workspace SMTP relay:

- **Relay Host**: `smtp-relay.gmail.com:587`
- **Authentication**: IP-based (no credentials required)
- **TLS**: Enabled for secure communication
- **Allowed Domains**: `bionicaisolutions.com`, `gmail.com`

### Gmail Workspace Setup

1. **IP Whitelisting**: Add your server's public IP to Gmail Workspace SMTP Relay settings
2. **Domain Configuration**: Ensure `bionicaisolutions.com` is verified in Gmail Workspace
3. **SMTP Relay**: Configure SMTP relay service in Google Admin Console

## API Endpoints

### Send Email
```http
POST /api/v1/send
Content-Type: application/json

{
  "to": ["recipient@example.com"],
  "cc": ["cc@example.com"],
  "bcc": ["bcc@example.com"],
  "subject": "Email Subject",
  "body": "Email body content",
  "is_html": false
}
```

### Get Email History
```http
GET /api/v1/history?limit=50
```

### Get Email by ID
```http
GET /api/v1/history/{message_id}
```

### Health Check
```http
GET /api/v1/health
```

## Testing

### Run Unit Tests
```bash
cd backend
poetry install
poetry run pytest tests/unit/ -v
```

### Run Integration Tests
```bash
cd backend
ENV=test poetry run pytest tests/integratione2e/ -v
```

### Check Services
```bash
python scripts/check_services.py
```

### Generate Sample Data
```bash
# Generate sample data (dry run)
python scripts/generate_sample_data.py 5

# Actually send sample emails
python scripts/generate_sample_data.py 5 --send
```

## Development

### Backend Development

1. **Install dependencies:**
   ```bash
   cd backend
   poetry install
   ```

2. **Run the development server:**
   ```bash
   poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Development

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Run the development server:**
   ```bash
   npm start
   ```

## Monitoring and Health Checks

The application includes comprehensive health monitoring:

- **Backend Health**: `/api/v1/health` endpoint
- **Frontend Health**: `/health` endpoint
- **kube-mail Connection**: Automatic connection testing
- **Docker Health Checks**: Built-in container health monitoring

## Security Features

- **CORS Configuration**: Configurable cross-origin resource sharing
- **Input Validation**: Comprehensive email and data validation
- **Error Handling**: Secure error messages without sensitive information
- **Security Headers**: Nginx security headers for frontend

## Troubleshooting

### Common Issues

1. **Postfix SMTP Relay Connection Failed**
   - Verify email server is deployed and running
   - Check namespace labels for SMTP access
   - Ensure network policies are configured correctly

2. **Frontend Cannot Connect to Backend**
   - Verify backend service is running
   - Check CORS configuration
   - Ensure correct API URL in frontend

3. **Email Sending Fails**
   - Check Gmail Workspace SMTP relay configuration
   - Verify IP address is whitelisted
   - Review Postfix logs for error messages

4. **Email Bounces**
   - Check Gmail Workspace domain configuration
   - Verify sender domain is properly configured
   - Review Postfix logs for specific error codes

### Logs

```bash
# Backend logs
docker-compose logs backend

# Frontend logs
docker-compose logs frontend

# Kubernetes logs
kubectl logs -n mail-service-prod deployment/mail-service-backend
kubectl logs -n mail-service-prod deployment/mail-service-frontend

# Email server logs
kubectl logs -n email-server-prod deployment/postfix-relay
```

## Contributing

1. Create a feature branch: `git checkout -b feature/new-feature`
2. Make your changes
3. Run tests: `poetry run pytest`
4. Commit your changes: `git commit -m "Add new feature"`
5. Push to the branch: `git push origin feature/new-feature`
6. Create a Pull Request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact:
- Email: info@bionicaisolutions.com
- Documentation: See `docs/feature/mail-service/` directory
# Trigger workflow
