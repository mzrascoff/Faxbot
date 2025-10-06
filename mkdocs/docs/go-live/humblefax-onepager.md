---
title: HumbleFax — One‑Pager
---

# HumbleFax — One‑Pager

Quick steps for outbound + inbound with HumbleFax.

## Checklist

- [ ] `HUMBLEFAX_ACCESS_KEY`, `HUMBLEFAX_SECRET_KEY`
- [ ] Optional: `HUMBLEFAX_FROM_NUMBER`
- [ ] Admin Console → Backend: `humblefax`
- [ ] `PUBLIC_API_URL` (HTTPS)
- [ ] Webhook: `<PUBLIC_API_URL>/inbound/humblefax/webhook`
- [ ] Optional: `HUMBLEFAX_WEBHOOK_SECRET` (HMAC)
- [ ] `API_KEY` minted; clients send `X-API-Key`

## Test

```bash
curl -sS -X POST "$PUBLIC_API_URL/fax" \
  -H "X-API-Key: ${API_KEY:?}" \
  -F to=+15551234567 -F file=@README.md | jq .
```

## Help

- [How it works](https://humblefax.com/?jump=how-it-works)
- [Sign up](https://humblefax.com/signup)
- [Dashboard](https://humblefax.com/dashboard)

!!! note "HIPAA"
    HumbleFax may not be HIPAA‑compliant. For PHI, choose a HIPAA‑capable provider and follow [HIPAA Requirements](/HIPAA_REQUIREMENTS/).

