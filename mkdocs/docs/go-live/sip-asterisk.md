---
title: SIP/Asterisk Go‑Live Checklist
---

# SIP/Asterisk Go‑Live Checklist

Self‑hosted backend using Asterisk. Requires proper SIP trunking, NAT, TLS, and T.38 where possible. Inbound delivery is internal; no external provider webhooks.

## Pre‑flight

- [ ] Asterisk reachable and stable; SIP trunk provisioned
- [ ] T.38 enabled end‑to‑end where supported; fall back to G.711 pass‑through if needed
- [ ] AMI credentials configured (Faxbot requires AMI; see Settings)
- [ ] Admin Console → Settings → Backend: `sip`
- [ ] Inbound enabled and storage configured for inbound PDFs
- [ ] `PUBLIC_API_URL` set for Admin links (not required for telephony)
- [ ] Ports/firewall hardened; TLS on signaling preferred

!!! tip "Tunnels"
    Don’t expose SIP/UDPTL over public tunnels. If you need remote Admin access, tunnel only the HTTPS API (8080) and keep telephony private.

## Inbound

- Internal route: `POST /_internal/asterisk/inbound` (used by your Asterisk dialplan)
- Inbound PDFs are stored via the configured storage backend and visible in Inbox

Helpful docs
- [SIP Setup (Faxbot)](/setup/sip-asterisk/)
- [Asterisk Project](https://wiki.asterisk.org/wiki/display/AST/Home)

## Smoke tests

- Place a test outbound fax through your trunk
- Post a simulated inbound to validate storage and Inbox

```bash
curl -sS -X POST "$PUBLIC_API_URL/admin/inbound/simulate" \
  -H "X-API-Key: ${API_KEY:?}" \
  -H 'Content-Type: application/json' \
  -d '{"backend":"sip","fr":"+15559876543","to":"+15551234567","pages":1}' | jq .
```

## Troubleshooting

- One‑way audio or failure → verify NAT/ALG, T.38 negotiation, and trunk codecs
- Jobs stuck → check AMI connectivity and Asterisk logs
- Inbound missing → confirm dialplan posts to `/_internal/asterisk/inbound` and storage backend is healthy

!!! warning "HIPAA posture"
    Use WireGuard/Tailscale for remote access; never expose AMI or SIP to the public internet. Review [HIPAA Requirements](/HIPAA_REQUIREMENTS/).

