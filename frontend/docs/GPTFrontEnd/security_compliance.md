# Security & Compliance

- Auth: Bearer tokens (JWT), short-lived; refresh securely.
- RBAC: Ensure user can only access their `portfolioId` resources.
- Rate Limits: 10 req/s per user; burst 30.
- Logging: Redact tokens; include request IDs for tracing.
- Data at Rest: Encrypt DB; secrets via vault (not env files).
