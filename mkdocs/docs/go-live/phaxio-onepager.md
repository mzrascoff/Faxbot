---
title: Phaxio Go‑Live — One‑Pager
---

# Phaxio Go‑Live — One‑Pager

Essentials for a clean Phaxio launch.

## Checklist

- [ ] `PHAXIO_API_KEY` and `PHAXIO_API_SECRET` set
- [ ] Admin Console → Backend: `phaxio`
- [ ] `PUBLIC_API_URL` (HTTPS) reachable from the internet
- [ ] Phaxio status callback → `<PUBLIC_API_URL>/phaxio-callback`
- [ ] `PHAXIO_VERIFY_SIGNATURE=true` (HMAC)
- [ ] `API_KEY` minted; clients send `X-API-Key`
- [ ] HIPAA: BAA executed; provider retention disabled

## Test

```bash
curl -sS -X POST "$PUBLIC_API_URL/fax" \
  -H "X-API-Key: ${API_KEY:?}" \
  -F to=+15551234567 -F file=@README.md | jq .
```

## Troubleshoot

- No callbacks → verify HTTPS and callback URL in Phaxio console
- Signature fail → check `PHAXIO_VERIFY_SIGNATURE` and secret
- 415 errors → only PDF/TXT accepted

## HIPAA checklist

- [ ] BAA executed with provider
- [ ] Provider document retention disabled
- [ ] HTTPS enforced end‑to‑end; strong TLS
- [ ] No PHI in logs; keys masked
- [ ] Keys rotated; least‑privilege access

## Help

- [Webhooks](https://www.phaxio.com/docs/api/v2.1/intro/webhooks)
- [Send webhooks](https://www.phaxio.com/docs/api/v2.1/faxes/send_webhooks)
- [Verify callbacks](https://www.phaxio.com/docs/security/callbacks)

!!! tip "Quick tunnel"
    For demos only: start a quick tunnel in Admin → Tools → Tunnels, then set `PUBLIC_API_URL`. Replace with a permanent domain for production.
