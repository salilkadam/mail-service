#!/bin/bash
# Deployment script for the mail service

set -e

echo "🚀 Mail Service Deployment Script"
echo "=================================="

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed or not in PATH"
    exit 1
fi

# Check if helm is available
if ! command -v helm &> /dev/null; then
    echo "❌ helm is not installed or not in PATH"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Function to deploy kube-mail
deploy_kube_mail() {
    echo "📧 Deploying kube-mail..."
    
    # Add helm repository
    helm repo add mittwald https://helm.mittwald.de
    helm repo update
    
    # Install kube-mail
    helm install kube-mail mittwald/kube-mail --namespace kube-system --create-namespace
    
    echo "✅ kube-mail deployed successfully"
}

# Function to deploy mail service
deploy_mail_service() {
    echo "📦 Deploying mail service..."
    
    # Create namespace
    kubectl apply -f k8s/namespace.yaml
    
    # Apply configurations
    kubectl apply -f k8s/configmap.yaml
    kubectl apply -f k8s/pvc.yaml
    
    # Deploy backend
    kubectl apply -f k8s/backend-deployment.yaml
    kubectl apply -f k8s/backend-service.yaml
    
    # Deploy frontend
    kubectl apply -f k8s/frontend-deployment.yaml
    kubectl apply -f k8s/frontend-service.yaml
    
    # Apply ingress
    kubectl apply -f k8s/ingress.yaml
    
    echo "✅ Mail service deployed successfully"
}

# Function to configure kube-mail
configure_kube_mail() {
    echo "⚙️  Configuring kube-mail..."
    
    # Apply SMTP server configuration
    kubectl apply -f k8s/kube-mail-smtp-server.yaml
    
    # Apply email policy
    kubectl apply -f k8s/kube-mail-email-policy.yaml
    
    echo "✅ kube-mail configured successfully"
}

# Function to check deployment status
check_status() {
    echo "🔍 Checking deployment status..."
    
    # Check kube-mail
    echo "kube-mail pods:"
    kubectl get pods -n kube-system -l app.kubernetes.io/name=kube-mail
    
    # Check mail service
    echo "Mail service pods:"
    kubectl get pods -n mail-service
    
    # Check services
    echo "Services:"
    kubectl get services -n mail-service
    
    echo "✅ Status check completed"
}

# Main deployment logic
main() {
    local deploy_kube_mail_flag=false
    local deploy_service_flag=false
    local configure_flag=false
    local status_flag=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --kube-mail)
                deploy_kube_mail_flag=true
                shift
                ;;
            --service)
                deploy_service_flag=true
                shift
                ;;
            --configure)
                configure_flag=true
                shift
                ;;
            --status)
                status_flag=true
                shift
                ;;
            --all)
                deploy_kube_mail_flag=true
                deploy_service_flag=true
                configure_flag=true
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --kube-mail    Deploy kube-mail"
                echo "  --service      Deploy mail service"
                echo "  --configure    Configure kube-mail"
                echo "  --status       Check deployment status"
                echo "  --all          Deploy everything"
                echo "  -h, --help     Show this help message"
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                echo "Use -h or --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # If no flags specified, show help
    if [[ "$deploy_kube_mail_flag" == false && "$deploy_service_flag" == false && "$configure_flag" == false && "$status_flag" == false ]]; then
        echo "No deployment options specified."
        echo "Use -h or --help for usage information"
        exit 1
    fi
    
    # Execute requested operations
    if [[ "$deploy_kube_mail_flag" == true ]]; then
        deploy_kube_mail
    fi
    
    if [[ "$deploy_service_flag" == true ]]; then
        deploy_mail_service
    fi
    
    if [[ "$configure_flag" == true ]]; then
        configure_kube_mail
    fi
    
    if [[ "$status_flag" == true ]]; then
        check_status
    fi
    
    echo ""
    echo "🎉 Deployment completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Configure your SMTP server in k8s/kube-mail-smtp-server.yaml"
    echo "2. Update the ingress hostname in k8s/ingress.yaml"
    echo "3. Access the application at the configured hostname"
}

# Run main function
main "$@"
