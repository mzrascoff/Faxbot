Agent Handoff — Sinch Outbound, HumbleFax Inbound, iOS Pairing QR, Diagnostics, Next‑Phase Roadmap (max compute)

Audience: Next engineering agent
Priority: High (end‑to‑end mobile + admin polish, all backends)

Environment and repos
- Faxbot API/Admin UI repo (this repo)
  - CWD: /Users/davidmontgomery/faxbot_folder/faxbot
  - Branch used for all work here: auto-tunnel
- Faxbot iOS app repo
  - CWD: /Users/davidmontgomery/faxbot_folder/faxbot_app
  - Branch pushed: developmenet (intentionally misspelled dev)

Important branch policy
- For v4 work in the Faxbot API/Admin UI repo, stay on auto-tunnel. Open PR → development only after green CI. Do not push to main.
- For iOS repo, changes were pushed to the misspelled dev branch developmenet, per request. Do not correct spelling yet.

What I did (every change, with full paths)

1) Outbound Sinch (end‑to‑end, success on real fax)
- Faxbot API (logic)
  - File: api/app/sinch_service.py (auto-tunnel)
    - Added robust /v3 fallbacks and “base variants” to try unversioned and /v3 paths.
    - Ensured upload_file, send_fax, get_fax_status, send_fax_file try project‑scoped and unscoped endpoints.
  - File: api/app/providers/outbound.py (auto-tunnel)
    - Switched SinchAdapter to prefer two‑step upload+send with multipart fallback.
    - Preserves surfacing provider error text to job.error.
- Result: Real fax send succeeded; job moved to success; provider_sid filled; validator shows path_ok via /v3 project scopes.

2) Inbound HumbleFax (webhook handler + downloader)
- Faxbot API (already present; I validated behavior)
  - File: api/app/main.py (auto-tunnel)
    - /inbound/humblefax/webhook: idempotent 202; optional HMAC; on IncomingFax.* it queues background download that stores PDF via storage adapter; Inbox showing works when webhook is registered.
  - One‑click registration endpoint exists but currently fails because provider rejects unstable URL (“Invalid webhook url”).
- Current blocker: Cloudflare quick tunnel is unstable (QUIC timeouts). Use a stable HTTPS host (named tunnel or PUBLIC_API_URL) before retrying registration.

3) Diagnostics (Sinch)
- Faxbot API
  - File: api/app/main.py:1931 (auto-tunnel)
    - GET /admin/diagnostics/sinch returns JSON with dns_ok, auth_present, auth_ok, path_ok, probes with exact URLs/status codes.
- Admin UI
  - File: api/admin_ui/src/components/TunnelSettings.tsx (auto-tunnel)
    - Added “Run Sinch Diagnostics” button; renders JSON result.
  - File: api/admin_ui/src/api/client.ts (auto-tunnel)
    - Added getSinchDiagnostics().

4) Mobile pairing autofill (iOS)
- Faxbot API
  - File: api/app/main.py:2008 (auto-tunnel)
    - POST /mobile/pair accepts { code, device_name? }.
      - In dev (ENABLE_LOCAL_ADMIN=true), accepts any code; if MOBILE_PAIRING_CODE is set, it must match.
      - Returns { base_urls: { local, tunnel, public }, token } where tunnel prefers active quick-tunnel or HUMBLEFAX_CALLBACK_BASE fallback; public uses PUBLIC_API_URL.
      - Issues a scoped API key (inbound:list, inbound:read, fax:send) and returns the token.
- Admin UI (pairing)
  - File: api/admin_ui/src/components/TunnelSettings.tsx (auto-tunnel)
    - Existing “Generate iOS Pairing Code” uses /admin/tunnel/pair for short code.
    - I added QR code rendering of that numeric code so iOS can Scan QR (no secrets in the QR). Uses a simple dev QR image URL (api.qrserver.com) to avoid new npm deps.
- iOS app repo (actual pairing fix)
  - File: /Users/davidmontgomery/faxbot_folder/faxbot_app/ios/FaxbotApp/Sources/Faxbot/APIClient.swift (developmenet)
    - After redeemPairing(), if a tunnel/public base exists, force‑clear localURL so bestBaseURL uses remote (not 127.0.0.1). This makes Inbox and PDF downloads hit the server from a device build.
  - Branch + push: developmenet (misspelled dev) at /Users/davidmontgomery/faxbot_folder/faxbot_app
    - Cherry‑picked onto developmenet and pushed to origin/developmenet.

