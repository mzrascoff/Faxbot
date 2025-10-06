---
title: Sinch Setup (Fax API v3)
---

# Sinch Setup (Fax API v3)

Direct upload backend: Faxbot posts PDFs to Sinch; PUBLIC_API_URL not required for outbound.

## Steps

1) Get Sinch keys: [dashboard.sinch.com/settings/access-keys](https://dashboard.sinch.com/settings/access-keys)
2) Admin Console → Setup Wizard → choose Sinch
3) Enter `SINCH_PROJECT_ID`, `SINCH_API_KEY`, `SINCH_API_SECRET`
4) Optional for HIPAA: `SINCH_AUTH_METHOD=oauth` (and `SINCH_AUTH_BASE_URL` for your region)
5) Optional inbound: set `<PUBLIC_API_URL>/sinch-inbound` and enforce Basic auth

## Webhooks

- Outbound: mapped from send response (callbacks may be added later)
- Inbound: `POST /sinch-inbound`
- Verification: Basic auth headers + IP allowlists

Helpful link
- [Sinch Fax API — Reference](https://developers.sinch.com/docs/fax/api-reference/)

## Quick test

```bash
curl -sS -X POST "$PUBLIC_API_URL/fax" \
  -H "X-API-Key: ${API_KEY:?}" \
  -F to=+15551234567 -F file=@README.md | jq .
```

!!! warning "HIPAA posture"
    Prefer OAuth for outbound auth, enforce HTTPS, and avoid quick tunnels for PHI. See [HIPAA Requirements](/HIPAA_REQUIREMENTS/).

