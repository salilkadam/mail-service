#!/bin/bash

# Email Server Deployment Script
# This script deploys the complete email server infrastructure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="email-server-prod"
RELEASE_NAME="email-server"
CHART_PATH="./helm/email-server"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi
    
    # Check if helm is installed
    if ! command -v helm &> /dev/null; then
        log_error "Helm is not installed. Please install Helm first."
        exit 1
    fi
    
    # Check if we can connect to Kubernetes cluster
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster. Please check your kubeconfig."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

deploy_email_server() {
    log_info "Deploying email server infrastructure..."
    
    # Create namespace if it doesn't exist
    if ! kubectl get namespace $NAMESPACE &> /dev/null; then
        log_info "Creating namespace: $NAMESPACE"
        kubectl create namespace $NAMESPACE
    else
        log_info "Namespace $NAMESPACE already exists"
    fi
    
    # Deploy with Helm
    log_info "Deploying email server with Helm..."
    helm upgrade --install $RELEASE_NAME $CHART_PATH \
        --namespace $NAMESPACE \
        --create-namespace \
        --wait \
        --timeout=10m
    
    log_success "Email server deployed successfully"
}

verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check if pods are running
    log_info "Checking pod status..."
    kubectl get pods -n $NAMESPACE
    
    # Wait for pods to be ready
    log_info "Waiting for pods to be ready..."
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=postfix-relay -n $NAMESPACE --timeout=300s
    
    # Check services
    log_info "Checking services..."
    kubectl get svc -n $NAMESPACE
    
    # Check network policies
    log_info "Checking network policies..."
    kubectl get networkpolicy -n $NAMESPACE
    
    log_success "Deployment verification completed"
}

configure_namespace_access() {
    local target_namespace=$1
    
    if [ -z "$target_namespace" ]; then
        log_warning "No target namespace specified for SMTP access configuration"
        return
    fi
    
    log_info "Configuring SMTP access for namespace: $target_namespace"
    
    # Check if namespace exists
    if ! kubectl get namespace $target_namespace &> /dev/null; then
        log_error "Namespace $target_namespace does not exist"
        return
    fi
    
    # Add label for SMTP access
    kubectl label namespace $target_namespace email-server.kubernetes.io/smtp-access=true --overwrite
    
    log_success "SMTP access configured for namespace: $target_namespace"
}

test_email_server() {
    log_info "Testing email server connectivity..."
    
    # Get a pod name
    local pod_name=$(kubectl get pods -n $NAMESPACE -l app.kubernetes.io/name=postfix-relay -o jsonpath='{.items[0].metadata.name}')
    
    if [ -z "$pod_name" ]; then
        log_error "No Postfix relay pods found"
        return 1
    fi
    
    # Test SMTP connection
    log_info "Testing SMTP connection to Gmail relay..."
    kubectl exec -n $NAMESPACE $pod_name -- telnet smtp-relay.gmail.com 587 <<< "quit" || {
        log_warning "SMTP connection test failed (this might be expected in some environments)"
    }
    
    log_success "Email server connectivity test completed"
}

show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help              Show this help message"
    echo "  -n, --namespace NAME    Target namespace for SMTP access (optional)"
    echo "  --test-only             Only run tests, don't deploy"
    echo "  --verify-only           Only verify existing deployment"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Deploy email server"
    echo "  $0 -n mail-service-prod              # Deploy and configure access for mail-service-prod"
    echo "  $0 --test-only                       # Only test existing deployment"
    echo "  $0 --verify-only                     # Only verify existing deployment"
}

main() {
    local target_namespace=""
    local test_only=false
    local verify_only=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -n|--namespace)
                target_namespace="$2"
                shift 2
                ;;
            --test-only)
                test_only=true
                shift
                ;;
            --verify-only)
                verify_only=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    log_info "Starting email server deployment script..."
    
    if [ "$test_only" = true ]; then
        test_email_server
        exit 0
    fi
    
    if [ "$verify_only" = true ]; then
        verify_deployment
        exit 0
    fi
    
    # Full deployment
    check_prerequisites
    deploy_email_server
    verify_deployment
    
    if [ -n "$target_namespace" ]; then
        configure_namespace_access "$target_namespace"
    fi
    
    test_email_server
    
    log_success "Email server deployment completed successfully!"
    echo ""
    log_info "Next steps:"
    echo "1. Configure Gmail Workspace SMTP relay settings"
    echo "2. Add your server's IP address to Gmail Workspace whitelist"
    echo "3. Test email sending from your applications"
    echo ""
    log_info "Connection details:"
    echo "  Host: postfix-relay.$NAMESPACE.svc.cluster.local"
    echo "  Port: 25"
    echo "  Protocol: SMTP"
    echo "  Authentication: None (IP-based)"
    echo ""
    log_info "Documentation:"
    echo "  - Setup Guide: docs/EMAIL-SERVER-SETUP.md"
    echo "  - Usage Guide: docs/EMAIL-SERVER-USAGE.md"
    echo "  - API Reference: docs/EMAIL-SERVER-API.md"
}

# Run main function
main "$@"
