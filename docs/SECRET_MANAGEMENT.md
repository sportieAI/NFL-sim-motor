# Secret Management and Key Rotation Process

## Overview
This document outlines the secret management and key rotation procedures for the NFL-sim-motor production system.

## Secret Categories

### 1. Database Credentials
- **POSTGRES_PASSWORD**: Main database password
- **POSTGRES_READ_REPLICA_PASSWORD**: Read replica password  
- **REDIS_PASSWORD**: Redis instance password

### 2. Storage & Cloud Credentials
- **AWS_ACCESS_KEY_ID**: S3 storage access key
- **AWS_SECRET_ACCESS_KEY**: S3 storage secret key
- **AWS_KMS_KEY_ID**: Encryption key for S3 objects

### 3. Application Secrets
- **JWT_SECRET**: JWT token signing secret (minimum 256 bits)
- **API_KEY_MASTER**: Master API key for system-to-system auth

### 4. Monitoring & External Services
- **DATADOG_API_KEY**: Monitoring service API key
- **SLACK_WEBHOOK_URL**: Alert notification webhook

## Secret Storage Methods

### Development & Staging
- Environment variables in `.env` files (never committed)
- Docker secrets for containerized deployments
- Kubernetes secrets for K8s deployments

### Production
- **Primary**: HashiCorp Vault or AWS Secrets Manager
- **Backup**: Kubernetes secrets (for K8s deployments)
- **Emergency**: Encrypted configuration files with restricted access

## Key Rotation Schedule

### High-Risk Secrets (Rotate Monthly)
- JWT_SECRET
- API_KEY_MASTER
- POSTGRES_PASSWORD

### Medium-Risk Secrets (Rotate Quarterly)
- AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY
- REDIS_PASSWORD
- External service API keys

### Low-Risk Secrets (Rotate Bi-Annually)
- Monitoring service keys
- Non-critical integration credentials

## Rotation Procedure

### 1. Pre-Rotation Checklist
- [ ] Verify backup systems are operational
- [ ] Notify team of scheduled rotation
- [ ] Ensure rollback procedures are documented
- [ ] Test new credentials in staging environment

### 2. Rotation Steps
1. **Generate new credentials** in the target system
2. **Update secrets in vault/secrets manager**
3. **Deploy new configuration** to staging first
4. **Validate staging functionality** with new credentials
5. **Deploy to production** using blue-green deployment
6. **Verify production functionality**
7. **Revoke old credentials** after validation period

### 3. Post-Rotation Verification
- [ ] All services are operational
- [ ] Authentication is working correctly
- [ ] No alerts or errors in monitoring
- [ ] Database connections are stable
- [ ] External integrations are functional

## Emergency Procedures

### Credential Compromise
1. **Immediate**: Revoke compromised credentials
2. **Generate**: New credentials immediately
3. **Deploy**: Emergency deployment with new credentials
4. **Monitor**: Enhanced monitoring for 24-48 hours
5. **Document**: Incident report and lessons learned

### Service Outage Due to Credential Issues
1. **Rollback**: To previous working configuration if possible
2. **Emergency Access**: Use break-glass procedures
3. **Fix**: Correct the credential configuration
4. **Validate**: Full system functionality
5. **Post-Mortem**: Root cause analysis

## Automation Scripts

### Rotation Automation
```bash
# Example rotation script for JWT secret
./scripts/rotate-jwt-secret.sh --environment production --validate
```

### Validation Scripts
```bash
# Verify all secrets are accessible
./scripts/validate-secrets.sh --environment production
```

## Monitoring & Alerting

### Secret Expiry Alerts
- 30 days before expiration: Warning alert
- 7 days before expiration: Critical alert
- Day of expiration: Emergency alert

### Failed Authentication Monitoring
- Monitor failed database connections
- Track API authentication failures
- Alert on unusual access patterns

## Compliance & Audit

### Audit Trail Requirements
- All secret access must be logged
- Rotation activities must be documented
- Access reviews conducted quarterly
- Compliance reports generated monthly

### Access Control
- Secrets accessible only to authorized personnel
- Role-based access to different secret categories
- Multi-factor authentication required for access
- Regular access reviews and cleanup

## Tools & Resources

### Recommended Tools
- **HashiCorp Vault**: Enterprise secret management
- **AWS Secrets Manager**: Cloud-native secret storage
- **Kubernetes Secrets**: Container orchestration secrets
- **Bitwarden/1Password**: Team password management

### Validation Tools
- TruffleHog: Scan for committed secrets
- GitLeaks: Prevent secret commits
- Custom scripts: Environment-specific validation

---

**Last Updated**: 2025-09-19
**Review Schedule**: Monthly
**Owner**: DevOps Team
**Approver**: Security Team