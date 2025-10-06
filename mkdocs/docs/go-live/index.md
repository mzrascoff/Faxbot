---
title: Go‑Live Checklists
---

# Go‑Live Checklists

Final readiness checklists for each backend profile. Each page is backend‑specific and includes provider help links, webhook guidance, and HIPAA notes where applicable.

!!! tip "Quick links"
    [:material-lan: Networking & Tunnels](/networking/tunnels/){ .md-button } [:material-webhook: Webhooks](/setup/webhooks/){ .md-button } [:material-cog: Setup Wizard](/admin-console/setup-wizard/){ .md-button .md-button--primary }

!!! note "Tip"
    Use search [:material-magnify:] with <kbd>Ctrl</kbd>+<kbd>K</kbd> (or <kbd>⌘</kbd>+<kbd>K</kbd>) to jump between providers and guides quickly.

## Providers

- [Phaxio](phaxio/)
- [Sinch](sinch/)
- [SignalWire](signalwire/)
- [Documo (mFax)](documo/)
- [HumbleFax](humblefax/)
- [SIP/Asterisk](sip-asterisk/)
- [FreeSWITCH](freeswitch/)

!!! tip "Auto‑tunnel and webhooks"
    Evaluating without a public domain? Use Admin Console → Tools → Tunnels to create a Cloudflare Quick Tunnel (non‑HIPAA) and auto‑detect your public URL. Then set `PUBLIC_API_URL` and register webhooks (where supported) for your selected provider.

!!! warning "HIPAA posture"
    For HIPAA workloads, avoid quick tunnels. Use a secure tunnel like WireGuard or Tailscale, ensure HTTPS termination, disable provider document retention, and execute a BAA with the provider. See [HIPAA Requirements](/HIPAA_REQUIREMENTS/).

## Print‑ready one‑pagers

- [Phaxio — One‑Pager](phaxio-onepager/)
- [Sinch — One‑Pager](sinch-onepager/)
- [SIP/Asterisk — One‑Pager](sip-asterisk-onepager/)
- [HumbleFax — One‑Pager](humblefax-onepager/)
- [Documo — One‑Pager](documo-onepager/)

See also: [Networking & Tunnels](/networking/tunnels/) · [Webhooks](/setup/webhooks/) · [Admin Console Setup Wizard](/admin-console/setup-wizard/)
