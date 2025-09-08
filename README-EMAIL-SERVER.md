# Email Server Infrastructure

A production-ready Postfix SMTP relay service for Kubernetes, designed to provide reliable email delivery through Gmail Workspace SMTP relay.

## 🚀 Quick Start

### Prerequisites

1. **Gmail Workspace Configuration**:
   - IP address whitelisted in Gmail Workspace SMTP Relay settings
   - Domain `bionicaisolutions.com` configured and verified

2. **Kubernetes Requirements**:
   - Kubernetes cluster with CNI supporting NetworkPolicies
   - Helm 3.x installed
   - Sufficient resources for Postfix containers

### Deploy with Helm

```bash
# Add the chart repository (if using a chart repository)
helm repo add email-server ./helm/email-server

# Deploy the email server
helm install email-server ./helm/email-server \
  --namespace email-server-prod \
  --create-namespace \
  --set env.maildomain=bionicaisolutions.com \
  --set env.relayhost="[smtp-relay.gmail.com]:587"
```

### Deploy with Kustomize

```bash
# Deploy the entire email server stack
kubectl apply -k k8s/email-server/

# Verify deployment
kubectl get pods -n email-server-prod
kubectl get svc -n email-server-prod
```

## 📋 Table of Contents

- [Architecture](#architecture)
- [Components](#components)
- [Configuration](#configuration)
- [Usage](#usage)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Security](#security)
- [Scaling](#scaling)
- [Maintenance](#maintenance)

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   Application   │───▶│  Postfix SMTP    │───▶│  Gmail Workspace    │
│   (Your App)    │    │     Relay        │    │  SMTP Relay         │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   Recipients     │
                       │   (Gmail, etc.)  │
                       └──────────────────┘
```

### Key Features

- **High Availability**: Multiple replicas with rolling updates
- **Security**: Network policies and security contexts
- **Monitoring**: Prometheus metrics and alerting
- **Scalability**: Horizontal Pod Autoscaler support
- **Reliability**: Health checks and restart policies

## 🔧 Components

### Core Components

| Component | Description | Port |
|-----------|-------------|------|
| **Postfix Relay** | SMTP relay service | 25 |
| **Service** | ClusterIP service for internal access | 25 |
| **Headless Service** | Direct pod access | 25 |
| **Network Policy** | Traffic control and security | - |
| **ConfigMap** | Postfix configuration | - |

### Optional Components

| Component | Description | When Enabled |
|-----------|-------------|--------------|
| **ServiceMonitor** | Prometheus metrics collection | `monitoring.serviceMonitor.enabled=true` |
| **PrometheusRule** | Alerting rules | `monitoring.prometheusRule.enabled=true` |
| **HPA** | Horizontal Pod Autoscaler | `autoscaling.enabled=true` |
| **PDB** | Pod Disruption Budget | `podDisruptionBudget.enabled=true` |

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `maildomain` | `bionicaisolutions.com` | Primary mail domain |
| `relayhost` | `[smtp-relay.gmail.com]:587` | Gmail SMTP relay host |
| `ALLOWED_SENDER_DOMAINS` | `bionicaisolutions.com,gmail.com` | Allowed sender domains |
| `SMTP_SERVER` | `smtp-relay.gmail.com` | SMTP server hostname |
| `SMTP_PORT` | `587` | SMTP server port |
| `SERVER_HOSTNAME` | `mail.bionicaisolutions.com` | Server hostname for HELO |

### Helm Values

Key configuration options in `values.yaml`:

```yaml
# Deployment configuration
deployment:
  replicas: 2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1

# Resource limits
resources:
  limits:
    cpu: 200m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi

# Network policy
networkPolicy:
  enabled: true
  ingress:
    enabled: true
    from:
      - namespaceSelector:
          matchLabels:
            email-server.kubernetes.io/smtp-access: "true"

# Monitoring
monitoring:
  enabled: true
  serviceMonitor:
    enabled: true
    interval: 30s
    path: /metrics
```

## 📖 Usage

### For Applications

1. **Add namespace label**:
   ```yaml
   apiVersion: v1
   kind: Namespace
   metadata:
     name: your-app-namespace
     labels:
       email-server.kubernetes.io/smtp-access: "true"
   ```

2. **Connect to email server**:
   - **Host**: `postfix-relay.email-server-prod.svc.cluster.local`
   - **Port**: `25`
   - **Protocol**: `SMTP`
   - **Authentication**: None (IP-based)

3. **Send emails**:
   ```python
   import smtplib
   from email.mime.text import MIMEText
   
   def send_email(to, subject, body):
       server = smtplib.SMTP('postfix-relay.email-server-prod.svc.cluster.local', 25)
       msg = MIMEText(body)
       msg['Subject'] = subject
       msg['From'] = 'info@bionicaisolutions.com'
       msg['To'] = to
       server.send_message(msg)
       server.quit()
   ```

### For Developers

See the comprehensive usage guide: [EMAIL-SERVER-USAGE.md](docs/EMAIL-SERVER-USAGE.md)

### For API Integration

See the API reference: [EMAIL-SERVER-API.md](docs/EMAIL-SERVER-API.md)

## 📊 Monitoring

### Metrics

The email server exposes Prometheus metrics:

- **Queue size**: Number of messages in the queue
- **Bounce rate**: Rate of bounced messages
- **Delivery rate**: Rate of successfully delivered messages
- **Connection count**: Number of active SMTP connections

### Alerts

Pre-configured alerts include:

- **PostfixRelayDown**: SMTP relay is not responding
- **PostfixRelayHighQueue**: Queue size exceeds 100 messages
- **PostfixRelayHighBounceRate**: Bounce rate exceeds 0.1 per second

### Logs

View Postfix logs:

```bash
kubectl logs -n email-server-prod deployment/postfix-relay
```

## 🔍 Troubleshooting

### Common Issues

1. **Connection Refused**:
   ```bash
   # Check namespace label
   kubectl get namespace your-app-namespace -o yaml | grep smtp-access
   
   # Check network policies
   kubectl get networkpolicy -n email-server-prod
   ```

2. **Email Bounces**:
   ```bash
   # Check Postfix logs
   kubectl logs -n email-server-prod deployment/postfix-relay | grep "550"
   
   # Verify Gmail configuration
   kubectl exec -n email-server-prod deployment/postfix-relay -- telnet smtp-relay.gmail.com 587
   ```

3. **High Queue Size**:
   ```bash
   # Check queue status
   kubectl exec -n email-server-prod deployment/postfix-relay -- postqueue -p
   
   # Check metrics
   kubectl port-forward -n email-server-prod svc/postfix-relay-metrics 8080:8080
   curl http://localhost:8080/metrics
   ```

### Debug Commands

```bash
# Test SMTP connection
kubectl exec -n email-server-prod deployment/postfix-relay -- telnet smtp-relay.gmail.com 587

# Check Postfix configuration
kubectl exec -n email-server-prod deployment/postfix-relay -- postconf -n

# View service endpoints
kubectl get endpoints -n email-server-prod postfix-relay

# Check pod status
kubectl describe pod -n email-server-prod -l app.kubernetes.io/name=postfix-relay
```

## 🔒 Security

### Network Security

- **Network Policies**: Restrict access to authorized namespaces only
- **Security Contexts**: Run containers as non-root user
- **Resource Limits**: Prevent resource exhaustion attacks

### Email Security

- **TLS**: All communication with Gmail SMTP relay uses TLS
- **Rate Limiting**: Postfix includes built-in rate limiting
- **Input Validation**: Validate email addresses and content

### Best Practices

1. **Namespace Isolation**: Use network policies to restrict access
2. **Resource Limits**: Set appropriate CPU and memory limits
3. **Monitoring**: Monitor for unusual patterns or abuse
4. **Logging**: Log all email sending attempts for audit purposes

## 📈 Scaling

### Horizontal Scaling

```bash
# Scale to 3 replicas
kubectl scale deployment postfix-relay -n email-server-prod --replicas=3

# Or use Helm
helm upgrade email-server ./helm/email-server \
  --set deployment.replicas=3
```

### Vertical Scaling

```bash
# Update resource limits
helm upgrade email-server ./helm/email-server \
  --set resources.limits.cpu=400m \
  --set resources.limits.memory=512Mi
```

### Autoscaling

```bash
# Enable HPA
helm upgrade email-server ./helm/email-server \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=2 \
  --set autoscaling.maxReplicas=10
```

## 🔧 Maintenance

### Updates

1. **Update Postfix image**:
   ```bash
   helm upgrade email-server ./helm/email-server \
     --set image.tag=latest
   ```

2. **Update configuration**:
   ```bash
   helm upgrade email-server ./helm/email-server \
     --set env.maildomain=newdomain.com
   ```

### Backup

Postfix queue data is ephemeral and doesn't require backup. Configuration is stored in ConfigMaps and can be backed up using standard Kubernetes backup procedures.

### Health Checks

```bash
# Check pod health
kubectl get pods -n email-server-prod -l app.kubernetes.io/name=postfix-relay

# Check service health
kubectl get svc -n email-server-prod postfix-relay

# Check network policies
kubectl get networkpolicy -n email-server-prod
```

## 📚 Documentation

- [Email Server Setup Guide](docs/EMAIL-SERVER-SETUP.md) - Detailed setup instructions
- [Email Server Usage Guide](docs/EMAIL-SERVER-USAGE.md) - How to use the email server
- [Email Server API Reference](docs/EMAIL-SERVER-API.md) - Complete API documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the documentation
3. Check email server logs
4. Verify Gmail Workspace configuration
5. Contact the infrastructure team

## 🏷️ Version History

- **v1.0.0**: Initial release with Postfix SMTP relay
- **v1.0.1**: Added monitoring and alerting
- **v1.0.2**: Improved security and network policies
- **v1.0.3**: Added Helm chart and autoscaling support
