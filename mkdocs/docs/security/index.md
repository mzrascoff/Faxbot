---
title: Security
---

# Security

Secure defaults for keys, webhooks, storage, and Admin access.

## Keys

- Use API Keys with scopes; rotate regularly
- Prefer OAuth/OIDC for Admin login where available

## Webhooks

- Enforce HMAC where supported (Phaxio, HumbleFax)
- Use Basic auth for providers without signing (Sinch inbound)
- Always use HTTPS

## Storage

- Tokenized, short‑TTL links for PDFs
- S3/compatible storage supported; avoid public buckets

## HIPAA

- Execute BAA with cloud providers
- Disable provider document retention
- Avoid quick tunnels; use private tunnels and a permanent HTTPS domain

See also
- [HIPAA Requirements](/HIPAA_REQUIREMENTS/)
- [Networking & Tunnels](/networking/tunnels/)

