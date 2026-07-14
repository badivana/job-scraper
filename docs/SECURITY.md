# Security

## Purpose

To describe the security controls, data protection measures, and compliance considerations for the AI‑Powered Job Finder platform. The architecture leverages Supabase’s built‑in security features (authentication, Row Level Security, encrypted storage) complemented by application‑level safeguards.

## Contents

- Overview
- Authentication & Identity Management
- Authorization & Access Control
- Data Encryption
- Network & Infrastructure Security
- Input Validation & Output Encoding
- Logging & Monitoring
- Vulnerability Management
- Compliance & Privacy
- Incident Response
- Security Testing

## Overview

Security is a foundational concern throughout the system. We rely on Supabase for hardened baseline services (PostgreSQL, Auth, Storage) and apply defense‑in‑depth principles at the application layer (FastAPI), infrastructure (Docker, networking), and operational processes (CI/CD, monitoring).

## Authentication & Identity Management

- **Primary Identity Provider**: Supabase Auth (email/password, OAuth providers: Google, GitHub, etc.).
- **Token Format**: JSON Web Token (JWT) signed with RS256; includes claims `sub` (user ID), `email`, `role` (`anon`/`authenticated`), `aud`, `exp`, `iat`.
- **Token Issuance**: Occurs exclusively via Supabase endpoints (`/auth/v1/token`, `/auth/v1/signup`, `/auth/v1/otp`, etc.). The frontend never handles raw passwords.
- **Token Validation**: All protected API endpoints verify the JWT signature using Supabase’s published JWKS (`https://<project>.supabase.co/auth/v1/keys`). The backend also checks:
  - Token not expired.
  - Token not revoked (optional via Redis‑based token blacklist for logout).
  - `aud` matches the project’s anonymous/public key.
- **Password Policies** (enforced by Supabase):
  - Minimum length 12 characters.
  - Requires mix of uppercase, lowercase, digit, special character.
  - Rate‑limited login attempts (via Supabase brute‑force protection).
- **Multi‑Factor Authentication (MFA)**: Optional TOTP or SMS via Supabase Auth; enforced for admin roles.
- **Session Management**: Short‑lived access tokens (15 minutes) + refresh tokens (rotating, stored HttpOnly cookie). Refresh token rotation prevents replay.
- **User Deletion**: When a user requests account deletion, the backend:
  - Revokes all refresh tokens.
  - Calls Supabase Auth admin API to delete the user (which cascades to auth‑related data).
  - Issues a GDPR‑compliant erasure request for personal data (see Data Retention section).

## Authorization & Access Control

- **Role‑Based Access Control (RBAC)**: Two primary roles:
  - `anon` – unauthenticated (limited to public endpoints and static assets).
  - `authenticated` – logged‑in users (can access own resources).
  - `service_role` – bypasses RLS, used exclusively by trusted backend services (FastAPI) and administrative tools.
- **Row Level Security (RLS)**:
  - Enabled on all tables containing user‑specific data (`users`, `resumes`, `saved_jobs`, `applications`, `generated_documents`, `notifications`, `search_history`, etc.).
  - Policies are defined using `auth.uid()` (the UUID from `auth.users`) to enforce “users can only see/modify their own data”.
  - Example policy for `resumes`:
    ```sql
    CREATE POLICY user_own_resume ON resumes
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);
    ```
  - Tables that are reference or public (e.g., `jobs`, `skills`) have `SELECT` granted to `anon` (read‑only) and `INSERT/UPDATE/DELETE` restricted to `service_role`.
- **Column‑Level Security** (where applicable): Sensitive fields such as `raw_text` of resumes are not exposed in API responses unless explicitly needed; only metadata and derived vectors are returned.
- **API Authorization**:
  - Endpoints inspect the JWT `sub` claim and compare it to resource IDs (e.g., `/resumes/{id}` must match `user_id`).
  - Admin‑only endpoints additionally verify `role` claim equals `service_role` or a custom `admin` claim (if we extend roles).
- **Principle of Least Privilege**: Database user used by the application (`app_user`) has only `SELECT`, `INSERT`, `UPDATE`, `DELETE` on `public.*` and `USAGE` on schemas; no `DROP`, `ALTER`, or access to `auth` schema except via Supabase Auth API.

