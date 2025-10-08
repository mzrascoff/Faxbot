
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

---

## HTTP Manifest: End‑to‑End Flow

This section captures the complete lifecycle from JSON → validation → install → activation → runtime.

1) Prepare JSON manifest (see [HTTP Manifest Providers](../plugins/manifest-http.md))  
   Schema and runtime live at `api/app/plugins/http_provider.py` (71‑102, 111‑139, 167‑238, 275‑304).
2) Validate in Console  
   Plugins → “HTTP Manifest Tester” → Validate (client calls `POST /admin/plugins/http/validate`)  
   Code: api/admin_ui/src/api/client.ts:623; server: api/app/main.py:2556, 2570‑2579, 2583‑2588.
3) Dry‑run send (optional)  
   Same endpoint with `render_only:false` uses the runtime to normalize a send.
4) Install  
   “Install” writes `config/providers/<id>/manifest.json` (client: api/admin_ui/src/api/client.ts:631; server: api/app/main.py:2530‑2538).  
   Diagnostics enumerate installed manifests and basic issues (api/app/main.py:3714, 3721‑3756).
5) Activate as outbound backend  
   Set `FEATURE_V3_PLUGINS=true` and `OUTBOUND_BACKEND=<id>` (or legacy `FAX_BACKEND=<id>`).  
   Alternatively, PUT `/plugins/{id}/config` (api/app/main.py:6288‑6323). Note: persists only; restart to apply (api/app/main.py:6322).
6) Runtime send path  
   `POST /fax` → manifest path computed and, when present, dispatches via `_send_via_manifest` (api/app/main.py:4086, 4093‑4153, 5045‑5090).
7) Status refresh (optional)  
   `POST /admin/fax-jobs/{job_id}/refresh` polls `get_status` if defined and updates DB (api/app/main.py:3496‑3608).

RAG tip: Use the MCP RAG tools to quickly locate endpoints and paths (e.g., “where is validate endpoint?”). See the rag‑service docs for setup.

