# Admin Console Precise Link-Building Prompt (Docs Anchors + JSON Maps)

Objective
- Generate exhaustive, precise, deep-linked help anchors and JSON maps for every screen, control, diagnostic, test, script, and flow in the Faxbot Admin Console (web/Electron). The result must let a user click from any inline help or Diagnostics item directly to the exact place in our docs that answers their question with minimal scrolling.

Your mandate
- Do not summarize. Create concrete page anchors and JSON maps so the UI can link precisely.
- Leave no screen or control without targeted help. If UI renders a help button, tooltip, or “Learn more” link, it must point to a stable anchor that loads the correct section and highlights it.
- Providers are isolated. Never point Phaxio tips to Sinch pages and vice versa. SIP/Freeswitch are separate.
- If the exact content does not exist in docs, add it with a new anchor id. Keep copy concise in-page; deep detail is fine but split into subsections with anchors.

Where to put anchors and maps
- Docs base: read from API `GET /admin/config` → `branding.docs_base`.
- Add anchors into the appropriate docs pages (backends, security, diagnostics, deployment, storage, mcp, plugins, tunnels, scripts, etc.).
- Add JSON maps under the docs site at `${docsBase}/anchors/`.
  - File-per-scope (provider or feature), flat object: `{ "topic-key": "https://.../page#anchor-id" }`.
  - Example: `anchors/sinch.json`, `anchors/phaxio.json`, `anchors/sip.json`, `anchors/inbound.json`, `anchors/security.json`, `anchors/storage.json`, `anchors/mcp.json`, `anchors/plugins.json`, `anchors/scripts.json`, `anchors/setup.json`, `anchors/send.json`, `anchors/jobs.json`, `anchors/diagnostics.json`, `anchors/tunnels.json`, `anchors/keys.json`.

Naming conventions
- Anchor ids: kebab-case, scoped by page context, short and durable. Example: `sinch-inbound-basic-auth`.
- Topic keys in JSON maps: same kebab-case and unique across the file. Keep stable; the Admin UI will reference these keys.

Validation requirements
- 200 OK for every mapped URL.
- `document.querySelector(location.hash)` must resolve on load; place anchors directly above the target heading or sentence.
- No external 3rd-party anchors unless they are guaranteed stable (prefer our docs and link out as secondary). When linking to 3rd-party, choose the most canonical documentation page and include their in-page fragment if present.
- Provide a machine-readable coverage summary for each UI component listing all controls and their associated topic keys.

Deliverables
1) PR to docs adding anchors/ sections and missing content.
2) JSON maps in `${docsBase}/anchors/*.json` with all topic→URL pairs.
3) A CSV/JSON coverage report: `component, control/diagnostic key, topic-key` for every entry in the UI.

Screens and required coverage (by component)

1) Dashboard (api/admin_ui/src/components/Dashboard.tsx)
- Cards → routes and help topics:
  - System Status: link to diagnostics overview and common backend health signals.
  - Job Queue: link to jobs page help and status meanings.
  - Inbound Fax: link to inbound overview and enabling per-backend.
  - Security: link to security settings (API keys, HTTPS, audit logging) with HIPAA guidance.
  - Config Overview: explain each line (backend, storage, require_api_key, enforce_https, v3 plugins).
  - MCP Overview: SSE/HTTP/OAuth sections and connect instructions.
  - Plugins: v3 plugin basics and discovery/manifest constraints.
  - SDK & Quickstart: basic API usage + link to SDK docs.
  - Last Updated: diagnostics run guidance.

2) Settings (api/admin_ui/src/components/Settings.tsx)
- Sections and topics:
  - Security Settings: require_api_key, enforce_https, audit_log_enabled, load persisted .env; HIPAA vs dev.
  - Backend selection (outbound/inbound): single vs hybrid, switching guidance.
  - Phaxio config: API key/secret, status callback, HMAC verify for inbound; BAA and storage requirements.
  - Sinch config: project id/key/secret, OAuth2 auth method, SINCH_BASE_URL; inbound webhook URL and Basic auth; register webhook limits and manual steps.
  - SIP/Asterisk: AMI host/port/user/pass, station id, security warnings.
  - Inbound Receiving: enable, retention days, token TTL policies, inbound rate limits.
  - Storage: local vs S3, KMS, compatible endpoints; PHI guidance.
  - Feature flags: v3 plugins, plugin install risks.

