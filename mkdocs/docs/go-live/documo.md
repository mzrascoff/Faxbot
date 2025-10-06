---
title: Documo (mFax) Go‑Live Checklist
---

# Documo (mFax) Go‑Live Checklist

Documo’s mFax API is a cloud backend with direct upload. PUBLIC_API_URL is not required for outbound, but is recommended for Admin links.

## Pre‑flight

- [ ] Documo API Key
- [ ] Environment: `DOCUMO_API_KEY`, optional `DOCUMO_BASE_URL`, optional `DOCUMO_USE_SANDBOX=true`
- [ ] Admin Console → Settings → Backend: `documo`
- [ ] Set `API_KEY` and ensure clients send `X-API-Key`
- [ ] `PUBLIC_API_URL` set for Admin links

## Notes

- Outbound uses direct upload; status is derived from provider responses
- Inbound not supported (use a different inbound provider if needed)

Helpful docs
- [Documo API docs](https://docs.documo.com)
- [mFax pricing & signup](https://www.mfax.io/pricing)

## Smoke tests

Send a test fax via Faxbot

```bash
curl -sS -X POST "$PUBLIC_API_URL/fax" \
  -H "X-API-Key: ${API_KEY:?}" \
  -F "to=+15551234567" \
  -F "file=@README.md" | jq .
```

## Troubleshooting

- 401 from Faxbot → set `API_KEY` and send `X-API-Key`
- Job not created → verify Production vs Sandbox selection; check API key validity
- 413 / size errors → adjust `MAX_FILE_SIZE_MB`; only PDF/TXT accepted

!!! warning "HIPAA posture"
    Confirm provider retention policies and execute a BAA before handling PHI. Review [HIPAA Requirements](/HIPAA_REQUIREMENTS/).

