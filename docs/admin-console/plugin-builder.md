
# Plugin Builder

Generate a starter outbound plugin with a guided wizard — either code plugins or HTTP Manifest providers.

[:material-puzzle-outline: Plugins Overview](../plugins/index.md){ .md-button }
[:material-store-outline: Curated Registry](../plugins/registry.md){ .md-button }
[:material-http: HTTP Manifest Docs](../plugins/manifest-http.md){ .md-button }

---

## Where

:material-puzzle-outline: Location
: Admin Console → Plugins → “Build Plugin” (when enabled)

---

## What it creates

:material-language-python: Python plugin
: Extends `FaxPlugin` with `send_fax` and optional `get_status`.  
  Files: `providers/<id>/__init__.py`, `providers/<id>/plugin.py`  
  Registration snippet for the runtime

:material-nodejs: Node plugin
: Extends `FaxPlugin` with `sendFax`/`getStatus`.  
  Files: `providers/<id>/index.js` (or TS source), package metadata

:material-http: HTTP Manifest
: `config/providers/<id>/manifest.json` with `actions.send_fax` and optional `get_status`.  
  Includes allowed domains, auth scheme, headers, body templates, and response mapping

---

## How to use

1) Enter basics (name, id, version)  
2) Choose target (Python, Node, or HTTP Manifest)  
3) Configure settings schema (non‑secrets) and capability set (send, get_status)  
4) Review & Generate → download the source or manifest  
5) Place files in your workspace and enable via Admin Console → Plugins

---

## How it works (under the hood)

:material-file-code: Manifest runtime
: Executed in `api/app/plugins/http_provider.py`

:material-content-save-cog: Config store
: Console persists plugin enablement/settings via `PUT /plugins/{id}/config` using `api/app/plugins/config_store.py`

:material-send-check: Dispatch
: When a manifest provider is active, outbound send dispatches through the manifest runtime (see `api/app/main.py` for dispatch and discovery endpoints)

---

## Security model

:material-key: Secrets
: Provided via environment/Admin settings; manifests store no secrets

:material-domain: Allowed domains
: Every manifest must include `allowed_domains`; the runtime blocks other hosts

:material-shield-lock: Permissions
: Admin writes require `admin:plugins:write`; reads require `admin:plugins:read`

---

## Developer tips

- Keep provider‑specific docs separate; do not leak instructions across providers
- Add “Learn more” links for operators that point to minimal, focused pages
- For HIPAA, keep remote install disabled and commit manifests to source control

---

## References

- Plugins (v3): [Overview](../plugins/index.md)  
- Curated Registry: [Docs](../plugins/registry.md)  
- HTTP Manifest Providers: [Docs](../plugins/manifest-http.md)
