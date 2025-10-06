---
title: SignalWire Setup (Compatibility API)
---

# SignalWire Setup (Compatibility API)

Outbound fax via SignalWire’s Compatibility (Twilio‑style) API. Inbound delivery is supported via the Plugin Manager (manifest providers), so you can enable full inbound flows when you install or upload a SignalWire inbound plugin.

!!! tip "Quick links"
    [SignalWire Fax](https://developer.signalwire.com/fax){ .md-button } [Compatibility API](https://developer.signalwire.com/compatibility-api){ .md-button } [Plugin Builder](/admin-console/plugin-builder/){ .md-button .md-button--primary }

## Steps

1) Collect credentials: Space URL (e.g., `example.signalwire.com`), Project ID, API Token
2) Admin Console → Setup Wizard → choose SignalWire
3) Enter values and optional `SIGNALWIRE_FAX_FROM_E164`
4) Set `PUBLIC_API_URL` (HTTPS) for tokenized media
5) Configure status callback to `<PUBLIC_API_URL>/signalwire-callback`
6) For inbound: install or upload a SignalWire inbound plugin in Admin → Plugins. The Admin Console will display the exact inbound webhook URL (copy‑to‑clipboard) for you to register in your SignalWire project.

Helpful links
- [SignalWire — Fax](https://developer.signalwire.com/fax)
- [Compatibility API](https://developer.signalwire.com/compatibility-api)

## Quick test (outbound)

```bash
curl -sS -X POST "$PUBLIC_API_URL/fax" \
  -H "X-API-Key: ${API_KEY:?}" \
  -F to=+15551234567 -F file=@README.md | jq .
```

## Inbound (via Plugin Manager)

- Use Admin → Plugin Builder (or Manifest Upload) to add an inbound provider for SignalWire. The inbound plugin defines the webhook path and verification method (e.g., HMAC or Basic auth) and surfaces the callback URL in Admin → Inbound.
- After installation, register the displayed inbound webhook URL in your SignalWire console. Validate delivery in Admin → Inbox.

Helpful link
- [Plugin Builder](/admin-console/plugin-builder/)

!!! warning "HIPAA posture"
    Use a permanent HTTPS domain and avoid quick tunnels for PHI. See [HIPAA Requirements](/HIPAA_REQUIREMENTS/).
