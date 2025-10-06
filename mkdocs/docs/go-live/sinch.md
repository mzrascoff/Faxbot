---
title: Sinch Go‑Live Checklist (Fax API v3)
---

# Sinch Go‑Live Checklist (Fax API v3)

Sinch Fax API v3 uses direct upload: Faxbot posts your file to Sinch and maps the immediate response. PUBLIC_API_URL is not required for outbound, but is recommended for Admin/Diagnostics and inbound.

!!! tip "Quick links"
    [Sinch Fax API Reference](https://developers.sinch.com/docs/fax/api-reference/){ .md-button } [Access Keys Dashboard](https://dashboard.sinch.com/settings/access-keys){ .md-button } [Setup Wizard](/admin-console/setup-wizard/){ .md-button .md-button--primary }

## Pre‑flight

- [ ] Sinch project and access keys (Dashboard → Settings → Access Keys)
- [ ] Environment: `SINCH_PROJECT_ID`, `SINCH_API_KEY`, `SINCH_API_SECRET`
- [ ] Optional: `SINCH_AUTH_METHOD=oauth` for HIPAA‑aligned auth; set `SINCH_AUTH_BASE_URL` for your region if needed
- [ ] Admin Console → Settings → Backend: `sinch`
- [ ] Inbound (optional): configure provider to `POST /sinch-inbound` and enable Basic auth (`SINCH_INBOUND_BASIC_USER`, `SINCH_INBOUND_BASIC_PASS`)
- [ ] Set `API_KEY` and ensure clients send `X-API-Key`
- [ ] `PUBLIC_API_URL` set for Admin links and inbound flows

!!! tip "Where to find keys"
    Use the Sinch Customer (Build) Dashboard: [dashboard.sinch.com/settings/access-keys](https://dashboard.sinch.com/settings/access-keys). Other Sinch portals may not show Fax API access keys.

## Webhooks

- Outbound status: mapped from send response today; additional callbacks may be added later
- Inbound receiving (optional): `POST /sinch-inbound`
- Verification: Basic auth (set `SINCH_INBOUND_BASIC_USER/PASS`) and use IP allowlists at your edge

Helpful docs
- [Sinch Fax API — Reference](https://developers.sinch.com/docs/fax/api-reference/)

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
- 401 from provider → verify Project ID and key/secret; check region and auth method
- Inbound rejected → ensure Basic auth credentials set and applied at your endpoint; prefer `application/json` payloads

!!! warning "HIPAA posture"
    Prefer OAuth (`SINCH_AUTH_METHOD=oauth`) and ensure your ingress is HTTPS with strict TLS. Review [HIPAA Requirements](/HIPAA_REQUIREMENTS/).
