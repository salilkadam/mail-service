#!/bin/bash

# GitHub Secrets Setup Script
# This script helps you set up the required secrets for GitHub Actions

set -e

echo "🔑 GitHub Secrets Setup for Mail Service"
echo "========================================"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    echo "Please install it from: https://cli.github.com/"
    echo "Or manually add the secrets in GitHub repository settings."
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub CLI."
    echo "Please run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI is installed and authenticated"
echo ""

# Get repository information
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo "📦 Repository: $REPO"
echo ""

# Function to add secret
add_secret() {
    local secret_name=$1
    local secret_value=$2
    local description=$3
    
    echo "🔐 Adding secret: $secret_name"
    echo "$secret_value" | gh secret set "$secret_name" --repo "$REPO"
    echo "✅ Added: $secret_name - $description"
    echo ""
}

# Add GitHub Container Registry token
echo "Adding GitHub Container Registry token..."
add_secret "GITHUB_TOKEN" "[Your GitHub Personal Access Token]" "GitHub Personal Access Token for container registry"

# Add Docker Hub credentials
echo "Adding Docker Hub credentials..."
add_secret "DOCKERHUB_USERNAME" "docker4zerocool" "Docker Hub username"
add_secret "DOCKERHUB_TOKEN" "[Your Docker Hub Personal Access Token]" "Docker Hub Personal Access Token"

# Kubernetes configuration
echo "⚠️  Kubernetes Configuration Required"
echo "You need to provide your Kubernetes cluster configuration."
echo ""
echo "To get your kubeconfig:"
echo "1. kubectl config view --raw"
echo "2. Base64 encode the output: kubectl config view --raw | base64 -w 0"
echo "3. Add the base64 encoded string as KUBE_CONFIG secret"
echo ""

read -p "Do you want to add KUBE_CONFIG now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Please paste your base64 encoded kubeconfig:"
    read -r kube_config
    add_secret "KUBE_CONFIG" "$kube_config" "Base64 encoded Kubernetes configuration"
fi

echo "🎉 GitHub secrets setup completed!"
echo ""
echo "📋 Summary of added secrets:"
echo "- GITHUB_TOKEN: GitHub Personal Access Token"
echo "- DOCKERHUB_USERNAME: Docker Hub username"
echo "- DOCKERHUB_TOKEN: Docker Hub Personal Access Token"
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "- KUBE_CONFIG: Kubernetes cluster configuration"
fi
echo ""
echo "🚀 You can now trigger the GitHub Actions workflows!"
echo "   - Push to 'main' branch for production deployment"
echo "   - Push to 'develop' branch for staging deployment"
echo "   - Use manual workflow dispatch for custom deployments"