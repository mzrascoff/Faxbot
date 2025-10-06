---
title: SignalWire Go‑Live Checklist
---

# SignalWire Go‑Live Checklist

SignalWire’s Compatibility (Twilio‑style) Fax API is supported for outbound sending. Faxbot hosts tokenized media for provider fetch and receives status callbacks. Inbound delivery is supported via the Plugin Manager (manifest providers) — install a SignalWire inbound plugin to enable full inbound flows.

## Pre‑flight

- [ ] SignalWire Space URL (e.g., `example.signalwire.com`)
- [ ] SignalWire Project ID and API Token
- [ ] Optional From number (`SIGNALWIRE_FAX_FROM_E164`)
- [ ] Admin Console → Settings → Backend: `signalwire`
- [ ] `PUBLIC_API_URL` points to an HTTPS host reachable by SignalWire
- [ ] Status callback configured to `<PUBLIC_API_URL>/signalwire-callback`
- [ ] Inbound: after installing the SignalWire inbound plugin, copy the inbound webhook URL from Admin → Inbound and register it in your SignalWire console
- [ ] Set `API_KEY` and ensure clients send `X-API-Key`

!!! tip "Quick tunnels for evaluation"
    Use Admin Console → Tools → Tunnels to create a temporary public URL (non‑HIPAA) and set `PUBLIC_API_URL`. Replace with a permanent domain for production.

## Webhooks

- Outbound status: `POST /signalwire-callback`
- Inbound: plugin‑defined webhook path shown in Admin → Inbound after installation

Helpful docs
- [SignalWire — Fax](https://developer.signalwire.com/fax)
- [SignalWire — Compatibility API](https://developer.signalwire.com/compatibility-api)

## Smoke tests

Send a test fax via Faxbot

```bash
curl -sS -X POST "$PUBLIC_API_URL/fax" \
  -H "X-API-Key: ${API_KEY:?}" \
  -F "to=+15551234567" \
  -F "file=@README.md" | jq .
```

## Troubleshooting

- Callback not received → verify `PUBLIC_API_URL` is HTTPS and reachable; confirm `<PUBLIC_API_URL>/signalwire-callback` is set
- 415 / file errors → only PDF/TXT are accepted; convert images to PDF first
- Inbound not delivering → ensure the SignalWire inbound plugin is installed/enabled and that you registered the exact inbound URL shown in Admin → Inbound

!!! warning "HIPAA posture"
    Do not use quick tunnels for PHI. Use a permanent HTTPS domain and follow [HIPAA Requirements](/HIPAA_REQUIREMENTS/).

See also
- [Plugin Builder](/admin-console/plugin-builder/)
