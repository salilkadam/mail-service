# Email Server Setup Guide

## Overview

This document describes the setup and configuration of the Postfix SMTP relay server for the mail service infrastructure. The email server provides a reliable, scalable SMTP relay service that forwards emails through Gmail Workspace SMTP relay.

## Architecture

```
Application → Postfix SMTP Relay → Gmail Workspace (smtp-relay.gmail.com:587) → Recipients
```

## Components

### 1. Postfix SMTP Relay
- **Image**: `juanluisbaptiste/postfix:latest`
- **Port**: 25 (SMTP)
- **Namespace**: `email-server-prod`
- **Replicas**: 2 (for high availability)

### 2. Services
- **postfix-relay**: ClusterIP service for internal communication
- **postfix-relay-headless**: Headless service for direct pod access
- **postfix-relay-metrics**: Metrics service for monitoring

### 3. Network Policies
- **postfix-relay-network-policy**: Controls access to Postfix relay
- **email-server-egress-policy**: Controls outbound email traffic

## Prerequisites

### Gmail Workspace Configuration

1. **IP Whitelisting**:
   - Add your server's public IP address to Gmail Workspace SMTP Relay settings
   - Go to Google Admin Console → Apps → Google Workspace → Gmail → Advanced settings → SMTP relay service
   - Add your server's IP address to the allowed IPs list

2. **Domain Configuration**:
   - Ensure `bionicaisolutions.com` is properly configured in your Gmail Workspace
   - Verify the domain is verified and active

### Kubernetes Requirements

- Kubernetes cluster with CNI that supports NetworkPolicies
- Namespace with appropriate labels for network access
- Sufficient resources for Postfix containers

## Deployment

### Option 1: Using Kustomize (Recommended)

```bash
# Deploy the entire email server stack
kubectl apply -k k8s/email-server/

# Verify deployment
kubectl get pods -n email-server-prod
kubectl get svc -n email-server-prod
```

### Option 2: Individual Manifests

```bash
# Deploy in order
kubectl apply -f k8s/email-server/namespace.yaml
kubectl apply -f k8s/email-server/configmap.yaml
kubectl apply -f k8s/email-server/postfix-relay-deployment.yaml
kubectl apply -f k8s/email-server/postfix-relay-service.yaml
kubectl apply -f k8s/email-server/network-policy.yaml
kubectl apply -f k8s/email-server/monitoring.yaml
```

## Configuration

### Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `maildomain` | `bionicaisolutions.com` | Primary mail domain |
| `relayhost` | `[smtp-relay.gmail.com]:587` | Gmail SMTP relay host |
| `ALLOWED_SENDER_DOMAINS` | `bionicaisolutions.com,gmail.com` | Allowed sender domains |
| `SMTP_SERVER` | `smtp-relay.gmail.com` | SMTP server hostname |
| `SMTP_PORT` | `587` | SMTP server port |
| `SERVER_HOSTNAME` | `mail.bionicaisolutions.com` | Server hostname for HELO |

### Network Access

To allow applications to use the email server, add the following label to your namespace:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: your-app-namespace
  labels:
    email-server.kubernetes.io/smtp-access: "true"
```

## Monitoring

### Metrics

The email server exposes metrics on port 8080:

- **Queue size**: Number of messages in the queue
- **Bounce rate**: Rate of bounced messages
- **Delivery rate**: Rate of successfully delivered messages
- **Connection count**: Number of active SMTP connections

### Alerts

Configured alerts include:

- **PostfixRelayDown**: SMTP relay is not responding
- **PostfixRelayHighQueue**: Queue size exceeds 100 messages
- **PostfixRelayHighBounceRate**: Bounce rate exceeds 0.1 per second

### Logs

View Postfix logs:

```bash
kubectl logs -n email-server-prod deployment/postfix-relay
```

## Troubleshooting

### Common Issues

1. **Connection Refused**:
   - Check if the namespace has the correct label: `email-server.kubernetes.io/smtp-access: "true"`
   - Verify network policies are applied correctly

2. **Email Bounces**:
   - Verify IP address is whitelisted in Gmail Workspace
   - Check domain configuration in Gmail Workspace
   - Review Postfix logs for specific error messages

3. **High Queue Size**:
   - Check Gmail Workspace quota limits
   - Verify network connectivity to Gmail SMTP relay
   - Review Postfix configuration

### Debug Commands

```bash
# Check Postfix status
kubectl exec -n email-server-prod deployment/postfix-relay -- postqueue -p

# Test SMTP connection
kubectl exec -n email-server-prod deployment/postfix-relay -- telnet smtp-relay.gmail.com 587

# View Postfix configuration
kubectl exec -n email-server-prod deployment/postfix-relay -- postconf -n
```

## Security Considerations

1. **Network Policies**: Restrict access to authorized namespaces only
2. **Resource Limits**: Prevent resource exhaustion attacks
3. **Security Context**: Run containers as non-root user
4. **TLS**: All communication with Gmail SMTP relay uses TLS
5. **Rate Limiting**: Postfix includes built-in rate limiting

## Scaling

### Horizontal Scaling

The Postfix relay is designed to scale horizontally:

```bash
# Scale to 3 replicas
kubectl scale deployment postfix-relay -n email-server-prod --replicas=3
```

### Vertical Scaling

Adjust resource limits in the deployment manifest:

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "200m"
  limits:
    memory: "512Mi"
    cpu: "400m"
```

## Maintenance

### Updates

1. Update the Postfix image tag in the deployment
2. Apply the updated manifest
3. Monitor the rolling update process

### Backup

Postfix queue data is ephemeral and doesn't require backup. Configuration is stored in ConfigMaps and can be backed up using standard Kubernetes backup procedures.

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review Postfix logs for error messages
3. Verify Gmail Workspace configuration
4. Check network connectivity and policies