## Data Encryption

- **At Rest**:
  - Supabase PostgreSQL encrypts data using Microsoft Transparent Data Encryption (TDE) or equivalent AES‑256 at the storage layer.
  - Supabase Storage buckets encrypt objects server‑side (AES‑256).
  - Backups (physical and logical) are stored encrypted.
- **In Transit**:
  - All external communication (client ↔ API, API ↔ Supabase, API → Apify/OpenAI, API ↔ Redis) uses TLS 1.2+.
  - Enforced via HTTPS and WSS (WebSocket Secure).
  - Internal service‑to‑service calls within the same VPC/network also use TLS (mTLS optional for future hardening).
- **Key Management**:
  - Supabase manages encryption keys for its services.
  - Application secrets (Supabase `anon` and `service_role` keys, API keys for Apify/OpenAI, JWT verification keys) are stored exclusively in environment variables or a secret manager (AWS Secrets Manager, GCP Secret Manager, or Docker secrets) – never in source code.
  - Keys are rotated quarterly or upon suspicion of compromise.

## Network & Infrastructure Security

- **Network Isolation**:
  - Frontend (Next.js) hosted on a public CDN or container platform with public ingress.
  - Backend (FastAPI) deployed in a private subnet; exposed only via an API gateway or load balancer with TLS termination.
  - Supabase services are accessed over public internet but restrict IP allow‑list if possible (Supabase allows trusted IPs for `service_role` connections).
  - Redis instance is private, accessible only from backend and worker subnets.
- **Firewalls & Security Groups**:
  - Inbound: Allow HTTPS (443) from internet to frontend and API gateway.
  - Outbound: Allow HTTPS to Supabase, Apify, OpenAI, and any external services; restrict to required destinations.
- **Docker Security**:
  - Images built from minimal base (e.g., `python:3.12-slim`).
  - Run as non‑root user.
  - Drop unnecessary capabilities (`CAP_NET_RAW`, etc.).
  - Read‑only root filesystem where possible; temporary volumes for logs/cache.
- **Dependency Management**:
  - Use `pip` with `--no-deps` and lock files (`requirements.txt` + hash checking).
  - Regularly run `pip-audit` and `safety` in CI.
  - Keep base images updated via automated rebuilds (e.g., Dependabot or Renovate).
- **Secrets in CI/CD**:
  - GitHub Actions secrets store credentials for Docker registry, cloud providers, and Supabase service keys.
  - No secrets are logged; mask output.

## Input Validation & Output Encoding

- **Validation**:
  - All incoming data (JSON, form, query params) validated via Pydantic models (strict `str`, `conint`, `EmailStr`, `UUID`, regex patterns).
  - Reject unknown fields (`extra='forbid'`).
  - Length limits on strings (e.g., bio ≤ 500 characters, filename ≤ 255 bytes).
- **Sanitization**:
  - HTML escape any user‑generated content before inserting into templates (Jinja2 auto‑escape enabled).
  - For markdown‑generated content (cover letters), strip or escape HTML tags before converting to PDF.
- **Output Encoding**:
  - API responses are `application/json`; no HTML is returned unless explicitly documented.
  - Error messages avoid leaking stack traces or internal details in production.

## Logging & Monitoring

- **Structured Logging**:
  - JSON logs via `structlog` or `python-json-logger`.
  - Fields: `timestamp`, `level`, `logger`, `request_id`, `trace_id`, `user_id` (if available), `message`, `error_details`.
  - Exclude sensitive data: passwords, tokens, personal data (PII) are redacted (`[REDACTED]`).
- **Log Destinations**:
  - Stdout/stderr captured by container orchestrator (e.g., AWS ECS, Cloud Run) and forwarded to a logging stack (ELK, Loki, or CloudWatch).
  - Retention: 30 days for operational logs, 90 days for audit logs.
- **Audit Trail**:
  - Critical actions (login, signup, password change, data export, role change, document generation) write to an `audit_log` table with immutable append‑only design (or use Supabase’s built‑in audit log extension).
  - Fields: `actor_user_id`, `action`, `target_table`, `target_id`, `changes_json`, `timestamp`.
