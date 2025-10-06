---
title: Settings
---

# Settings

Manage outbound/inbound providers, storage, and security.

## Providers

=== "Outbound"

    Select your sending backend. Cloud providers expose credential fields and status callbacks; self‑hosted backends show AMI/T.38 guidance.

=== "Inbound"

    Choose an inbound provider or install one via Plugins. The UI shows the exact webhook URL and verification method with copy‑button.

!!! tip "Traits‑driven UI"
    The Settings screen renders fields from provider traits — no backend name checks. This guarantees clean isolation and correct guidance.

## Storage

- Local or S3‑compatible storage for inbound PDFs and artifacts
- Short‑TTL tokens for PDF access; scope‑guarded downloads

## Security

- API Key enforcement (`X-API-Key`)
- HMAC verification for supported providers; Basic auth for others
- Optional OAuth/OIDC for Admin login

See also
- [Webhooks](/setup/webhooks/)
- [Diagnostics](/admin-console/diagnostics/)