5) Admin UI (QR for pairing)
- File: api/admin_ui/src/components/TunnelSettings.tsx (auto-tunnel)
  - Pairing dialog now shows both the numeric code and a QR image (generated via https://api.qrserver.com/v1/create-qr-code/?data=CODE). The code is short‑lived and contains no secrets.
  - Note: If you later want full offline QR, we can add a small in‑repo QR generator or a server endpoint.

6) Handoff documentation
- File: docs/HANDOFF_NEXT_AGENT.md (auto-tunnel)
  - A compact handoff with what changed, files, usage, and next steps.

How to use (today)
1) Stack up
   - docker compose --profile cloudflare up -d --build api cloudflared
   - curl http://localhost:8080/health → {"status":"ok"}

2) Pair iOS
   - Admin Console → Tools → Tunnels → “Generate iOS Pairing Code” (shows code + QR).
   - On device (TestFlight build 12): Settings → Pairing → enter code or Scan QR.
   - App receives base URLs + token via /mobile/pair; it clears localURL and stores the remote base + token. Inbox should populate.

3) Diagnostics
   - UI: “Run Sinch Diagnostics” on Tunnels page.
   - API: curl -H 'X-API-Key: fbk_live_local_admin' http://localhost:8080/admin/diagnostics/sinch

4) HumbleFax registration (webhook)
   - Use a stable HTTPS host (named Cloudflare Tunnel or real domain set as PUBLIC_API_URL).
   - Click “Register HumbleFax Webhook” (Tunnel page) or POST /admin/inbound/register-humblefax.
   - Then IncomingFax.* events will be auto‑downloaded and Inbox shows real documents.

Known issues and blockers
- HumbleFax rejects unstable quick‑tunnel URLs during webhook validation (“Invalid webhook url”). Cloudflared logs show QUIC timeouts/no recent activity. Solution: stabilize public base before retrying.
- iOS History uses local only (FaxHistory). It updates when send succeeds and during status polling. If users don’t see updates, ensure /fax/{id}?refresh=true is called and the token is set from pairing.

Next: unify UI with all backends (plugin/traits‑first)

Goals
1) Combine the most up‑to‑date Admin UI with the latest backend logic to fully support all outbound/inbound providers:
   - Providers: Sinch, Phaxio, HumbleFax, SignalWire, SIP/Asterisk, FreeSWITCH, Test
   - Traits first; do not key on provider names. Gate UI sections via traits.

2) Make Inbox and History consistently populated across backends
   - Inbox: relies on real InboundFax rows (webhooks or manual ingest). For cloud providers, ensure webhook registration + downloader exists.
   - History: iOS History is local; Admin Jobs page shows server job rows. Ensure polling paths exist and UI calls refresh endpoints.

Implementation outline
1) Traits‑gated UI coverage
   - Files in Admin UI: api/admin_ui/src/components/Settings.tsx, ProviderSetupWizard.tsx, TunnelSettings.tsx
   - Use useTraits() consistently to show only active provider settings. Avoid string checks like provider === 'sinch'.
   - Add per‑provider sections based on canonical trait keys (see config/provider_traits.json).

2) Outbound support (all providers)
   - Ensure get_outbound_adapter() (api/app/providers/outbound.py) returns adapters for all configured backends.
   - Converge send flows to _send_via_outbound_normalized(); surface provider errors to job.error.
   - Keep status mapping via config/provider_status_map.json.

3) Inbound support (show in Inbox)
   - For each provider with inbound webhooks (HumbleFax, Phaxio, Sinch, SignalWire when applicable), ensure:
     - Dedicated /inbound/<provider> webhook returns 202 and is idempotent.
     - A best‑effort downloader stores inbound PDFs via storage adapter (local/S3) to create InboundFax rows.
   - UI Inbox (Admin) should call GET /inbound and render items; iOS app uses /inbound on the server the phone is paired to.

