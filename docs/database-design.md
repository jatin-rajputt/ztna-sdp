# Database Design

| Table | Purpose | Key columns |
|---|---|---|
| users | Login accounts | username, password_hash, status, mfa_enabled, failed_logins, locked_until |
| roles | ADMIN, SECURITY_ANALYST, EMPLOYEE | name |
| user_roles | Links users to roles | user_id, role_id |
| devices | Registered devices and posture | user_id, hostname, registration_status, compliance_status |
| applications | Protected apps | name, upstream_url |
| policies | Which role may reach which app, and under which conditions | role_id, application_id, mfa_required, device_required, max_risk |
| sessions | Access sessions per app | id, user_id, device_id, application_id, expires_at, status |
| audit_logs | Every security event | timestamp, event, username, source_ip, decision, reason |
| risk_events | Risk factors recorded per user | user_id, factor, points |

## Relationships
(Add: users to roles via user_roles; devices belong to a user; policies link a role and an application; sessions link user, device and application.)

## Notes
(Add: password hashes only, never plaintext. MFA secrets are stored unencrypted in this prototype.)