# Faxbot Auto‑Tunneling — Current State and Revised Plan (v1.4)

This document reflects the code now in the repo and aligns with AGENTS.md: Admin Console first, backend isolation, HIPAA‑safe defaults, and no CLI‑only features. Tunnels serve two audiences: non‑HIPAA users who want external access (Admin Console and webhooks) and HIPAA users who require private/VPN access only.

## 0) Big Picture (Strategy)

- Purpose of tunnels
  - Provide secure remote reachability for Admin Console and the iOS companion app when direct LAN access is unavailable.
  - Not for telephony media (SIP/UDPTL/T.38) and not a substitute for TLS/WAF in production.
- Architectural boundaries
  - The API does not orchestrate host/container lifecycles. It surfaces status, runs safe checks, and persists config — nothing more.
  - Admin Console is the primary UX; every setting includes inline help and a Learn more link (built from `docsBase`).
- Compliance defaults
  - HIPAA posture disables Cloudflare Quick Tunnel and hides any public URLs. WireGuard/Tailscale are the HIPAA‑capable options.
  - No PHI or secrets in logs; show only minimal identifiers (last 4 if applicable).
- Target state
  - Persisted, scoped tunnel configuration; backend‑isolated UX; reliable status; WireGuard QR + .conf upload/download; solid docs; optional compose helpers for ops.

## 1) Current Reality (as implemented)

Server (FastAPI)
- Admin‑only endpoints (`api/app/main.py`):
  - `GET /admin/tunnel/status` → returns in‑memory status; hides Cloudflare URL in HIPAA posture; dev‑only auto‑detects Quick Tunnel from logs.
  - `POST /admin/tunnel/config` → updates in‑memory provider selection.
  - `POST /admin/tunnel/test` → probes active public URL (tunnel if present) or localhost `/health`.
  - `POST /admin/tunnel/pair` → returns a short‑lived numeric code (no pairing QR — by design).
  - `POST /admin/tunnel/register-sinch` → sets Sinch incoming fax webhook to `{public_base}/sinch-inbound` when inbound=sinch.
  - WireGuard admin:
    - `POST /admin/tunnel/wg/import` (size‑capped, validates `[Interface]/PrivateKey` + `[Peer]`), stores at `WIREGUARD_CONF_PATH` (mode 600)
    - `GET /admin/tunnel/wg/conf` (download), `DELETE /admin/tunnel/wg/conf` (delete)
    - `POST /admin/tunnel/wg/qr` returns `svg_base64` (SVG‑only via segno)
- Cloudflared logs API:
  - `GET /admin/tunnel/cloudflared/logs` reads the mounted logfile (no shell exec).
- HIPAA posture logic:
  - When HIPAA posture is active, Cloudflare Quick Tunnel is disabled and its public URL is not surfaced.
- Admin UI tunnel access:
  - Admin Console is local‑only by default. Set `ADMIN_UI_ALLOW_TUNNEL=true` to allow access via a tunnel for demos/tests (non‑HIPAA only).

Admin Console (Vite/React/MUI)
- Tools → “Tunnels” panel:
  - Provider select: none | cloudflare | wireguard | tailscale (Cloudflare disabled in HIPAA mode).
  - “Save & Apply” persists provider (`PUT /admin/settings`) and applies runtime config (`/admin/tunnel/config`).
  - “Test Connectivity” (`/admin/tunnel/test`).
  - “Generate iOS Pairing Code” (`/admin/tunnel/pair`).
  - “Register with Sinch” shown only when inbound=sinch and creds exist; calls `/admin/tunnel/register-sinch`.
  - “View Cloudflared Logs” calls `GET /admin/tunnel/cloudflared/logs`.
- Setup Wizard now loads `/admin/settings` at mount and initializes from effective outbound/inbound (no Phaxio hard‑default). Apply sets backend=outbound to avoid mismatched UX.

Compose / Runtime
- `docker-compose.yml` includes a Cloudflared sidecar under the `cloudflare` profile; logs are written to `./cloudflared-logs/cloudflared.log` and mounted into the API as `/faxdata/cloudflared/cloudflared.log`.
- The API never shells out to Docker and does not orchestrate third‑party clients.

Security / HIPAA
- Admin endpoints require admin auth (bootstrap env API_KEY or DB key with `keys:manage`).
- Cloudflare Quick Tunnel public URL is hidden and blocked in HIPAA posture.

## 2) Known Gaps and Risks (Delta to Target)

- Admin Actions: keep only “safe checks.” No start/stop orchestration. Logs are served via API.
- Compose: Cloudflared sidecar present; WireGuard/Tailscale orchestration remains out of scope.
- Pairing UX: Numeric code only (intentional). WireGuard QR is separate and implemented.

