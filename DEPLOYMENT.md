# Mail Service Kubernetes Deployment Guide

This guide covers deploying the Mail Service to Kubernetes using GitHub Actions CI/CD pipeline.

## 🏗️ Architecture

The Mail Service consists of:
- **Backend**: FastAPI application running on port 8000
- **Frontend**: React application served by Nginx on port 80
- **kube-mail**: SMTP server for sending emails
- **Ingress**: External access to the services

## 🚀 Quick Start

### Prerequisites

1. **Kubernetes Cluster**: Access to a Kubernetes cluster (v1.20+)
2. **kubectl**: Configured to access your cluster
3. **GitHub Repository**: With GitHub Actions enabled
4. **Container Registry**: GitHub Container Registry (ghcr.io) or custom registry

### GitHub Secrets

Configure the following secrets in your GitHub repository:

```bash
# Kubernetes cluster configuration
KUBE_CONFIG=<base64-encoded-kubeconfig>

# Optional: Custom registry credentials
REGISTRY_USERNAME=<registry-username>
REGISTRY_PASSWORD=<registry-password>
```

### Deployment Environments

- **Staging**: Deploys from `develop` branch to `mail-service-staging` namespace
- **Production**: Deploys from `main` branch to `mail-service-prod` namespace

## 📋 Deployment Process

### 1. Automatic Deployment (GitHub Actions)

The deployment is triggered automatically when you push to:
- `main` branch → Production deployment
- `develop` branch → Staging deployment

#### Workflow Steps:
1. **Test**: Run unit tests and code quality checks
2. **Build**: Build and push Docker images to registry
3. **Deploy**: Deploy to Kubernetes cluster
4. **Health Check**: Verify deployment health

### 2. Manual Deployment

#### Using the deployment script:

```bash
# Deploy to staging
./scripts/deploy.sh staging latest

# Deploy to production
./scripts/deploy.sh production v1.0.0
```

#### Using kubectl directly:

```bash
# Update image tags in manifests
sed -i "s|image: mail-service-backend:latest|image: ghcr.io/your-username/mail-service/backend:v1.0.0|g" k8s/backend-deployment.yaml
sed -i "s|image: mail-service-frontend:latest|image: ghcr.io/your-username/mail-service/frontend:v1.0.0|g" k8s/frontend-deployment.yaml

# Apply manifests
kubectl apply -f k8s/namespace-production.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml
kubectl apply -f k8s/ingress.yaml
```

## 🔧 Configuration

### Environment Variables

The application is configured via ConfigMap and environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `KUBE_MAIL_HOST` | kube-mail server hostname | `kube-mail.kube-system.svc.cluster.local` |
| `KUBE_MAIL_PORT` | kube-mail server port | `25` |
| `FROM_EMAIL` | Default sender email | `info@bionicaisolutions.com` |
| `FROM_NAME` | Default sender name | `Bionic AI Solutions` |
| `DEBUG` | Enable debug mode | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `CORS_ORIGINS` | Allowed CORS origins | `["http://localhost:3000"]` |

### Resource Requirements

#### Backend:
- **Requests**: 256Mi memory, 250m CPU
- **Limits**: 512Mi memory, 500m CPU

#### Frontend:
- **Requests**: 128Mi memory, 100m CPU
- **Limits**: 256Mi memory, 200m CPU

## 🏥 Health Checks

### Liveness Probes
- **Backend**: `GET /api/v1/health`
- **Frontend**: `GET /health`

### Readiness Probes
- **Backend**: `GET /api/v1/health`
- **Frontend**: `GET /health`

### Health Check Endpoints

```bash
# Backend health
curl http://backend-service:8000/api/v1/health

# Frontend health
curl http://frontend-service:80/health
```

## 📊 Monitoring

### View Deployment Status

```bash
# Check pods
kubectl get pods -n mail-service-prod

# Check services
kubectl get services -n mail-service-prod

# Check ingress
kubectl get ingress -n mail-service-prod

# View logs
kubectl logs -f deployment/mail-service-backend -n mail-service-prod
kubectl logs -f deployment/mail-service-frontend -n mail-service-prod
```

### Scaling

```bash
# Scale backend
kubectl scale deployment mail-service-backend --replicas=3 -n mail-service-prod

# Scale frontend
kubectl scale deployment mail-service-frontend --replicas=3 -n mail-service-prod
```

## 🔒 Security

### Network Policies

The deployment includes network policies to restrict traffic between services.

### RBAC

Service accounts with minimal required permissions are used for deployments.

### Secrets Management

Sensitive configuration should be stored in Kubernetes secrets:

```bash
# Create secret for SMTP credentials
kubectl create secret generic mail-service-secrets \
  --from-literal=smtp-username=your-username \
  --from-literal=smtp-password=your-password \
  -n mail-service-prod
```

## 🚨 Troubleshooting

### Common Issues

1. **Image Pull Errors**
   ```bash
   # Check image pull secrets
   kubectl get secrets -n mail-service-prod
   
   # Verify image exists
   docker pull ghcr.io/your-username/mail-service/backend:latest
   ```

2. **Pod Startup Issues**
   ```bash
   # Check pod events
   kubectl describe pod <pod-name> -n mail-service-prod
   
   # Check logs
   kubectl logs <pod-name> -n mail-service-prod
   ```

3. **Service Connectivity**
   ```bash
   # Test service connectivity
   kubectl run test-pod --image=busybox -it --rm -- nslookup mail-service-backend
   ```

### Debug Commands

```bash
# Get all resources
kubectl get all -n mail-service-prod

# Check resource usage
kubectl top pods -n mail-service-prod

# Port forward for local testing
kubectl port-forward svc/mail-service-backend 8000:8000 -n mail-service-prod
kubectl port-forward svc/mail-service-frontend 3000:80 -n mail-service-prod
```

## 🔄 Rollback

### Rollback Deployment

```bash
# View deployment history
kubectl rollout history deployment/mail-service-backend -n mail-service-prod

# Rollback to previous version
kubectl rollout undo deployment/mail-service-backend -n mail-service-prod

# Rollback to specific revision
kubectl rollout undo deployment/mail-service-backend --to-revision=2 -n mail-service-prod
```

## 📈 Performance Tuning

### Resource Optimization

1. **Monitor resource usage**:
   ```bash
   kubectl top pods -n mail-service-prod
   ```

2. **Adjust resource limits** based on actual usage

3. **Enable horizontal pod autoscaling**:
   ```bash
   kubectl autoscale deployment mail-service-backend --cpu-percent=70 --min=2 --max=10 -n mail-service-prod
   ```

### Caching

- Frontend assets are cached with 1-year expiration
- API responses can be cached at the ingress level

## 🔧 Customization

### Custom Registry

To use a different container registry, update the GitHub Actions workflow:

```yaml
env:
  REGISTRY: your-registry.com
  IMAGE_NAME: your-org/mail-service
```

### Custom Domain

Update the ingress configuration:

```yaml
spec:
  rules:
  - host: mail.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: mail-service-frontend
            port:
              number: 80
```

## 📚 Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

