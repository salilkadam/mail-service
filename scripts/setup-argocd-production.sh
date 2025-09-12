#!/bin/bash

# ArgoCD Mail Service Production Setup Script
set -e

echo "🚀 ArgoCD Mail Service Production Setup"
echo "======================================"
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

# Create production namespace
echo "🏗️  Creating mail service production namespace..."
kubectl create namespace mail-service-prod --dry-run=client -o yaml | kubectl apply -f -
echo "✅ Created namespace: mail-service-prod"
echo ""

# Create Docker registry secret
echo "🔐 Creating Docker registry secret..."
kubectl create secret docker-registry docker-registry-secret \
    --docker-server=docker.io \
    --docker-username=docker4zerocool \
    --docker-password='Sw@pn@S@1i1K@d@m' \
    --docker-email='Salil.Kadam@Gmail.com' \
    --namespace=mail-service-prod \
    --dry-run=client -o yaml | kubectl apply -f -
echo "✅ Created Docker registry secret in mail-service-prod"
echo ""

# Apply ArgoCD application
echo "📋 Applying ArgoCD application..."
kubectl apply -f argocd/mail-service-production.yaml
echo "✅ Applied ArgoCD application: mail-service-production"
echo ""

# Wait for application to be created
echo "⏳ Waiting for ArgoCD application to be created..."
sleep 5

# Check application status
echo "📊 ArgoCD Application Status:"
echo ""

# Check production application
PROD_STATUS=$(kubectl get application mail-service-production -n argocd -o jsonpath='{.status.sync.status}' 2>/dev/null || echo "Not Found")
PROD_HEALTH=$(kubectl get application mail-service-production -n argocd -o jsonpath='{.status.health.status}' 2>/dev/null || echo "Unknown")

echo "Production Application:"
echo "  - Sync Status: $PROD_STATUS"
echo "  - Health Status: $PROD_HEALTH"
echo ""

# Display next steps
echo "🎉 ArgoCD Mail Service Production Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Push your code to the repository:"
echo "   git add ."
echo "   git commit -m 'Configure mail service for ArgoCD production'"
echo "   git push origin main"
echo ""
echo "2. Monitor deployment:"
echo "   kubectl get applications -n argocd | grep mail-service"
echo ""
echo "3. Check application logs:"
echo "   kubectl logs -n argocd -l app.kubernetes.io/name=argocd-application-controller"
echo ""
echo "4. Access ArgoCD UI:"
echo "   kubectl port-forward -n argocd svc/argocd-server 8080:443"
echo "   Then visit https://localhost:8080"
echo ""
echo "🔍 Useful Commands:"
echo "  # Check application status"
echo "  kubectl get application mail-service-production -n argocd"
echo ""
echo "  # Check pods in production namespace"
echo "  kubectl get pods -n mail-service-prod"
echo ""
echo "  # Check services"
echo "  kubectl get services -n mail-service-prod"
echo ""
echo "  # Check ingress"
echo "  kubectl get ingress -n mail-service-prod"
echo ""
echo "✅ Setup completed successfully!"
