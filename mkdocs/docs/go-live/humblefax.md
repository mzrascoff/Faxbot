---
title: HumbleFax Go‑Live Checklist
---

# HumbleFax Go‑Live Checklist

HumbleFax is a lightweight cloud provider supported for outbound sending and inbound delivery via webhooks. It also offers a native email‑to‑fax flow you can use alongside Faxbot.

!!! tip "Quick links"
    [:material-help-circle: How it works](https://humblefax.com/?jump=how-it-works){ .md-button } [:material-account-plus: Sign up](https://humblefax.com/signup){ .md-button } [:material-cog: Setup Wizard](/admin-console/setup-wizard/){ .md-button .md-button--primary }

## Pre‑flight

- [ ] HumbleFax Access Key and Secret Key
- [ ] Optional default From number (`HUMBLEFAX_FROM_NUMBER`)
- [ ] Admin Console → Settings → Backend: `humblefax`
- [ ] Set `API_KEY` and ensure clients send `X-API-Key`
- [ ] `PUBLIC_API_URL` points to an HTTPS host
- [ ] Inbound webhooks configured to `<PUBLIC_API_URL>/inbound/humblefax/webhook`
- [ ] Optional: `HUMBLEFAX_WEBHOOK_SECRET` set for HMAC verification

!!! tip "One‑shot tunnel + webhook register"
    Use `scripts/setup-humblefax-tunnel.sh` to start a tunnel, detect the public URL, set `HUMBLEFAX_CALLBACK_BASE`, and register the webhook automatically.

## Webhooks

- Outbound status: `SentFax` events update job status by `provider_sid`
- Inbound delivery: `IncomingFax` events trigger background PDF download into your configured storage backend
- Verification: HMAC‑SHA256 when `HUMBLEFAX_WEBHOOK_SECRET` is set (header `X-Humblefax-Signature`)

Helpful links
- [HumbleFax – How it works](https://humblefax.com/?jump=how-it-works)
- [HumbleFax – Sign up](https://humblefax.com/signup)
- [HumbleFax – Dashboard](https://humblefax.com/dashboard)

## Email → Fax (native HumbleFax)

Send an email to `<fax-number>@humblefax.com` with your attachments. Subject/body become a cover sheet. This works independently of Faxbot and is useful for quick wins.

## Smoke tests

Send a test fax via Faxbot

```bash
curl -sS -X POST "$PUBLIC_API_URL/fax" \
  -H "X-API-Key: ${API_KEY:?}" \
  -F "to=+15551234567" \
  -F "file=@README.md" | jq .
```

Diagnostics

```bash
curl -sS -H "X-API-Key: ${API_KEY:?}" \
  "$PUBLIC_API_URL/admin/diagnostics/humblefax" | jq .
```

## Troubleshooting

- Webhook URL not reachable → set `PUBLIC_API_URL` (HTTPS) or use a stable tunnel
- Auth failures → verify access/secret keys and optional From number
- No inbound PDFs → ensure storage backend is configured and reachable

!!! note "HIPAA posture"
    HumbleFax may not be HIPAA‑compliant. If you handle PHI, choose a HIPAA‑capable provider and follow [HIPAA Requirements](/HIPAA_REQUIREMENTS/).
