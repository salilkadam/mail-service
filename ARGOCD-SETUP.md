# 🚀 ArgoCD Setup Guide for Mail Service

This guide will help you set up ArgoCD for deploying the Mail Service to Kubernetes.

## 📋 Prerequisites

- ✅ Kubernetes cluster with ArgoCD installed
- ✅ GitHub repository with Docker images
- ✅ ArgoCD CLI installed (optional)
- ✅ Access to ArgoCD UI

## 🔧 ArgoCD Configuration

### 1. Repository Configuration

The ArgoCD applications are configured to use:
- **Repository**: `https://github.com/salilkadam/mail-service`
- **Staging Branch**: `develop`
- **Production Branch**: `main`
- **Manifest Path**: `k8s/`

### 2. Application Manifests

#### Staging Application (`argocd/mail-service-staging.yaml`):
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: mail-service-staging
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/salilkadam/mail-service
    targetRevision: develop
    path: k8s
    helm:
      valueFiles:
        - values-staging.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: mail-service-staging
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

#### Production Application (`argocd/mail-service-production.yaml`):
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: mail-service-production
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/salilkadam/mail-service
    targetRevision: main
    path: k8s
    helm:
      valueFiles:
        - values-production.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: mail-service-prod
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

## 🚀 Deployment Process

### 1. Initial Setup

Apply the ArgoCD applications to your cluster:

```bash
# Apply staging application
kubectl apply -f argocd/mail-service-staging.yaml

# Apply production application
kubectl apply -f argocd/mail-service-production.yaml
```

### 2. GitHub Actions Integration

The GitHub Actions workflow will:

1. **Build and push** Docker images to Docker Hub
2. **Update** Kubernetes manifests with new image tags
3. **Commit and push** changes to the repository
4. **Trigger** ArgoCD sync automatically

### 3. Automatic Deployment

ArgoCD will automatically:
- ✅ **Detect** changes in the repository
- ✅ **Sync** the application with new manifests
- ✅ **Deploy** updated images to Kubernetes
- ✅ **Monitor** deployment health

## 🔍 Monitoring and Management

### ArgoCD UI

Access the ArgoCD UI to:
- Monitor deployment status
- View application health
- Check sync status
- Review deployment history

### ArgoCD CLI Commands

```bash
# Check application status
argocd app get mail-service-staging
argocd app get mail-service-production

# Sync application manually
argocd app sync mail-service-staging
argocd app sync mail-service-production

# Check application logs
argocd app logs mail-service-staging
argocd app logs mail-service-production

# List all applications
argocd app list

# Get application details
argocd app get mail-service-staging --show-params
```

### Kubernetes Commands

```bash
# Check pods in staging
kubectl get pods -n mail-service-staging

# Check pods in production
kubectl get pods -n mail-service-prod

# Check services
kubectl get services -n mail-service-staging
kubectl get services -n mail-service-prod

# Check ingress
kubectl get ingress -n mail-service-staging
kubectl get ingress -n mail-service-prod
```

## 🌍 Environment Configuration

### Staging Environment
- **Namespace**: `mail-service-staging`
- **Replicas**: 1
- **Resources**: 250m CPU, 256Mi Memory
- **URL**: `mail-service-staging.local`
- **Debug**: Enabled

### Production Environment
- **Namespace**: `mail-service-prod`
- **Replicas**: 2
- **Resources**: 500m CPU, 512Mi Memory
- **URL**: `mail-service.bionicaisolutions.com`
- **Debug**: Disabled
- **Auto-scaling**: Enabled (2-10 replicas)

## 🔄 Deployment Workflow

### 1. Code Changes
```bash
# Make changes to your code
git add .
git commit -m "Update mail service"
git push origin develop  # For staging
git push origin main     # For production
```

### 2. GitHub Actions
- Automatically builds Docker images
- Pushes to Docker Hub
- Updates Kubernetes manifests
- Commits changes to repository

### 3. ArgoCD Sync
- Detects repository changes
- Syncs application automatically
- Deploys new images to Kubernetes
- Monitors deployment health

## 🚨 Troubleshooting

### Common Issues:

1. **Application Not Syncing**
   ```bash
   # Check application status
   argocd app get mail-service-staging
   
   # Force sync
   argocd app sync mail-service-staging --force
   ```

2. **Image Pull Errors**
   ```bash
   # Check pod events
   kubectl describe pod -n mail-service-staging
   
   # Check image pull secrets
   kubectl get secrets -n mail-service-staging
   ```

3. **Service Not Accessible**
   ```bash
   # Check service endpoints
   kubectl get endpoints -n mail-service-staging
   
   # Check ingress configuration
   kubectl describe ingress -n mail-service-staging
   ```

### Debug Commands:

```bash
# Check ArgoCD application health
argocd app get mail-service-staging --show-params

# Check Kubernetes resources
kubectl get all -n mail-service-staging

# Check application logs
kubectl logs -n mail-service-staging -l app.kubernetes.io/name=mail-service-backend

# Check ArgoCD sync status
argocd app sync mail-service-staging --dry-run
```

## 📚 Best Practices

### 1. GitOps Workflow
- ✅ All changes go through Git
- ✅ ArgoCD syncs from repository
- ✅ No manual kubectl commands
- ✅ Version control for all configurations

### 2. Environment Separation
- ✅ Separate namespaces for staging/production
- ✅ Different resource limits
- ✅ Environment-specific configurations
- ✅ Independent scaling policies

### 3. Monitoring and Alerting
- ✅ ArgoCD health checks
- ✅ Kubernetes health probes
- ✅ Application metrics
- ✅ Log aggregation

## 🔒 Security Considerations

### 1. Access Control
- ✅ ArgoCD RBAC configuration
- ✅ Kubernetes RBAC policies
- ✅ Network policies
- ✅ Image security scanning

### 2. Secrets Management
- ✅ Use Kubernetes secrets
- ✅ ArgoCD secret management
- ✅ Encrypted storage
- ✅ Regular rotation

## 🆘 Support

If you encounter issues:

1. Check the [troubleshooting section](#-troubleshooting)
2. Review ArgoCD application logs
3. Check Kubernetes pod events
4. Verify repository access and permissions

---

**Note**: This setup provides a complete GitOps workflow for deploying the Mail Service to Kubernetes using ArgoCD. The system automatically builds, pushes, and deploys images whenever changes are pushed to the repository.