3) Setup Wizard (api/admin_ui/src/components/SetupWizard.tsx and ProviderSetupWizard.tsx)
- Steps → topics:
  - Choose Providers: cloud vs self-hosted traits, decision guidance.
  - Credentials: provider-specific credential retrieval (Phaxio, Sinch Build Access Keys), region/base URLs.
  - Security Settings: HIPAA posture requirements (API key, HTTPS, audit logging).
  - Apply & Export: env persistence, restart guidance.
  - Webhooks: per-provider inbound callback URL and verification/auth (Phaxio HMAC, Sinch Basic).
  - Register with Sinch: helper limitations, manual steps.

4) Diagnostics (api/admin_ui/src/components/Diagnostics.tsx)
- Provide anchors for every check/key rendered:
  - Backend: phaxio/sinch/sip and their common failures.
  - System: ghostscript, fax_data_dir, database connected, rate limits.
  - Security: enforce_https, require_api_key, audit_logging, rate_limiting.
  - Storage: backend, bucket, kms enabled, endpoint.
  - Inbound: enabled, provider-specific webhook setup and verification.
  - Built-in tests: send TXT/image/PDF – error interpretations per backend.
  - Troubleshooting: auth failures, webhook failures, regional configs.

5) Send Fax (api/admin_ui/src/components/SendFax.tsx)
- Inputs and errors: file types, size limit, E.164 formatting, base64 limits; cloud vs SIP nuances.

6) Jobs (api/admin_ui/src/components/JobsList.tsx)
- Status values: queued/in_progress/SUCCESS/FAILED; provider status mapping; how to refresh/cancel.

7) Inbound (api/admin_ui/src/components/Inbound.tsx, InboundWebhookTester.tsx)
- Listing, detail, download: tokenized access; retention policies; rate limits.
- Webhook tester: content-types, auth, common errors.

8) Keys (api/admin_ui/src/components/ApiKeys.tsx)
- Scopes and lifecycle: create, rotate, revoke; token format; recommended scopes.

9) Logs (api/admin_ui/src/components/Logs.tsx)
- Where logs go, audit log fields, PHI rules.

10) Terminal & Scripts & Tests (api/admin_ui/src/components/Terminal.tsx, ScriptsTests.tsx)
- Terminal restrictions (local-only), safe actions list; backend-aware tests.

11) Tunnels (api/admin_ui/src/components/TunnelSettings.tsx)
- Cloudflared dev profile, WireGuard import/download/QR, admin access policy; public demo warnings.

12) Plugins (api/admin_ui/src/components/Plugins.tsx, PluginConfigDialog.tsx, PluginBuilder.tsx)
- Enabling/disabling providers; manifests; safe install policies; schema-driven forms.

13) MCP (api/admin_ui/src/components/MCP.tsx)
- SSE/HTTP transport, OAuth requirements, URLs; Electron pairing.

14) Provider specifics
- Phaxio: BAA, disable storage, HMAC verification, callback setup, tokenized PDF.
- Sinch: Build access keys, OAuth2 tokens, base URLs, inbound Basic auth, webhook registry constraints.
- SIP/Asterisk: T.38, AMI security, NAT/ports, originate; inbound internal secret.
- SignalWire/FreeSWITCH/Documo (preview): supported capabilities and setup.

JSON topic key guidelines
- Use consistent prefixes: `security-*`, `storage-*`, `inbound-*`, `diagnostics-*`, `send-*`, `jobs-*`, `keys-*`, `tunnels-*`, `plugins-*`, `mcp-*`, and provider-specific like `phaxio-*`, `sinch-*`, `sip-*`.
- Examples:
  - `security-require-api-key` → deep link to enabling API keys.
  - `security-enforce-https` → deep link for HTTPS policy.
  - `storage-s3-kms` → KMS setup.
  - `inbound-token-ttl` → download token TTL explanation.
  - `diagnostics-ghostscript` → Ghostscript requirement; SIP only.
  - `send-size-limit` → 10 MB limit and base64 notes.
  - `jobs-status-meanings` → canonical status mapping.
  - `mcp-sse-auth` → SSE+OAuth setup.

Process (repeat for each scope)
1) Inspect UI component and list all visible controls and diagnostics keys.
2) Find/author the best doc paragraph for each; add an anchor id.
3) Add a JSON topic map in `anchors/<scope>.json` with topic-key→URL.
4) Verify links (200 OK + element exists).
5) Produce coverage CSV/JSON per component.

Quality bar
- If a user read every linked section in order, they should be able to self-serve or staff a help desk. Err on the side of splitting long pages with multiple anchors.

Submission checklist
- PR with docs page anchors.
- JSON files in `${docsBase}/anchors/` for all scopes.
- Coverage JSON attached.
