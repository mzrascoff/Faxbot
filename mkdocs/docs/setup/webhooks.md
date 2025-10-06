---
title: Webhooks
---

# Webhooks

Configure provider callbacks for outbound status and inbound fax delivery. The Admin Console shows exact URLs for your active providers and verifies reachability.

!!! tip "Quick links"
    [:material-lan: Networking & Tunnels](/networking/tunnels/){ .md-button } [:material-stethoscope: Diagnostics](/admin-console/diagnostics/){ .md-button } [:material-puzzle: Plugin Builder](/admin-console/plugin-builder/){ .md-button .md-button--primary }

## Outbound status

- Phaxio: `POST /phaxio-callback` (HMAC verification)
- SignalWire: `POST /signalwire-callback`
- Sinch: status mapped from send response; additional callbacks may be introduced by plugins

## Inbound delivery

- Phaxio: `POST /phaxio-inbound` (HMAC verification)
- Sinch: `POST /sinch-inbound` (use Basic auth; add IP allowlists)
- HumbleFax: `POST /inbound/humblefax/webhook` (HMAC‑SHA256 when configured)
- SignalWire: via Plugin Manager — install or upload a SignalWire inbound plugin; the Admin will display the plugin‑defined inbound path

!!! tip "Find your URLs"
    Admin → Inbound shows the active inbound provider, verification method (HMAC/Basic), and a copy‑to‑clipboard webhook URL. Admin → Settings → Backend lists outbound status callbacks.

## Security

- Use HTTPS URLs
- Enable HMAC or Basic auth where supported
- Avoid quick tunnels for PHI; prefer named tunnels or a domain

## Test quickly

```bash
curl -sS -X POST "$PUBLIC_API_URL/phaxio-callback" \
  -H 'Content-Type: application/json' \
  -d '{"test":true}'
```

Use Admin → Diagnostics to run provider‑specific checks.

See also
- [Networking & Tunnels](/networking/tunnels/)
- [Go‑Live Checklists](/go-live/)
