---
title: API Keys
---

# API Keys

Create scoped API keys for apps and integrations.

## Create a key

1) Open Admin → API Keys
2) Click “Create key” and choose scopes (e.g., `fax:send`, `fax:read`)
3) Copy the generated token (`fbk_live_<id>_<secret>`) — it’s shown once

!!! tip "Scopes"
    Use least‑privilege: sending apps need `fax:send`; dashboards often need `fax:read` only.

## Use in requests

```bash
curl -H "X-API-Key: fbk_live_..." "$PUBLIC_API_URL/fax/{id}"
```

## Rotate and revoke

- Rotate keys periodically and revoke unused ones
- Jobs remain readable if the user/account retains access

