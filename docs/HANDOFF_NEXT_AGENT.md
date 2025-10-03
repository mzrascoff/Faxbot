Insanely Detailed Handoff — Sinch Outbound, HumbleFax Inbound, iOS Pairing, Diagnostics (auto-tunnel)

Scope
- Branch: auto-tunnel (per branch policy, do NOT push to main)
- Goal: End‑to‑end send via Sinch; inbound via HumbleFax; iOS app pairing autofill; diagnostics visibility

What I changed

Backend (API)
- Sinch diagnostics endpoint
  - File: api/app/main.py:1931
  - GET /admin/diagnostics/sinch → { dns_ok, auth_present, auth_ok, path_ok, probes }
  - Helps separate DNS vs. auth vs. path (/v3) issues.

- iOS mobile pairing flow
  - File: api/app/main.py:2008
  - POST /mobile/pair accepts { code, device_name? } and returns { base_urls, token }
  - Accepts any code when ENABLE_LOCAL_ADMIN=true (dev); 
    if MOBILE_PAIRING_CODE is set, it must match.
  - base_urls.tunnel derives from active Cloudflare tunnel or HUMBLEFAX_CALLBACK_BASE; public from PUBLIC_API_URL.
  - Issues a scoped API key with scopes: inbound:list, inbound:read, fax:send.

- Sinch service + provider adapter (previous step)
  - Adds /v3 fallbacks universally and two-step upload+send with multipart fallback.
  - OUTCOME: Real fax send → success with provider_sid.

Admin UI (React)
- Tunnel page: iOS pairing + diagnostics
  - File: api/admin_ui/src/components/TunnelSettings.tsx
  - “Generate iOS Pairing Code” button (already existed) shows code dialog.
  - “Run Sinch Diagnostics” button shows JSON of /admin/diagnostics/sinch.
  - Cloudflared logs view remains.

- API client additions
  - File: api/admin_ui/src/api/client.ts
  - Added getSinchDiagnostics() and existing methods createTunnelPairing(), registerHumbleFaxWebhook(), etc.

iOS App (FaxbotApp)
- Pairing autofill fix
  - File: /Users/davidmontgomery/faxbot_folder/faxbot_app/ios/FaxbotApp/Sources/Faxbot/APIClient.swift
  - After redeemPairing, force‑clear localURL when a tunnel/public base is returned so bestBaseURL uses the remote.
  - This prevents 127.0.0.1 default from shadowing the tunnel on device builds.

What works now
- Outbound Sinch
  - Real sends complete; job transitions from in_progress → success.
  - Diagnostics show path_ok true when /v3 project‑scoped is used.

- iOS pairing autofill
  - Admin Console → Tunnels → “Generate iOS Pairing Code” to produce a one‑time code.
  - On device: Settings tab → Pairing → enter code (or scan). App calls /mobile/pair, receives base URLs + mobile token; localURL is cleared; tunnel/public retained; Inbox works.

- Inbound storage + secure PDF serving
  - /inbound/{id}/pdf validates token or X‑API‑Key with inbound:read scope.

What is still blocked
- HumbleFax webhook registration
  - Error “Invalid webhook url.” Root cause: public URL (trycloudflare) is unstable/unresolvable from providers at this time.
  - Cloudflared logs show frequent quic timeouts/no recent network activity.
  - Once a stable HTTPS base is reachable (named tunnel or a real domain), POST /admin/inbound/register-humblefax succeeds; Inbound downloader (already wired) will store PDFs on IncomingFax.*.

How to operate
1) Stack up
   - docker compose --profile cloudflare up -d --build api cloudflared
   - curl http://localhost:8080/health → {"status":"ok"}

2) Run Sinch diagnostics
   - curl -H 'X-API-Key: fbk_live_local_admin' http://localhost:8080/admin/diagnostics/sinch
   - UI: Tunnels → “Run Sinch Diagnostics”

3) Send fax (real)
   - curl -X POST 'http://localhost:8080/fax' -H 'X-API-Key: fbk_live_local_admin' -F to='+1XXXXXXXXXX' -F file=@test.pdf
   - curl 'http://localhost:8080/fax/{job_id}?refresh=true' until success or fail.

4) Pair iOS app
   - Admin Console → Tools → Tunnels → “Generate iOS Pairing Code”
   - On device: Settings → Pairing → enter code. App updates base URLs and token automatically.

5) Inbound (HumbleFax)
   - Ensure public HTTPS base is stable. Then: curl -H 'X-API-Key:…' -X POST http://localhost:8080/admin/inbound/register-humblefax
   - When active, IncomingFax.* triggers background download; Inbox shows real documents.

Key files touched
- api/app/main.py (diagnostics + pairing)
- api/admin_ui/src/components/TunnelSettings.tsx (UI buttons + diag panel)
- api/admin_ui/src/api/client.ts (client helpers)
- /Users/davidmontgomery/faxbot_folder/faxbot_app/ios/FaxbotApp/Sources/Faxbot/APIClient.swift (clear local URL on pairing)

Security/Compliance
- No PHI in logs; pairing code contains no secrets; mobile keys are scoped.
- Cloudflare quick tunnel should remain disabled in HIPAA posture.

Next suggested work (Yes to all if you want me to proceed)
1) Stabilize public base
   - Use a named Cloudflare Tunnel with a custom domain (preferred) or a real HTTPS domain on your reverse proxy. Update PUBLIC_API_URL.
   - Re-run HumbleFax registration.

2) HumbleFax diagnostics endpoint
   - Add /admin/diagnostics/humblefax to test reachability (auth, webhook POST dry-run) and present provider guidance.

3) Admin UI: “Mobile Pairing” card
   - Dedicated card with QR rendering of numeric pairing code (app already supports Scan QR). Current dialog shows code only.

4) Optional: prefer tunnel automatically in iOS Release builds
   - Update bestBaseURL to prefer tunnel when set, or gate isOnLAN=false on Release.

Branch policy note
- Per AGENTS.md, all v4 work remains on `auto-tunnel`. Open a PR to `development` after green CI; never push directly to `main`.

Troubleshooting quick refs
- Sinch path
  - Unversioned endpoints may 404; /v3 project-scoped responds 200. Client auto-falls back.
- HumbleFax 400 “Invalid webhook url”
  - Due to provider validation when your URL is unstable/not resolvable. Fix the public base, then retry.

End of handoff.

