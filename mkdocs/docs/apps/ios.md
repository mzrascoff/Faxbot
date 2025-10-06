---
title: iOS App
---

# iOS App

Pair your device with Faxbot to view Inbox and receive notifications.

## Pairing

1) Ensure your server is reachable from the device (named tunnel or domain)
2) Admin → Mobile Pairing → Generate code (or QR)
3) In the iOS app, enter the code (or scan the QR)
4) The app exchanges the code for a short‑lived token and the best base URL

!!! tip "Tunnels"
    For off‑LAN access, use a HIPAA‑capable tunnel (WireGuard/Tailscale). Avoid quick tunnels for PHI.

## Troubleshooting

- Code expired → generate a new one
- Cannot connect → verify the tunnel/domain is reachable over HTTPS from your device
- Inbox empty → verify inbound provider and webhooks are configured

See also
- [Networking & Tunnels](/networking/tunnels/)
- [Inbound & Webhooks](/setup/webhooks/)

