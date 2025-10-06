---
title: SIP/Asterisk — One‑Pager
---

# SIP/Asterisk — One‑Pager

Self‑hosted telephony with Asterisk.

## Checklist

- [ ] Trunk registered; NAT/TLS configured
- [ ] T.38 enabled (or G.711 fallback)
- [ ] AMI credentials set in Admin
- [ ] Admin Console → Backend: `sip`
- [ ] Inbound enabled and storage configured
- [ ] `PUBLIC_API_URL` set for Admin links

## Test

- Send a test fax via your trunk
- Simulate inbound to verify storage and Inbox

```bash
curl -sS -X POST "$PUBLIC_API_URL/admin/inbound/simulate" \
  -H "X-API-Key: ${API_KEY:?}" \
  -H 'Content-Type: application/json' \
  -d '{"backend":"sip","fr":"+15559876543","to":"+15551234567","pages":1}' | jq .
```

## Help

- [SIP Setup (Faxbot)](/setup/sip-asterisk/)
- [Asterisk Project](https://wiki.asterisk.org/wiki/display/AST/Home)

!!! warning "HIPAA"
    Keep telephony private. Use WireGuard/Tailscale for Admin only and review [HIPAA Requirements](/HIPAA_REQUIREMENTS/).

