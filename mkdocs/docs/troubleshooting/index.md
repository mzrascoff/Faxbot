---
title: Troubleshooting
---

# Troubleshooting

Common issues and quick fixes.

## Outbound

- 401 from API → set `API_KEY` and send `X-API-Key`
- 413 / 415 → adjust `MAX_FILE_SIZE_MB`; only PDF/TXT supported
- Callback not received → verify `<PUBLIC_API_URL>` (HTTPS) and correct callback path in provider console

## Inbound

- No inbound PDFs → confirm storage configured and webhook verification matches provider
- Sinch inbound 401 → ensure Basic auth credentials set and used
- Plugin inbound not delivering → verify plugin installed/enabled and URL registered

## Tunnels

- Quick tunnel unstable → use a named tunnel or domain for production
- Mobile pairing fails → ensure best base URL resolves on device

See also
- [Diagnostics](/admin-console/diagnostics/)
- [Networking & Tunnels](/networking/tunnels/)

