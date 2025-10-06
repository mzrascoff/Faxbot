---
title: Phaxio Go‑Live Checklist
---

# Phaxio Go‑Live Checklist

Phaxio is a cloud backend where the provider fetches your PDF via a tokenized URL and posts status callbacks. This page covers the essentials to move from eval to production.

!!! tip "Quick links"
    [:material-webhook: Phaxio Webhooks](https://www.phaxio.com/docs/api/v2.1/intro/webhooks){ .md-button } [:material-shield-check: Verify Callbacks](https://www.phaxio.com/docs/security/callbacks){ .md-button } [:material-cog: Setup Wizard](/admin-console/setup-wizard/){ .md-button .md-button--primary }

## Pre‑flight

- [ ] Phaxio account and API credentials (`PHAXIO_API_KEY`, `PHAXIO_API_SECRET`)
- [ ] Admin Console → Settings → Backend: `phaxio`
- [ ] Set `API_KEY` and ensure clients send `X-API-Key`
- [ ] `PUBLIC_API_URL` points to an HTTPS host reachable by Phaxio
- [ ] Callback URL in Phaxio console set to `<PUBLIC_API_URL>/phaxio-callback`
- [ ] HMAC verification enabled (`PHAXIO_VERIFY_SIGNATURE=true`)
- [ ] Storage policy reviewed (HIPAA: disable provider document retention)
- [ ] BAA executed (HIPAA)

!!! tip "Fast path with a tunnel (non‑HIPAA)"
    Use Admin Console → Tools → Tunnels to start a Cloudflare Quick Tunnel, then copy the public URL into `PUBLIC_API_URL`. Set the status callback URL in Phaxio to `<PUBLIC_API_URL>/phaxio-callback`. When you move to production, replace the quick tunnel with a permanent HTTPS domain.

## Webhooks

- Outbound status: `POST /phaxio-callback`
- Inbound receiving (optional): `POST /phaxio-inbound`
- Verification: HMAC (header `X-Phaxio-Signature`)

Helpful docs
- [Phaxio Webhooks (v2.1)](https://www.phaxio.com/docs/api/v2.1/intro/webhooks)
- [Send fax webhooks](https://www.phaxio.com/docs/api/v2.1/faxes/send_webhooks)
- [Receive fax webhooks](https://www.phaxio.com/docs/api/v2.1/faxes/receive_webhooks)
- [Verifying callback requests](https://www.phaxio.com/docs/security/callbacks)

## Smoke tests

Send a test fax via Faxbot

```bash
curl -sS -X POST "$PUBLIC_API_URL/fax" \
  -H "X-API-Key: ${API_KEY:?}" \
  -F "to=+15551234567" \
  -F "file=@README.md" | jq .
```

Poll job status (replace `{job_id}`)

```bash
curl -sS "$PUBLIC_API_URL/fax/{job_id}" -H "X-API-Key: ${API_KEY}" | jq .
```

## Troubleshooting

- 401 from Faxbot → set `API_KEY` and send `X-API-Key`
- Callback not received → verify `PUBLIC_API_URL` is HTTPS and reachable; confirm `<PUBLIC_API_URL>/phaxio-callback` in Phaxio console
- Signature mismatch → ensure `PHAXIO_VERIFY_SIGNATURE=true` and use the correct secret
- 415 / file errors → only PDF/TXT are accepted; convert images to PDF first

!!! warning "HIPAA posture"
    Do not use quick tunnels for PHI. Use a permanent HTTPS domain, disable provider document retention, execute a BAA, and review [HIPAA Requirements](/HIPAA_REQUIREMENTS/).
