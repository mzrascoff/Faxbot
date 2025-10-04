---
layout: default
title: Mobile Pairing (iOS)
nav_order: 50
permalink: /apps/ios/pairing
---

# Mobile Pairing (iOS)

The iOS app pairs to your Faxbot server using a short numeric code. Pairing returns a scoped API key and base URLs so the app can reach your server.

Flow
1) Admin Console → Tools → Tunnels → Generate iOS Pairing Code
   - Shows the numeric code and a QR (no secrets) that expires quickly.
2) iOS app → Settings → Pairing
   - Enter the code or scan the QR. In dev (`ENABLE_LOCAL_ADMIN=true`), any code is accepted unless `MOBILE_PAIRING_CODE` is set.
3) Server returns:
   - `base_urls`: `{ local, tunnel, public }` – the app chooses a remote base when available.
   - `token`: API key with minimal scopes: `inbound:list`, `inbound:read`, `fax:send`.

API
- POST `/admin/tunnel/pair` (admin) → `{ code, expires_at }`
- POST `/mobile/pair` (no admin) → `{ base_urls, token }` (validates code; dev bypass available)

Environment
```
ENABLE_LOCAL_ADMIN=true            # dev only; bypasses code check unless MOBILE_PAIRING_CODE is set
# Optional fixed code (dev labs / demos)
MOBILE_PAIRING_CODE=123456
```

Security Notes
- Codes contain no secrets and expire rapidly.
- The returned token is scoped and can be revoked from Admin → Keys.
- In HIPAA mode, public/quick tunnel URLs are suppressed; prefer stable HTTPS (`PUBLIC_API_URL`) or HIPAA-capable VPN.

