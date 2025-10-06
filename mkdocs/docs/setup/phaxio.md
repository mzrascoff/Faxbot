---
title: Phaxio Setup
---

# Phaxio Setup

Cloud backend where Phaxio fetches your PDF via a tokenized URL and posts status callbacks.

## Steps

1) Admin Console → Setup Wizard → choose Phaxio
2) Enter `PHAXIO_API_KEY` and `PHAXIO_API_SECRET`
3) Set `PUBLIC_API_URL` (HTTPS) so Phaxio can reach your callbacks and tokenized PDFs
4) In Phaxio console, set status callback URL to `<PUBLIC_API_URL>/phaxio-callback`
5) Enable HMAC verification: `PHAXIO_VERIFY_SIGNATURE=true`

!!! tip "Evaluating without a domain?"
    Use Admin → Tools → Tunnels to create a Cloudflare Quick Tunnel (non‑HIPAA) and copy the public URL into `PUBLIC_API_URL`. Replace with a permanent HTTPS domain for production.

## Webhooks

- Status callback: `POST /phaxio-callback`
- Inbound receiving: `POST /phaxio-inbound`
- Verification: HMAC (header `X-Phaxio-Signature`)

Helpful links
- [Webhooks overview](https://www.phaxio.com/docs/api/v2.1/intro/webhooks)
- [Send webhooks](https://www.phaxio.com/docs/api/v2.1/faxes/send_webhooks)
- [Receive webhooks](https://www.phaxio.com/docs/api/v2.1/faxes/receive_webhooks)
- [Verify callbacks](https://www.phaxio.com/docs/security/callbacks)

## Quick test

```bash
curl -sS -X POST "$PUBLIC_API_URL/fax" \
  -H "X-API-Key: ${API_KEY:?}" \
  -F to=+15551234567 -F file=@README.md | jq .
```

!!! warning "HIPAA posture"
    Execute a BAA, disable provider document retention, and use a permanent HTTPS domain. Avoid quick tunnels for PHI. See [HIPAA Requirements](/HIPAA_REQUIREMENTS/).

