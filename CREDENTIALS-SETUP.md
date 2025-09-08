# 🔑 Credentials Setup Guide

This guide will help you configure the GitHub Actions workflows with the required credentials.

## 📋 Required Credentials

### GitHub Credentials:
- **Username**: Your GitHub username
- **Access Token**: Your GitHub Personal Access Token

### Docker Hub Credentials:
- **Username**: `docker4zerocool`
- **Token**: Your Docker Hub Personal Access Token

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)

If you have GitHub CLI installed:

```bash
# Run the setup script
./scripts/setup-github-secrets.sh
```

### Option 2: Manual Setup

1. **Go to your GitHub repository**
2. **Navigate to Settings** → **Secrets and variables** → **Actions**
3. **Add the following secrets:**

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `GITHUB_TOKEN` | `[Your GitHub Personal Access Token]` | GitHub Personal Access Token |
| `DOCKERHUB_USERNAME` | `docker4zerocool` | Docker Hub username |
| `DOCKERHUB_TOKEN` | `[Your Docker Hub Personal Access Token]` | Docker Hub Personal Access Token |

## 🔧 Configuration Details

### GitHub Container Registry
- **Registry**: `ghcr.io`
- **Username**: Your GitHub username
- **Token**: Your GitHub Personal Access Token

### Docker Hub
- **Registry**: `docker.io`
- **Username**: `docker4zerocool`
- **Token**: Your Docker Hub Personal Access Token

## 📦 Image Locations

After setup, your images will be available at:

### GitHub Container Registry:
- `ghcr.io/[your-username]/mail-service/backend:latest`
- `ghcr.io/[your-username]/mail-service/frontend:latest`

### Docker Hub:
- `docker4zerocool/mail-service-backend:latest`
- `docker4zerocool/mail-service-frontend:latest`

## 🏗️ Workflow Configuration

The GitHub Actions workflows are configured to:

1. **Build and push** to both registries
2. **Use Docker Hub** as the primary registry for Kubernetes deployments
3. **Support both** GitHub Container Registry and Docker Hub

### Build Workflow Features:
- ✅ Multi-architecture builds (AMD64/ARM64)
- ✅ Pushes to both GitHub Container Registry and Docker Hub
- ✅ Automatic tagging with commit SHA and latest
- ✅ Build caching for faster builds

## 🚀 Deployment Process

### Automatic Deployment via ArgoCD:
1. **Push to `main`** → Production deployment via ArgoCD
2. **Push to `develop`** → Staging deployment via ArgoCD
3. **ArgoCD automatically syncs** when repository changes

### Manual Deployment:
1. Go to **Actions** tab
2. Select **"Deploy to Kubernetes via ArgoCD"** workflow
3. Click **"Run workflow"**
4. Choose environment and image tag
5. ArgoCD will handle the actual deployment

## 🔍 Verification

### Check if secrets are set:
```bash
# Using GitHub CLI
gh secret list --repo your-username/mail-service
```

### Test Docker Hub access:
```bash
# Login to Docker Hub
echo "[Your Docker Hub Token]" | docker login --username docker4zerocool --password-stdin

# Test pull
docker pull docker4zerocool/mail-service-backend:latest
```

### Test GitHub Container Registry:
```bash
# Login to GitHub Container Registry
echo "[Your GitHub Personal Access Token]" | docker login ghcr.io --username [your-username] --password-stdin

# Test pull
docker pull ghcr.io/[your-username]/mail-service/backend:latest
```

## 🚨 Troubleshooting

### Common Issues:

1. **Authentication Failed**
   - Verify token permissions
   - Check if tokens are not expired
   - Ensure correct username/email

2. **Image Pull Errors**
   - Verify registry credentials
   - Check if images exist in registry
   - Ensure proper image names

3. **Kubernetes Deployment Issues**
   - Verify ArgoCD application status
   - Check cluster connectivity
   - Ensure proper RBAC permissions

### Debug Commands:

```bash
# Check GitHub secrets
gh secret list --repo your-username/mail-service

# Test Docker Hub login
docker login --username docker4zerocool

# Test GitHub Container Registry login
docker login ghcr.io --username [your-username]

# Check ArgoCD applications
kubectl get applications -n argocd | grep mail-service
```

## 🔒 Security Notes

- **Tokens are sensitive**: Never commit them to code
- **Use GitHub Secrets**: Store credentials securely
- **Rotate regularly**: Update tokens periodically
- **Minimal permissions**: Use tokens with least required access

## 📚 Next Steps

1. ✅ **Set up secrets** using the guide above
2. ✅ **Push code** to trigger the build workflow
3. ✅ **Deploy to Kubernetes** via ArgoCD
4. ✅ **Monitor deployment** using ArgoCD UI or CLI
5. ✅ **Set up ArgoCD applications** using the provided manifests

## 🆘 Support

If you encounter issues:

1. Check the [troubleshooting section](#-troubleshooting)
2. Review GitHub Actions logs
3. Verify credentials and permissions
4. Check ArgoCD application status

---

**Note**: The credentials provided are now configured in the GitHub Actions workflows. The system will automatically build and push images to both GitHub Container Registry and Docker Hub, with Docker Hub being used as the primary registry for Kubernetes deployments.