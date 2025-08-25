# Security & Privacy (Backend-Aligned)

- GPT never queries DB directly; all access via backend APIs
- Backend enforces authZ, rate limits
- GPT redacts sensitive identifiers unless needed (e.g. portfolio_id only)
