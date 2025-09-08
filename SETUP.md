# Mail Service Setup Guide

This guide will help you set up the Mail Service with GitHub Actions CI/CD for Kubernetes deployment.

## 🚀 Quick Setup

### 1. Repository Setup

1. **Fork or Clone** this repository
2. **Update image references** in Kubernetes manifests:
   ```bash
   # Replace 'your-username' with your GitHub username
   sed -i 's/your-username/YOUR_GITHUB_USERNAME/g' k8s/*.yaml
   ```

### 2. GitHub Secrets Configuration

Configure the following secrets in your GitHub repository settings:

#### Required Secrets:
```bash
# Kubernetes cluster configuration (base64 encoded kubeconfig)
KUBE_CONFIG=<base64-encoded-kubeconfig>
```

#### Optional Secrets:
```bash
# Custom registry credentials (if not using GitHub Container Registry)
REGISTRY_USERNAME=<registry-username>
REGISTRY_PASSWORD=<registry-password>
```

### 3. Kubernetes Cluster Setup

#### Prerequisites:
- Kubernetes cluster (v1.20+)
- kubectl configured to access your cluster
- kube-mail SMTP server (or configure custom SMTP)

#### Deploy kube-mail (if needed):
```bash
# Apply kube-mail manifests
kubectl apply -f k8s/kube-mail-smtp-server.yaml
kubectl apply -f k8s/kube-mail-email-policy.yaml
```

### 4. GitHub Actions Setup

The repository includes the following workflows:

- **`test.yml`**: Runs tests and security scans
- **`build.yml`**: Builds and pushes Docker images
- **`deploy-k8s.yml`**: Deploys to Kubernetes

#### Workflow Triggers:
- **Push to `main`**: Deploys to production
- **Push to `develop`**: Deploys to staging
- **Manual dispatch**: Deploy specific version to any environment

## 🔧 Configuration

### Environment Variables

Update the ConfigMap in `k8s/configmap.yaml`:

```yaml
data:
  KUBE_MAIL_HOST: "kube-mail.kube-system.svc.cluster.local"
  KUBE_MAIL_PORT: "25"
  FROM_EMAIL: "your-email@yourdomain.com"
  FROM_NAME: "Your Company Name"
  DEBUG: "false"
  LOG_LEVEL: "INFO"
  CORS_ORIGINS: '["https://yourdomain.com"]'
```

### Custom Domain

Update the ingress in `k8s/ingress.yaml`:

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

## 📋 Deployment Process

### Automatic Deployment

1. **Push to `main` branch** → Production deployment
2. **Push to `develop` branch** → Staging deployment

### Manual Deployment

1. Go to **Actions** tab in GitHub
2. Select **"Deploy to Kubernetes"** workflow
3. Click **"Run workflow"**
4. Choose environment and image tag
5. Click **"Run workflow"**

### Local Deployment

```bash
# Make deployment script executable
chmod +x scripts/deploy.sh

# Deploy to staging
./scripts/deploy.sh staging latest

# Deploy to production
./scripts/deploy.sh production v1.0.0
```

## 🏥 Health Checks

After deployment, verify the services are running:

```bash
# Check pods
kubectl get pods -n mail-service-prod

# Check services
kubectl get services -n mail-service-prod

# Check ingress
kubectl get ingress -n mail-service-prod

# Test health endpoint
kubectl port-forward svc/mail-service-backend 8000:8000 -n mail-service-prod
curl http://localhost:8000/api/v1/health
```

## 🔒 Security

### Network Policies

Network policies are included to restrict traffic between services.

### RBAC

The deployment uses minimal required permissions.

### Secrets Management

Store sensitive data in Kubernetes secrets:

```bash
kubectl create secret generic mail-service-secrets \
  --from-literal=smtp-username=your-username \
  --from-literal=smtp-password=your-password \
  -n mail-service-prod
```

## 🚨 Troubleshooting

### Common Issues

1. **Image Pull Errors**
   - Check if images exist in registry
   - Verify image pull secrets

2. **Pod Startup Issues**
   - Check pod logs: `kubectl logs <pod-name> -n <namespace>`
   - Check pod events: `kubectl describe pod <pod-name> -n <namespace>`

3. **Service Connectivity**
   - Verify network policies
   - Check service endpoints

### Debug Commands

```bash
# Get all resources
kubectl get all -n mail-service-prod

# Check resource usage
kubectl top pods -n mail-service-prod

# View logs
kubectl logs -f deployment/mail-service-backend -n mail-service-prod
```

## 📊 Monitoring

### View Deployment Status

```bash
# Check deployment status
kubectl rollout status deployment/mail-service-backend -n mail-service-prod

# Check pod status
kubectl get pods -n mail-service-prod -o wide

# Check service endpoints
kubectl get endpoints -n mail-service-prod
```

### Scaling

```bash
# Scale backend
kubectl scale deployment mail-service-backend --replicas=3 -n mail-service-prod

# Scale frontend
kubectl scale deployment mail-service-frontend --replicas=3 -n mail-service-prod
```

## 🔄 Rollback

```bash
# View deployment history
kubectl rollout history deployment/mail-service-backend -n mail-service-prod

# Rollback to previous version
kubectl rollout undo deployment/mail-service-backend -n mail-service-prod

# Rollback to specific revision
kubectl rollout undo deployment/mail-service-backend --to-revision=2 -n mail-service-prod
```

## 📚 Additional Resources

- [DEPLOYMENT.md](./DEPLOYMENT.md) - Detailed deployment guide
- [README.md](./README.md) - Project overview
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## 🆘 Support

If you encounter issues:

1. Check the [troubleshooting section](#-troubleshooting)
2. Review the GitHub Actions logs
3. Check the Kubernetes events and logs
4. Open an issue in the repository

