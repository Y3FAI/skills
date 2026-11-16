# Security

**Last updated:** {{DATE}}

## 1. What we protect

Accounts, personal data, secrets, the service's availability.

## 2. Rules

- Secrets never enter the repo; `.env*` is gitignored; `.env.example` lists names only.
- Never log personal data, codes or tokens.
- Validate every input on the server; never trust identity or role from the request body.
- Every endpoint: auth, authz, rate limit, validation, test.

## 3. Threats and mitigations

| Threat | Mitigation | Test |
|---|---|---|
