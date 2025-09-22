# Faxbot Local‑Only Admin Console — Production‑Ready Plan (v1)

## Purpose
- Deliver a pragmatic, local‑only admin console that rides on the existing API.
- v1 goal: help operators do the basics without hand‑editing `.env`: keys, readiness/diagnostics, simple send, inbound view (when enabled).
- Keep it local‑only by default, safe to ship, and easy to implement incrementally.

## Architecture Overview (grounded in current code)

### Runtime Topology
- Serve the UI from the existing FastAPI app under `GET /admin/ui/*` as static files (`ENABLE_LOCAL_ADMIN=true`).
- Reuse existing endpoints: `/admin/api-keys`, `/admin/config`, `/admin/settings`, `/health`, `/fax`, `/fax/{id}`, and inbound endpoints.
- Local‑only by default: middleware 403‑blocks remote clients for `/admin/ui` unless explicitly allowed for demo (`ADMIN_UI_ALLOW_TUNNEL=true`).
- No extra ports in v1.

### Security Model
- Middleware blocks non‑loopback access for `/admin/ui`; tunnel access blocked unless `ADMIN_UI_ALLOW_TUNNEL=true` (demo only).
- UI uses an API key with `keys:manage` (or bootstrap `API_KEY`) and stores it locally for this browser session. All admin calls send `X-API-Key`.
- Strict headers on `/admin/*`; no PHI in UI.
- Terminal is local‑only and requires `ENABLE_LOCAL_ADMIN=true`.

### Settings Strategy
- Read with `/admin/settings` and `/admin/config`.
- Apply with `PUT /admin/settings` and `POST /admin/settings/reload`; export/persist via `/admin/settings/export` and `/admin/settings/persist`.
- Validate with `POST /admin/settings/validate` (provider/AMI checks).

### Events & Real‑Time
- Polling by default: dashboard polls `/health/ready`; jobs poll `GET /fax/{id}`.
- MCP transports (HTTP/SSE/WebSocket) optional for assistant integrations.

## Admin Endpoints (Summary)
- API Keys: create/list/rotate/revoke under `/admin/api-keys`.
- Settings: get/update/reload/validate under `/admin/settings`.
- Diagnostics: run bounded checks; surface remediation tips.

## Pages & Flows (v1)
- Dashboard: health, active backend, recent jobs, storage check; actions for Wizard/Send.
- Setup Wizard: choose backend → validate → security → review/apply.
- Send Fax: PDF/TXT picker, client size/type checks; submit to `POST /fax`; poll status.
- Jobs: filters and details; copy job id; re‑send; delete artifacts.
- Inbound Inbox (optional): list and secure PDF downloads.
- API Keys: list/create/rotate/revoke; token shown once.
- Diagnostics: provider ping, AMI connect, Ghostscript, storage, clock drift.
- About/Version: version/build/licensing.

## Components & UX
- Secret inputs masked; copy‑once behavior; re‑entry for changes.
- Accessible, responsive layouts; mobile tabs.
- No data retention in browser; no PHI in logs or UI.

## Security & Networking
- Keep `/admin/ui` local‑only; avoid exposing the Terminal via public tunnels.
- For HIPAA: enforce HTTPS, enable HMAC verification where supported, use audit logging per policy.

See also
- Security: security/index.md
- OAuth/OIDC Setup: security/oauth-setup.md
- Terminal: terminal.md
- Tunnels: networking/tunnels.md
