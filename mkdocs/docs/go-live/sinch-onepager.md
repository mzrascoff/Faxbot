---
title: Sinch Go‑Live — One‑Pager
---

# Sinch Go‑Live — One‑Pager

Direct upload with Fax API v3.

## Checklist

- [ ] `SINCH_PROJECT_ID`, `SINCH_API_KEY`, `SINCH_API_SECRET`
- [ ] Admin Console → Backend: `sinch`
- [ ] Optional: `SINCH_AUTH_METHOD=oauth` (HIPAA‑aligned)
- [ ] Inbound (optional): `<PUBLIC_API_URL>/sinch-inbound` + Basic auth
- [ ] `API_KEY` minted; clients send `X-API-Key`
- [ ] `PUBLIC_API_URL` set for Admin links

## Test

```bash
curl -sS -X POST "$PUBLIC_API_URL/fax" \
  -H "X-API-Key: ${API_KEY:?}" \
  -F to=+15551234567 -F file=@README.md | jq .
```

## Help

- [Sinch Fax API — Reference](https://developers.sinch.com/docs/fax/api-reference/)
- [Access Keys (Dashboard)](https://dashboard.sinch.com/settings/access-keys)

## HIPAA checklist

- [ ] :material-shield-key: Prefer OAuth (`SINCH_AUTH_METHOD=oauth`)
- [ ] :material-lock-check: HTTPS enforced; strong TLS
- [ ] :material-eye-off: No PHI in logs; keys masked
- [ ] :material-key-change: Keys rotated; least‑privilege access

!!! warning "HIPAA"
    Prefer OAuth, enforce HTTPS, and review [HIPAA Requirements](/HIPAA_REQUIREMENTS/).
