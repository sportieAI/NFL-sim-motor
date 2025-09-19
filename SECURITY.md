# Security Policy

This document outlines the security practices, secret management, and key rotation processes for the NFL Simulation Engine.

## 🔐 Secret Management

### Environment Variables

All secrets and sensitive configuration should be managed through environment variables or secure vault systems. **Never commit secrets to the repository.**

#### Required Environment Variables

| Variable | Description | Example Format |
|----------|-------------|----------------|
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `POSTGRES_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/nfl_sim` |
| `OPENAI_API_KEY` | OpenAI API key (optional) | `sk-...` |
| `NFL_API_KEY` | NFL data API key | `api_key_123...` |
| `JWT_SECRET_KEY` | JWT signing secret | Random 256-bit string |
| `ENCRYPTION_KEY` | Data encryption key | 32-byte base64 encoded |

#### Environment Configuration Files

```bash
# staging.yaml - Staging environment
redis:
  url: ${REDIS_URL}
  timeout: 30

postgres:
  url: ${POSTGRES_URL}
  pool_size: 10

security:
  jwt_secret: ${JWT_SECRET_KEY}
  encryption_key: ${ENCRYPTION_KEY}

logging:
  level: DEBUG
  structured: true
  correlation_ids: true

randomness:
  enabled: true
  seed: null  # Use random seed in staging

# prod.yaml - Production environment  
redis:
  url: ${REDIS_URL}
  timeout: 10
  ssl: true

postgres:
  url: ${POSTGRES_URL}
  pool_size: 20
  ssl_mode: require

security:
  jwt_secret: ${JWT_SECRET_KEY}
  encryption_key: ${ENCRYPTION_KEY}
  rate_limiting: true
  ip_allowlist: ${ALLOWED_IPS}

logging:
  level: INFO
  structured: true
  correlation_ids: true

randomness:
  enabled: false  # Deterministic in production
  seed: ${SIMULATION_SEED}
```

### Secret Storage Best Practices

1. **Use Environment Variables**: Store all secrets in environment variables
2. **Vault Integration**: For production, integrate with HashiCorp Vault, AWS Secrets Manager, or Azure Key Vault
3. **No Hardcoded Secrets**: Never embed API keys, passwords, or tokens in source code
4. **Secret Scanning**: Automated TruffleHog scans prevent accidental commits
5. **Least Privilege**: Grant minimal permissions necessary for each service

## 🔄 Key Rotation Process

### Automated Secret Rotation

#### JWT Secret Keys
- **Rotation Schedule**: Every 90 days
- **Process**:
  1. Generate new JWT secret using secure random generator
  2. Update environment variable in secure store
  3. Restart services to pick up new secret
  4. Verify all JWT operations work correctly
  5. Monitor for authentication failures

#### Database Credentials
- **Rotation Schedule**: Every 180 days
- **Process**:
  1. Create new database user with same permissions
  2. Update connection string with new credentials
  3. Test connectivity from all services
  4. Deploy configuration update
  5. Remove old database user after 24-hour grace period

#### API Keys (External Services)
- **Rotation Schedule**: Quarterly or when compromised
- **Process**:
  1. Generate new API key from provider
  2. Test new key in staging environment
  3. Update production environment variables
  4. Monitor API call success rates
  5. Revoke old API key after verification

### Manual Rotation Triggers

Immediately rotate secrets when:
- Security incident or suspected compromise
- Employee departure with secret access
- Third-party security breach notification
- Compliance audit requirements
- Regular scheduled maintenance

### Rotation Verification Checklist

- [ ] New secret generated using cryptographically secure method
- [ ] Secret tested in staging environment
- [ ] All dependent services updated simultaneously
- [ ] Connectivity and functionality verified
- [ ] Monitoring alerts configured for failures
- [ ] Old secret revoked/deleted after grace period
- [ ] Incident documented in security log

## 🛡️ Security Hardening

### API Security

#### Authentication & Authorization
```python
# RBAC implementation with JWT
@require_permission("simulation:read")
def get_simulation_results(user_context):
    # Scoped access based on user permissions
    pass

@require_permission("simulation:write") 
def create_simulation(user_context):
    # Write operations require elevated permissions
    pass
```

#### Rate Limiting
- **Ingest Endpoints**: 100 requests/minute per API key
- **Simulation Endpoints**: 10 simulations/hour per user
- **Admin Interfaces**: 20 requests/minute per IP

#### Request Signing
All API requests must include:
- `X-API-Key`: Valid API key
- `X-Timestamp`: Request timestamp (max 300 seconds old)
- `X-Signature`: HMAC-SHA256 signature of request body + timestamp

