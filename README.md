# Mail Service

A comprehensive mail service application for sending emails via kube-mail pod with sender address `info@bionicaisolutions.com`.

## Features

- **Backend API**: FastAPI-based REST API for email operations
- **Frontend UI**: React-based web interface for composing and sending emails
- **kube-mail Integration**: Seamless integration with Kubernetes kube-mail service
- **Email History**: Track and view email sending history
- **Health Monitoring**: Real-time health checks and service status
- **Docker Support**: Containerized deployment with Docker and Docker Compose
- **Kubernetes Ready**: Complete Kubernetes manifests for production deployment

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   kube-mail     │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (Kubernetes)  │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 25      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

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

1. **Install kube-mail (if not already installed):**
   ```bash
   helm repo add mittwald https://helm.mittwald.de
   helm repo update
   helm install kube-mail mittwald/kube-mail --namespace kube-system
   ```

2. **Configure SMTP server:**
   ```bash
   kubectl apply -f k8s/kube-mail-smtp-server.yaml
   ```

3. **Deploy the mail service:**
   ```bash
   kubectl apply -f k8s/
   ```

4. **Configure email policy:**
   ```bash
   kubectl apply -f k8s/kube-mail-email-policy.yaml
   ```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `KUBE_MAIL_HOST` | kube-mail service hostname | `kube-mail.kube-system.svc.cluster.local` |
| `KUBE_MAIL_PORT` | kube-mail service port | `25` |
| `FROM_EMAIL` | Default sender email | `info@bionicaisolutions.com` |
| `FROM_NAME` | Default sender name | `Bionic AI Solutions` |
| `DEBUG` | Enable debug mode | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |

### SMTP Server Configuration

Update `k8s/kube-mail-smtp-server.yaml` with your actual SMTP server details:

```yaml
spec:
  server: your-smtp-server.com
  port: 587
  tls: true
  authType: PLAIN
  # Add authentication credentials via Kubernetes secrets
```

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

1. **kube-mail Connection Failed**
   - Verify kube-mail is installed and running
   - Check SMTP server configuration
   - Ensure network connectivity

2. **Frontend Cannot Connect to Backend**
   - Verify backend service is running
   - Check CORS configuration
   - Ensure correct API URL in frontend

3. **Email Sending Fails**
   - Check SMTP server credentials
   - Verify email policy configuration
   - Review kube-mail logs

### Logs

```bash
# Backend logs
docker-compose logs backend

# Frontend logs
docker-compose logs frontend

# Kubernetes logs
kubectl logs -n mail-service deployment/mail-service-backend
kubectl logs -n mail-service deployment/mail-service-frontend
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
