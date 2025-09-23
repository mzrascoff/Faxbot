
# Curated Plugin Registry

The Plugins tab uses these discovery endpoints when `FEATURE_V3_PLUGINS=true`.

[:material-puzzle-outline: Plugins Overview](index.md){ .md-button }
[:material-http: HTTP Manifest Docs](manifest-http.md){ .md-button }
[:material-file-cog: Plugin Config File](config-file.md){ .md-button }
[:material-puzzle: Plugin Builder](../admin-console/plugin-builder.md){ .md-button }

---

## Endpoints (admin scope required)

:material-puzzle: `GET /plugins`
: List installed plugins with manifests and current enabled/config values

:material-cog: `GET /plugins/{id}/config`
: Return `enabled` and `settings` for a plugin

:material-content-save-cog: `PUT /plugins/{id}/config`
: Validate and persist via the JSON config store

:material-database-search: `GET /plugin-registry`
: Serve the curated registry JSON for UI search

---

## Config store

:material-file-cog: Path
: `FAXBOT_CONFIG_PATH` (default `config/faxbot.config.json`)

:material-content-save: Writes
: Atomic writes with `.bak` backups; roll back to last known‑good on validation/startup failure

---

## Security & permissions

:material-shield-key: Scopes
: `admin:plugins:read`, `admin:plugins:write`

:material-key: Who can write
: Only keys with `keys:manage` may change plugin configs

:material-speedometer: Rate limits
: Per‑key RPM: mirror inbound list/get defaults for reads (stricter for writes)

---

## Dynamic install (optional)

:material-toggle-switch-off: Default
: Keep `FEATURE_PLUGIN_INSTALL=false`

:material-shield-lock: When enabled
: Use a strict allowlist and checksums (signatures if provided); non‑interactive, sandboxed install only

:material-hospital: HIPAA
: Leave remote install disabled for HIPAA profiles

---

## Admin Console behavior

:material-view-grid-plus: Plugins tab
: Reads `/plugins` and renders schema‑driven forms

:material-filter-variant: Backend isolation
: Only the active outbound provider’s help is shown; switching providers is a guided flow (no mixed instructions)

---

## Notes

- Backends remain isolated across docs and UI; Phaxio users never see SIP/Asterisk instructions  
- Inbound cloud callbacks remain core HTTP endpoints that delegate to plugin handlers; HMAC/signature verification is enforced in core

---

## Troubleshooting

- `/plugins` returns 404 → enable `FEATURE_V3_PLUGINS=true` and restart the API  
- Config write errors → check permissions on `FAXBOT_CONFIG_PATH` (default lives under the `faxdata` volume)

---

## Quick examples

=== "Registry JSON"

```json
{
  "providers": [
    {
      "id": "phaxio",
      "name": "Phaxio (Cloud)",
      "type": "outbound",
      "version": "1.0.0",
      "manifest": {
        "actions": { "send_fax": { "method": "POST", "url": "https://api.phaxio.com/..." } },
        "allowed_domains": ["api.phaxio.com"]
      }
    }
  ]
}
```

=== "/plugins response"

```json
{
  "plugins": [
    {
      "id": "phaxio",
      "enabled": true,
      "settings": { "api_key": "***", "api_secret": "***" },
      "type": "outbound"
    }
  ]
}
```

=== "Enable plugin (curl)"

```bash
BASE="http://localhost:8080"
API_KEY="your_admin_api_key"
curl -sS -X PUT "$BASE/plugins/phaxio/config" \
  -H "X-API-Key: $API_KEY" -H 'content-type: application/json' \
  -d '{"enabled":true, "settings": {"api_key":"...","api_secret":"..."}}'
```