4) iOS app — Inbox and History reliability
   - Inbox: With pairing applied and localURL cleared, listInbound() calls `/inbound` with X‑API‑Key. Verify scopes inbound:list and inbound:read are set.
   - PDF open: `/inbound/{id}/pdf` requires the same key and returns 200.
   - History: On send, append job to FaxHistory; poll via `/fax/{id}` and `/fax/{id}?refresh=true` to update status. Ensure app persists the token and uses it consistently.

5) Docs updates (mddocs branch)
   - Repository: /Users/davidmontgomery/faxbot_folder/faxbot (unless you have a separate docs repo, adjust accordingly)
   - Branch: mddocs
   - Update: everything that changed in the last 24 hours:
     - New endpoints: `/admin/diagnostics/sinch`, `/mobile/pair`
     - Sinch client behavior: /v3 fallback paths, two‑step upload+send
     - Admin UI Tunnels page changes: “Run Sinch Diagnostics”, iOS Pairing QR
     - HumbleFax webhook + download flow; requirement for stable PUBLIC_API_URL
     - iOS pairing flow and required scopes; how to clear localURL and prefer remote base
   - Suggested structure:
     - docs/diagnostics.md (new)
     - docs/mobile-pairing.md (new)
     - docs/providers/sinch.md (update)
     - docs/providers/humblefax.md (update)
     - docs/admin-ui/tunnels.md (update)

6) Testing plan (post‑merge)
   - Sinch: validate settings; send; ensure success; diagnostic shows ok.
   - HumbleFax: once public base is stable, register webhook; send an inbound fax; verify Inbox row + PDF download.
   - iOS app: pair; confirm Inbox shows records; open PDF; send a test fax; History updates after polling.

Warnings and constraints
- Very large effort ahead: unify UI + logic across 7 providers, ensure inbound downloaders exist, and polish Admin UI gating. Expect long cycles.
- Use max compute / high‑juice thinking; break the work into verifiable milestones and keep PRs narrowly scoped.

Concrete next tasks
1) Stabilize public base URL
   - Configure a named Cloudflare Tunnel or a proper domain; set `PUBLIC_API_URL` in /Users/davidmontgomery/faxbot_folder/faxbot/.env.
   - Retry POST /admin/inbound/register-humblefax.

2) Add HumbleFax diagnostics
   - API: GET /admin/diagnostics/humblefax → dns_ok, auth_ok, webhook_url_ok (HEAD), sample createWebhook dry‑run.
   - UI: Add a diagnostics card on Tunnels page (like Sinch) when inbound backend = humblefax.

3) Provider‑specific UI cleanup
   - Ensure Settings.tsx and ProviderSetupWizard.tsx only render sections for the active provider (traits‑gated).
   - Remove any string checks for provider names.

4) iOS QR polish (optional offline)
   - Replace external QR with an in‑repo TS utility or add a small npm QR lib + lockfile update; render as SVG.

5) Prepare PRs
   - Faxbot API/Admin UI: auto-tunnel → development; include docs/HANDOFF_NEXT_AGENT.md and internal_docs/HANDOFF_AGENT_QR_AND_ROADMAP.md.
   - iOS repo: confirm developmenet includes the pairing fix. Coordinate TestFlight update if needed.

Appendix A — Full paths touched
- Faxbot repo (auto-tunnel):
  - api/app/sinch_service.py
  - api/app/providers/outbound.py
  - api/app/main.py (diagnostics + pairing + existing inbound handlers)
  - api/admin_ui/src/components/TunnelSettings.tsx
  - api/admin_ui/src/api/client.ts
  - docs/HANDOFF_NEXT_AGENT.md
  - internal_docs/HANDOFF_AGENT_QR_AND_ROADMAP.md (this file)
- iOS repo (developmenet):
  - /Users/davidmontgomery/faxbot_folder/faxbot_app/ios/FaxbotApp/Sources/Faxbot/APIClient.swift

Appendix B — Minimal commands
- Run stack: `docker compose --profile cloudflare up -d --build api cloudflared`
- Diagnostics: `curl -H 'X-API-Key: fbk_live_local_admin' http://localhost:8080/admin/diagnostics/sinch`
- Pair iOS: Admin UI → Tunnels → Generate iOS Pairing Code; enter code in app
- Inbox simulate (dev): POST /admin/inbound/simulate

