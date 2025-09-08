#!/bin/bash

# ArgoCD Mail Service Setup Script
# This script sets up the mail service for your existing ArgoCD installation

set -e

echo "🚀 ArgoCD Mail Service Setup"
echo "============================"
echo ""

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed or not in PATH"
    exit 1
fi

# Check if we can connect to the cluster
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot connect to Kubernetes cluster"
    exit 1
fi

echo "✅ Connected to Kubernetes cluster"
echo ""

# Get current context
CONTEXT=$(kubectl config current-context)
echo "📦 Current context: $CONTEXT"
echo ""

# Check if ArgoCD namespace exists
if ! kubectl get namespace argocd &> /dev/null; then
    echo "❌ ArgoCD namespace not found. Please install ArgoCD first."
    exit 1
fi

echo "✅ ArgoCD namespace found"
echo ""

# Create mail service namespaces
echo "🏗️  Creating mail service namespaces..."

# Create staging namespace
kubectl create namespace mail-service-staging --dry-run=client -o yaml | kubectl apply -f -
echo "✅ Created namespace: mail-service-staging"

# Create production namespace  
kubectl create namespace mail-service-prod --dry-run=client -o yaml | kubectl apply -f -
echo "✅ Created namespace: mail-service-prod"

echo ""

# Create Docker registry secrets in both namespaces
echo "🔐 Creating Docker registry secrets..."

# Create secret for staging
kubectl create secret docker-registry docker-registry-secret \
    --docker-server=docker.io \
    --docker-username=docker4zerocool \
    --docker-password='Sw@pn@S@1i1K@d@m' \
    --docker-email='Salil.Kadam@Gmail.com' \
    --namespace=mail-service-staging \
    --dry-run=client -o yaml | kubectl apply -f -

echo "✅ Created Docker registry secret in mail-service-staging"

# Create secret for production
kubectl create secret docker-registry docker-registry-secret \
    --docker-server=docker.io \
    --docker-username=docker4zerocool \
    --docker-password='Sw@pn@S@1i1K@d@m' \
    --docker-email='Salil.Kadam@Gmail.com' \
    --namespace=mail-service-prod \
    --dry-run=client -o yaml | kubectl apply -f -

echo "✅ Created Docker registry secret in mail-service-prod"

echo ""

# Apply ArgoCD applications
echo "📋 Applying ArgoCD applications..."

# Apply staging application
kubectl apply -f argocd/mail-service-staging.yaml
echo "✅ Applied ArgoCD application: mail-service-staging"

# Apply production application
kubectl apply -f argocd/mail-service-production.yaml
echo "✅ Applied ArgoCD application: mail-service-production"

echo ""

# Wait for applications to be created
echo "⏳ Waiting for ArgoCD applications to be created..."
sleep 5

# Check application status
echo "📊 ArgoCD Application Status:"
echo ""

# Check staging application
STAGING_STATUS=$(kubectl get application mail-service-staging -n argocd -o jsonpath='{.status.sync.status}' 2>/dev/null || echo "Not Found")
STAGING_HEALTH=$(kubectl get application mail-service-staging -n argocd -o jsonpath='{.status.health.status}' 2>/dev/null || echo "Unknown")

echo "Staging Application:"
echo "  - Sync Status: $STAGING_STATUS"
echo "  - Health Status: $STAGING_HEALTH"

# Check production application
PROD_STATUS=$(kubectl get application mail-service-production -n argocd -o jsonpath='{.status.sync.status}' 2>/dev/null || echo "Not Found")
PROD_HEALTH=$(kubectl get application mail-service-production -n argocd -o jsonpath='{.status.health.status}' 2>/dev/null || echo "Unknown")

echo "Production Application:"
echo "  - Sync Status: $PROD_STATUS"
echo "  - Health Status: $PROD_HEALTH"

echo ""

# Display next steps
echo "🎉 ArgoCD Mail Service Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Push your code to the repository:"
echo "   git add ."
echo "   git commit -m 'Configure mail service for ArgoCD'"
echo "   git push origin main"
echo ""
echo "2. Monitor deployment in ArgoCD UI or CLI:"
echo "   kubectl get applications -n argocd | grep mail-service"
echo ""
echo "3. Check application logs:"
echo "   kubectl logs -n argocd -l app.kubernetes.io/name=argocd-application-controller"
echo ""
echo "4. Access ArgoCD UI (if available):"
echo "   kubectl port-forward -n argocd svc/argocd-server 8080:443"
echo "   # Then visit https://localhost:8080"
echo ""
echo "🔍 Useful Commands:"
echo "  # Check all ArgoCD applications"
echo "  kubectl get applications -n argocd"
echo ""
echo "  # Check mail service applications specifically"
echo "  kubectl get applications -n argocd | grep mail-service"
echo ""
echo "  # Get detailed application info"
echo "  kubectl describe application mail-service-staging -n argocd"
echo "  kubectl describe application mail-service-production -n argocd"
echo ""
echo "  # Check pods in mail service namespaces"
echo "  kubectl get pods -n mail-service-staging"
echo "  kubectl get pods -n mail-service-prod"
echo ""
echo "✅ Setup completed successfully!"
