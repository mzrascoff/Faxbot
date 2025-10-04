---
layout: default
title: Diagnostics
nav_order: 45
permalink: /diagnostics
---

# Diagnostics

Faxbot includes lightweight, non-destructive diagnostics to validate provider connectivity and webhook reachability from inside the API container.

Endpoints (admin)
- GET `/admin/diagnostics/sinch` → DNS, auth presence, OAuth/basic probe, v3 path compatibility; returns exact probed URLs + status codes.
- GET `/admin/diagnostics/humblefax` → DNS, Basic auth reachability, computed webhook URL reachability (HEAD/GET tolerant), exact probe statuses.
- POST `/admin/diagnostics/run` → Bounded, trait-driven checks across active providers (health, Ghostscript if required, storage when inbound requires it).

Admin Console
- Tools → Tunnels page exposes “Run Sinch Diagnostics” and “Run HumbleFax Diagnostics” when relevant, and shows the raw JSON report.

Troubleshooting Tips
- DNS failures: verify container DNS or override `SINCH_BASE_URL`/`HUMBLEFAX_API_HOST` if using a custom region/host.
- Auth failures: confirm credentials in Settings and ensure the selected auth method (OAuth2 vs Basic) matches provider configuration.
- Webhook URL not reachable: set `PUBLIC_API_URL` (HTTPS) or use a stable named tunnel. Quick tunnels can be rejected by providers.

Security
- No PHI is logged. Probes avoid sending recipient numbers or document content.
- Webhook reachability checks tolerate 405 Method Not Allowed to avoid accidental side effects.

