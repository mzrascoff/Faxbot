---
title: Networking & Tunnels
---

# Networking & Tunnels

Options to reach your Faxbot API from outside your LAN. Use a quick tunnel for demos, and a HIPAA‑capable tunnel for production.

!!! tip "Quick links"
    [:material-cog: Setup Wizard](/admin-console/setup-wizard/){ .md-button } [:material-stethoscope: Diagnostics](/admin-console/diagnostics/){ .md-button } [:material-webhook: Webhooks](/setup/webhooks/){ .md-button .md-button--primary }

## Options

- Cloudflare Quick Tunnel (non‑HIPAA): easiest way to test webhooks and the Admin Console over the internet.
- WireGuard or Tailscale (HIPAA‑capable): private, durable connectivity for Admin/iOS; keep SIP/UDPTL private.
- Public HTTPS domain: for production, terminate TLS and expose only the API port.

!!! tip "Admin Console helper"
    Admin → Tools → Tunnels lets you start/stop quick tunnels, tail logs, and auto‑detect your public URL. The Admin also renders the best base URL for mobile pairing.

## Quick Tunnel (Cloudflare)

Use for evaluations only (no PHI). The Admin can discover the `https://*.trycloudflare.com` URL and set `PUBLIC_API_URL`. Replace with a permanent hostname before go‑live.

## WireGuard / Tailscale

Use a private tunnel for production, especially with PHI or self‑hosted backends (SIP/Asterisk/FreeSWITCH).

Checklist
- [ ] Do not expose SIP/UDPTL publicly
- [ ] Expose only HTTPS API (8080)
- [ ] Rate limit and enforce strong TLS
- [ ] Verify mobile pairing and Admin access through the tunnel

## Troubleshooting

- Webhook not reaching → verify `PUBLIC_API_URL` is set and reachable over HTTPS
- Quick tunnel frequently changes URL → providers may reject it; use a named tunnel or domain
- Mobile pairing fails → ensure the best base URL resolves on device and that the tunnel is running

See also
- [Webhooks](/setup/webhooks/)
- [Admin Console: Diagnostics](/admin-console/diagnostics/)
