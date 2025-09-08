# 🚀 ArgoCD Integration Summary for Mail Service

## 📋 Current Setup Analysis

Based on your existing ArgoCD installation, I've configured the mail service to integrate seamlessly with your current setup.

### ✅ Existing Infrastructure:
- **ArgoCD Namespace**: `argocd` (active for 52 days)
- **Repository**: `Bionic-AI-Solutions/new-api` already configured
- **Docker Hub Credentials**: Already configured
  - Username: `docker4zerocool`
  - Password: `[Your Docker Hub Personal Access Token]`
  - Email: `Salil.Kadam@Gmail.com`
- **Multiple Applications**: Already managed by ArgoCD

## 🔧 Configuration Updates Made

### 1. Repository Configuration
- **Updated repository URL** to: `https://github.com/Bionic-AI-Solutions/mail-service`
- **Removed Helm dependencies** (using plain Kubernetes manifests)
- **Configured for both staging and production** environments

### 2. Docker Registry Integration
- **Created Docker registry secret** using your existing credentials
- **Added imagePullSecrets** to both backend and frontend deployments
- **Configured for both namespaces** (staging and production)

### 3. GitHub Actions Integration
- **Updated Docker Hub login** to use your existing credentials
- **Configured automatic image building** and pushing
- **Set up ArgoCD application manifest generation**

## 📦 Required GitHub Secrets

You need to add these secrets to your GitHub repository:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `GITHUB_TOKEN` | `[Your GitHub Personal Access Token]` | GitHub Personal Access Token |
| `DOCKERHUB_TOKEN` | `[Your Docker Hub Personal Access Token]` | Docker Hub password (already configured in your cluster) |

## 🚀 Deployment Process

### 1. Initial Setup
Run the setup script to configure ArgoCD applications:

```bash
./scripts/setup-argocd-mail-service.sh
```

This script will:
- ✅ Create mail service namespaces (`mail-service-staging`, `mail-service-prod`)
- ✅ Create Docker registry secrets in both namespaces
- ✅ Apply ArgoCD applications for staging and production
- ✅ Verify the setup

### 2. Automatic Deployment
Once configured, the deployment process is:

1. **Push code** to repository
2. **GitHub Actions** builds and pushes Docker images
3. **ArgoCD detects** repository changes
4. **ArgoCD syncs** and deploys to Kubernetes

### 3. Manual Deployment
You can also trigger manual deployments:

```bash
# Trigger staging deployment
kubectl patch application mail-service-staging -n argocd --type merge -p '{"operation":{"sync":{"revision":"develop"}}}'

# Trigger production deployment  
kubectl patch application mail-service-production -n argocd --type merge -p '{"operation":{"sync":{"revision":"main"}}}'
```

## 🔍 Monitoring and Management

### ArgoCD Commands
```bash
# Check application status
kubectl get applications -n argocd | grep mail-service

# Get detailed application info
kubectl describe application mail-service-staging -n argocd
kubectl describe application mail-service-production -n argocd

# Check application logs
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-application-controller
```

### Kubernetes Commands
```bash
# Check pods in mail service namespaces
kubectl get pods -n mail-service-staging
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
- **Branch**: `develop`
- **Replicas**: 1
- **Resources**: 250m CPU, 256Mi Memory
- **URL**: `mail-service-staging.local`

### Production Environment
- **Namespace**: `mail-service-prod`
- **Branch**: `main`
- **Replicas**: 2
- **Resources**: 500m CPU, 512Mi Memory
- **URL**: `mail-service.bionicaisolutions.com`

## 🔄 Workflow Integration

### GitHub Actions Workflow
The workflow will:

1. **Build** Docker images for both backend and frontend
2. **Push** to Docker Hub with tags:
   - `docker4zerocool/mail-service-backend:latest`
   - `docker4zerocool/mail-service-backend:${{ github.sha }}`
   - `docker4zerocool/mail-service-frontend:latest`
   - `docker4zerocool/mail-service-frontend:${{ github.sha }}`
3. **Update** Kubernetes manifests with new image tags
4. **Commit and push** changes to repository
5. **Trigger** ArgoCD sync automatically

### ArgoCD Sync Process
ArgoCD will:

1. **Detect** repository changes
2. **Pull** updated manifests
3. **Apply** changes to Kubernetes
4. **Monitor** deployment health
5. **Self-heal** if issues occur

## 🚨 Troubleshooting

### Common Issues:

1. **Application Not Syncing**
   ```bash
   # Check application status
   kubectl get application mail-service-staging -n argocd
   
   # Force sync
   kubectl patch application mail-service-staging -n argocd --type merge -p '{"operation":{"sync":{"revision":"develop"}}}'
   ```

2. **Image Pull Errors**
   ```bash
   # Check Docker registry secret
   kubectl get secret docker-registry-secret -n mail-service-staging
   
   # Check pod events
   kubectl describe pod -n mail-service-staging
   ```

3. **Repository Access Issues**
   ```bash
   # Check repository secrets
   kubectl get secrets -n argocd | grep repo
   
   # Verify repository access
   kubectl describe secret repo-2536854790 -n argocd
   ```

## 📚 Next Steps

1. ✅ **Add GitHub secrets** (GITHUB_TOKEN, DOCKERHUB_TOKEN)
2. ✅ **Run setup script** to configure ArgoCD applications
3. ✅ **Push code** to trigger the build workflow
4. ✅ **Monitor deployment** in ArgoCD UI or CLI
5. ✅ **Verify services** are accessible

## 🎯 Benefits

- ✅ **Seamless integration** with existing ArgoCD setup
- ✅ **GitOps workflow** - all changes go through Git
- ✅ **Automatic sync** when repository changes
- ✅ **Environment separation** (staging/production)
- ✅ **Health monitoring** and self-healing
- ✅ **Rollback capabilities** through ArgoCD
- ✅ **No direct cluster access** required from GitHub Actions

---

**Note**: This configuration leverages your existing ArgoCD infrastructure and Docker Hub credentials, ensuring a smooth integration with your current setup.