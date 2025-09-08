#!/bin/bash

# Mail Service Kubernetes Deployment Script
# Usage: ./deploy.sh [staging|production] [image-tag]

set -e

NAMESPACE=${1:-staging}
IMAGE_TAG=${2:-latest}
REGISTRY=${REGISTRY:-ghcr.io}
REPOSITORY=${REPOSITORY:-your-username/mail-service}

# Validate namespace
if [[ "$NAMESPACE" != "staging" && "$NAMESPACE" != "production" ]]; then
    echo "Error: Namespace must be 'staging' or 'production'"
    exit 1
fi

# Set namespace suffix
if [[ "$NAMESPACE" == "production" ]]; then
    NAMESPACE_SUFFIX="prod"
else
    NAMESPACE_SUFFIX="staging"
fi

FULL_NAMESPACE="mail-service-$NAMESPACE_SUFFIX"

echo "🚀 Deploying Mail Service to $NAMESPACE environment"
echo "📦 Namespace: $FULL_NAMESPACE"
echo "🏷️  Image Tag: $IMAGE_TAG"
echo "📋 Registry: $REGISTRY/$REPOSITORY"

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed or not in PATH"
    exit 1
fi

# Check if cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot connect to Kubernetes cluster"
    exit 1
fi

echo "✅ Kubernetes cluster is accessible"

# Create namespace if it doesn't exist
echo "📁 Creating namespace..."
kubectl apply -f k8s/namespace-$NAMESPACE.yaml

# Update image tags in manifests
echo "🏷️  Updating image tags..."
cp k8s/backend-deployment.yaml k8s/backend-deployment-temp.yaml
cp k8s/frontend-deployment.yaml k8s/frontend-deployment-temp.yaml

# Update backend image
sed -i "s|image: mail-service-backend:latest|image: $REGISTRY/$REPOSITORY/backend:$IMAGE_TAG|g" k8s/backend-deployment-temp.yaml
sed -i "s|namespace: mail-service|namespace: $FULL_NAMESPACE|g" k8s/backend-deployment-temp.yaml

# Update frontend image
sed -i "s|image: mail-service-frontend:latest|image: $REGISTRY/$REPOSITORY/frontend:$IMAGE_TAG|g" k8s/frontend-deployment-temp.yaml
sed -i "s|namespace: mail-service|namespace: $FULL_NAMESPACE|g" k8s/frontend-deployment-temp.yaml

# Update other manifests
cp k8s/configmap.yaml k8s/configmap-temp.yaml
cp k8s/pvc.yaml k8s/pvc-temp.yaml
cp k8s/backend-service.yaml k8s/backend-service-temp.yaml
cp k8s/frontend-service.yaml k8s/frontend-service-temp.yaml
cp k8s/ingress.yaml k8s/ingress-temp.yaml

# Update namespaces in all manifests
for file in k8s/*-temp.yaml; do
    sed -i "s|namespace: mail-service|namespace: $FULL_NAMESPACE|g" "$file"
done

# Apply manifests
echo "📋 Applying Kubernetes manifests..."

# Apply in order
kubectl apply -f k8s/configmap-temp.yaml
kubectl apply -f k8s/pvc-temp.yaml
kubectl apply -f k8s/backend-deployment-temp.yaml
kubectl apply -f k8s/backend-service-temp.yaml
kubectl apply -f k8s/frontend-deployment-temp.yaml
kubectl apply -f k8s/frontend-service-temp.yaml
kubectl apply -f k8s/ingress-temp.yaml

# Wait for deployments
echo "⏳ Waiting for deployments to be ready..."
kubectl rollout status deployment/mail-service-backend -n $FULL_NAMESPACE --timeout=300s
kubectl rollout status deployment/mail-service-frontend -n $FULL_NAMESPACE --timeout=300s

# Clean up temporary files
rm -f k8s/*-temp.yaml

# Get service information
echo "📊 Deployment Status:"
kubectl get pods -n $FULL_NAMESPACE
kubectl get services -n $FULL_NAMESPACE
kubectl get ingress -n $FULL_NAMESPACE

# Health check
echo "🏥 Running health checks..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=mail-service-backend -n $FULL_NAMESPACE --timeout=300s
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=mail-service-frontend -n $FULL_NAMESPACE --timeout=300s

echo "✅ Deployment completed successfully!"
echo "🌐 Services are running in namespace: $FULL_NAMESPACE"

# Get ingress URL if available
INGRESS_URL=$(kubectl get ingress mail-service-ingress -n $FULL_NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "pending")
if [[ "$INGRESS_URL" != "pending" ]]; then
    echo "🌍 Application URL: https://$INGRESS_URL"
else
    echo "🌍 Ingress URL is pending. Check with: kubectl get ingress -n $FULL_NAMESPACE"
fi