### Network Security

#### IP Allowlisting
```yaml
# Production IP restrictions
security:
  ip_allowlist:
    admin: ["10.0.0.0/8", "192.168.1.100"]
    api: ["0.0.0.0/0"]  # Public API access
    internal: ["10.0.0.0/8"]
```

#### TLS Configuration
- **Minimum Version**: TLS 1.2
- **Cipher Suites**: Modern, secure ciphers only
- **Certificate Validation**: Strict certificate validation
- **HSTS**: HTTP Strict Transport Security enabled

### Data Protection

#### Encryption at Rest
- **Database**: Column-level encryption for sensitive fields
- **File Storage**: AES-256 encryption for data files
- **Backups**: Encrypted backup storage with separate key management

#### Encryption in Transit
- **API Communications**: TLS 1.2+ for all external communications
- **Internal Services**: mTLS for service-to-service communication
- **Database Connections**: SSL/TLS for all database connections

### Monitoring & Alerting

#### Security Events
- Failed authentication attempts (>5 in 10 minutes)
- Unusual API usage patterns
- Database access from new IPs
- Failed secret rotations
- Suspicious simulation patterns

#### Honeypot Integration
```python
# Honeypot endpoints for threat detection
@app.route('/admin/legacy')
def legacy_admin():
    # Log potential intrusion attempt
    security_logger.warning(f"Honeypot access from {request.remote_addr}")
    return "Not Found", 404
```

## 🚨 Incident Response

### Security Incident Classification

#### Critical (P0)
- Active data breach or unauthorized access
- Compromised production systems
- Exposed customer data or secrets

#### High (P1) 
- Failed secret rotation
- Suspicious access patterns
- Potential insider threat

#### Medium (P2)
- Outdated dependencies with security fixes
- Failed security scans
- Policy violations

### Response Process

1. **Detection**: Automated monitoring or manual report
2. **Assessment**: Determine severity and scope
3. **Containment**: Isolate affected systems
4. **Investigation**: Analyze logs and determine root cause
5. **Remediation**: Fix vulnerabilities and rotate secrets
6. **Recovery**: Restore normal operations
7. **Documentation**: Document incident and lessons learned

### Emergency Contacts

- **Security Team**: security@sportieai.com
- **On-Call Engineer**: +1-XXX-XXX-XXXX
- **Incident Commander**: Available 24/7

## 🔍 Security Scanning

### Automated Scans

#### Secret Scanning
- **Tool**: TruffleHog v3
- **Frequency**: Every push and weekly full scan
- **Scope**: All repository files, commit history
- **Actions**: Block commits with secrets, alert security team

#### Dependency Scanning
- **Tool**: GitHub Dependabot + Snyk
- **Frequency**: Daily scans, immediate alerts for critical CVEs
- **Actions**: Auto-update patch versions, manual review for major updates

#### Code Quality & Security
- **Tool**: SonarQube + CodeQL
- **Frequency**: Every PR and nightly full scan
- **Metrics**: Security hotspots, code coverage, complexity

### Manual Security Reviews

#### Quarterly Security Audit
- [ ] Access control review
- [ ] Secret rotation verification
- [ ] Network security assessment
- [ ] Dependency vulnerability scan
- [ ] Incident response plan testing

#### Annual Penetration Testing
- External security firm assessment
- Full-scope application security testing
- Infrastructure vulnerability scanning
- Social engineering assessment

## 📋 Compliance

### Data Governance
- **Data Classification**: Public, Internal, Confidential, Restricted
- **Retention Policies**: Automated data lifecycle management
- **Privacy Controls**: Data anonymization and pseudonymization

### Audit Trail
- All security events logged with tamper-proof timestamps
- User actions tracked with correlation IDs
- Configuration changes audited with approval workflows
- Secret access logged for compliance reviews

### Regulatory Requirements
- **SOC 2 Type II**: Annual compliance verification
- **ISO 27001**: Information security management standards
- **GDPR**: Privacy and data protection compliance (if applicable)

## 📞 Reporting Security Issues

### Internal Reporting
For SportieAI team members:
1. Create security incident ticket
2. Notify security team immediately
3. Do not discuss publicly until resolved

### External Reporting
For external security researchers:
- **Email**: security@sportieai.com
- **PGP Key**: Available on request
- **Response Time**: 48 hours acknowledgment

### Responsible Disclosure
- 90-day disclosure timeline
- Coordinated vulnerability disclosure
- Recognition for valid security findings

---

*This security policy is reviewed quarterly and updated as needed. Last updated: 2025-01-21*