- **Metrics**:
  - Prometheus endpoint exposing:
    - Request latency (by endpoint, status).
    - Error rates.
    - Queue depths (Celery).
    - Cache hit/miss ratios (Redis).
    - Authentication events (success/failure).
    - External API call latencies (Apify, OpenAI).
- **Alerting**:
  - Critical alerts (e.g., auth failure spike, 5xx error rate > 1%, latency > 2 s SLA) routed to PagerDuty/Slack.
  - Daily security digest summary.

## Vulnerability Management

- **Dependency Scanning**:
  - Automated in each pull request using `pip-audit`, `safety`, and `dependabot`.
  - Fail build on high‑severity CVEs.
- **Container Image Scanning**:
  - Use Trivy or Clair in CI to scan for OS and language vulnerabilities.
- **Penetration Testing**:
  - Annual external penetration test (grey‑box) covering OWASP Top 10.
  - Quarterly internal web‑app scans with OWASP ZAP.
- **Patch Management**:
  - OS patches applied via base image rebuild (weekly).
  - Application dependencies updated automatically via Dependabot; manual review for major versions.

## Compliance & Privacy

- **GDPR / CCPA**:
  - Right to Access: Provide endpoint `/api/v1/me/export` that returns all personal data in JSON (including resume text, job history, etc.) within 30 days.
  - Right to Rectification: Allow users to edit profile, resume fields, preferences.
  - Right to Erasure: As described in Authentication section; also anonymizes associated analytics data (replace `user_id` with null).
  - Data Minimization: Store only what is necessary for core functionality; avoid logging полн.
  - Consent: Explicit opt‑in for marketing communications; separate from service terms.
- **Data Residency**: Choose Supabase region (e.g., US‑East, EU‑West) based on user geography; optionally allow region selection per account.
- **Privacy by Design**:
  - Pseudonymization: Use UUIDs instead of sequential IDs; store email only in `auth.users` (not duplicated elsewhere unless needed for login recovery).
  - Purpose Limitation: Data used solely for job matching, notifications, and account management.
- **Legal**:
  - Terms of Service and Privacy Policy hosted at `/terms` and `/privacy`.
  - DMCA takedown procedure for copyrighted material in user‑generated content (e.g., cover letters).

## Incident Response

- **Preparation**:
  - Run tabletop exercises quarterly.
  - Maintain runbooks for common scenarios (credential leak, ransomware, data breach).
- **Detection**:
  - SIEM correlates logs (auth failures, spike in 401/403, abnormal data export volume).
  - Alert thresholds trigger automated playbooks.
- **Containment**:
  - Revoke compromised `service_role` or `anon` keys immediately.
  - Isolate affected container instances; scale down malicious workloads.
  - Enable Supabase “disable auth” temporarily if needed (with maintenance notice).
- **Eradication**:
  - Patch vulnerabilities, rotate all keys, audit logs for unauthorized access.
- **Recovery**:
  - Restore from latest clean backup (Supabase point‑in‑time recovery) if data corrupted.
  - Verify integrity before resuming traffic.
- **Post‑mortem**:
  - Document timeline, root cause, lessons learned.
  - Update controls and testing accordingly.

## Security Testing

- **Static Analysis**: `bandit` (Python) and `semgrep` run on each commit.
- **Dynamic Analysis**: Nightly scans with OWASP ZAP against a staging environment.
- **API Security**: Scheduled runs of `contract-test` using `schemathesis` against OpenAPI spec.
- **Red‑Team/Blue‑Team**: Annual exercise with external security firm.
- **Bug Bounty**: Optional program hosted on HackerOne/Intigriti for responsible disclosure.

## Summary

By combining Supabase’s hardened authentication, encrypted storage, and RLS with rigorous application‑level validation, logging, and monitoring, the platform achieves a strong security posture suitable for handling personal data (resumes, job history) while remaining developer‑friendly and compliant with major privacy regulations.

---  
*Document version: 1.0*  
*Last updated: 2026-07-14*