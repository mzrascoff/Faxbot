---
title: Documo (mFax) — One‑Pager
---

# Documo (mFax) — One‑Pager

Direct upload with Documo’s mFax API.

## Checklist

- [ ] `DOCUMO_API_KEY`
- [ ] Optional: `DOCUMO_BASE_URL`, `DOCUMO_USE_SANDBOX=true`
- [ ] Admin Console → Backend: `documo`
- [ ] `API_KEY` minted; clients send `X-API-Key`
- [ ] `PUBLIC_API_URL` set for Admin links

## Test

```bash
curl -sS -X POST "$PUBLIC_API_URL/fax" \
  -H "X-API-Key: ${API_KEY:?}" \
  -F to=+15551234567 -F file=@README.md | jq .
```

## Help

- [Documo API docs](https://docs.documo.com)
- [mFax pricing & signup](https://www.mfax.io/pricing)

!!! warning "HIPAA"
    Confirm provider retention policies and execute a BAA before handling PHI. See [HIPAA Requirements](/HIPAA_REQUIREMENTS/).

