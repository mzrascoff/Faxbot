---
title: FreeSWITCH Go‑Live Checklist
---

# FreeSWITCH Go‑Live Checklist

Self‑hosted backend using FreeSWITCH. Requires a SIP trunk and correct T.38 support via `mod_spandsp`.

## Pre‑flight

- [ ] FreeSWITCH running with `mod_spandsp` enabled
- [ ] SIP trunk registered and reachable (`sofia/gateway/<name>`)
- [ ] T.38 configured where possible; fall back to G.711 if needed
- [ ] Admin Console → Settings → Backend: `freeswitch`
- [ ] Inbound: not supported (use a cloud inbound provider if needed)
- [ ] `PUBLIC_API_URL` set for Admin links (not required for telephony)

## Notes

- Outbound originates via your FreeSWITCH gateway
- No inbound webhooks; inbound support is not available in this backend

Helpful docs
- [FreeSWITCH Setup (Faxbot)](/setup/freeswitch/)
- [FreeSWITCH Project](https://freeswitch.com/)

## Smoke tests

- Place a test outbound fax through your FreeSWITCH gateway

```bash
curl -sS -X POST "$PUBLIC_API_URL/fax" \
  -H "X-API-Key: ${API_KEY:?}" \
  -F "to=+15551234567" \
  -F "file=@README.md" | jq .
```

## Troubleshooting

- Negotiation errors → check T.38 SDP, gateway configuration, and codec settings
- Jobs stuck → verify gateway registration and outbound route permissions

!!! warning "HIPAA posture"
    Keep SIP and media private. Use WireGuard/Tailscale for remote access to Admin only, and review [HIPAA Requirements](/HIPAA_REQUIREMENTS/).