Non‑goals (explicit)
- Auto‑downloading or installing third‑party binaries from inside the API.
- Embedding long‑running tunnel clients inside the API process.
- Exposing Admin Actions that can mutate the host outside a controlled, local‑only environment.

## 3) Revised Plan (phased)

P0 — Stabilize and align with the shipped code
- Persistence
  - Persist `TUNNEL_PROVIDER` via `/admin/settings` and `.env` export/persist (done)
- Cloudflare discovery
  - Dev‑only log parse of Cloudflared sidecar logs to detect/set public URL (disabled under HIPAA) (done)
  - Replace Admin Action tail with `GET /admin/tunnel/cloudflared/logs` (done)
- WireGuard
  - `.conf` upload, size cap 64 KB, validate `[Interface]` + `PrivateKey` + `[Peer]` (done)
  - Store at `WIREGUARD_CONF_PATH` with mode 600 (done)
  - “Show QR” returns SVG (only) via segno; no secrets in logs (done)
- Admin UI
  - Tunnels panel wired to new endpoints with inline Alerts and docs link.
  - Setup Wizard initializes from `/admin/settings`; apply sets backend=outbound to avoid “stuck to Phaxio.”

P1 — Nice‑to‑haves
- Add small “last checked” timestamp + refresh in status chip.
- Cache QR generation for repeated views (server‑side small TTL).
- Tighten OpenAPI/types across Admin UI (remove remaining `any`).

Docs
- Add/update tunnels overview with Cloudflared sidecar profile and HIPAA guardrails.
- WireGuard: document importing a device `.conf` (e.g., Firewalla) and scanning SVG QR.
- Emphasize Admin Console local‑only by default; for demos/tests, `ADMIN_UI_ALLOW_TUNNEL=true` (non‑HIPAA only). Never expose `/admin/terminal` externally.

QA/Validation
- Verify HIPAA posture with `ENFORCE_PUBLIC_HTTPS=true` (Cloudflare disabled/hidden URL).
- Verify error mapping (400/401/404/413/415) across the new/gated endpoints.

## 9) QR Output Format Notes (SVG‑only)

- SVG via `segno` is the single output path. No native deps required in the container. UI consumes `svg_base64`.

## 10) Reference Blueprint: Scrypted

- Self‑hosted, Docker‑based platform with an iOS app and Electron desktop shell.
- Uses tunnels for external access; Cloudflare changes are handled seamlessly without user intervention.
- Parallels: Admin Console‑first UX, tunnel‑based connectivity, multiple runtimes (Electron/iOS), backend isolation.

## 11) Must Change (P0 blockers)

- Backend isolation for Sinch registration — done
- Remove unsafe orchestration Admin Actions — done (use log API)
- WireGuard hardening — done (caps/validation/no path echo)
- SVG‑only QR — done
- Setup Wizard fixes — done (load effective backends; backend=outbound on apply)

## 12) Nits (polish, not blockers)

- Inline helper copy and Learn more links on every control per AGENTS.md.
- Consider status timestamp/refresh chip.
- Align Admin UI types with OpenAPI.

## 13) CTO Alpha Test Readiness

- Preconditions
  - Non‑HIPAA dev profile with Cloudflared sidecar.
  - Admin UI allowed through tunnel for demo (`ADMIN_UI_ALLOW_TUNNEL=true`), or use WireGuard.

- What “just works” for Cloudflare (non‑HIPAA)
  - Start `api` + `cloudflared` (compose profile). The API auto‑detects the issued `https://*.trycloudflare.com` and sets it in runtime (no pasting) when allowed.
  - Tunnels panel shows “Connected via public URL.” Webhooks and Admin Console are reachable via that URL.

- HIPAA posture
  - Cloudflare option disabled and hidden; WG/Tailscale recommended; `PUBLIC_API_URL` should be your TLS endpoint.

- Smoke script for CTO
  1) Admin Console login (env API_KEY or DB key with `keys:manage`).
  2) Cloudflare: Tunnels → Cloudflare; Test Connectivity OK; view logs.
  3) WireGuard: upload `.conf`, Show QR (SVG), Download, Delete.
  4) HIPAA: enable `ENFORCE_PUBLIC_HTTPS=true`; verify Cloudflare disabled; WG QR still works.
  5) Sinch: only when inbound=sinch and creds present; test Register button.

- Known rough edges (alpha)
  - No global notifications yet; inline Alerts used.

## 14) Plan Update Discipline (Process)

- Re‑read this plan before starting work and before merging. Update when:
  - Scope changes (e.g., SVG‑only decision),
  - New endpoints/UX land (e.g., WG QR, Sinch gating),
  - Readiness gates are met (e.g., CTO Alpha Test Readiness).

