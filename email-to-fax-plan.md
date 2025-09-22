# Email-to-Fax — Plan (alpha)

## Goals (non-HIPAA first)
- Zero-install, optional feature to send faxes by emailing attachments to a gateway address.
- Receive inbound faxes as email attachments to a configured mailbox.
- OAuth-only mail access (no raw passwords). No PHI in logs. Feature OFF by default.
- Self-hosted friendly; no SaaS dependency.

## Scope (phase 1)
- Outbound (email to fax):
  - Monitor an OAuth-authenticated mailbox (IMAP IDLE/poll) for new messages.
  - Parse subject/body for destination number (e.g., `fax:+15551234567`).
  - Accept only PDF/TXT attachments (max 10 MB each). Convert TXT→PDF.
  - Create fax job via existing `/fax` endpoint using local file path.
  - Send status email reply (queued/sent/failed) back to sender.
- Inbound (fax to email):
  - On inbound saved to storage, send an email with PDF attached to a configured distribution list.

## Architecture
- New optional provider slot: `emailfax` (disabled by default).
- Mail access via OAuth2 (providers: Gmail/Workspace, Outlook/Microsoft 365, generic OAuth IMAP/SMTP).
- Worker process in API container:
  - Async task loop for mailbox watch + message processing.
  - Rate limiting and dedupe via `Message-Id` and DB table `mail_events`.
- Security:
  - OAuth tokens stored in encrypted file (local dev) or in env for PoC.
  - No plaintext passwords; redact email addresses where possible.
  - Enforce attachment type/size; reject archives/links.

## Config (env)
- EMAILFAX_ENABLED=false
- EMAILFAX_IMAP_HOST=
- EMAILFAX_IMAP_PORT=993
- EMAILFAX_SMTP_HOST=
- EMAILFAX_SMTP_PORT=587
- EMAILFAX_OAUTH_PROVIDER=gmail|microsoft|generic
- EMAILFAX_OAUTH_CLIENT_ID= (optional; for device-code flow later)
- EMAILFAX_OAUTH_TOKENS_PATH=/faxdata/emailfax/tokens.json
- EMAILFAX_ALLOWED_SENDERS= (comma list; optional)
- EMAILFAX_DEFAULT_COUNTRY=US
- EMAILFAX_OUTBOUND_PREFIX=+1
- EMAILFAX_STATUS_REPLY=true
- EMAILFAX_INBOUND_DISTRO= (comma list for inbound fanout)

## API (admin)
- GET /admin/emailfax/status — health, last poll, enabled, provider.
- POST /admin/emailfax/validate — check OAuth token presence/scopes.
- POST /admin/emailfax/toggle — enable/disable.

## UI (Admin Console)
- Tools → Email-to-Fax (feature-gated):
  - OAuth status, provider select (read-only in alpha).
  - Allowed senders list; default country; number parsing help.
  - Learn more links; HIPAA warnings.

## Acceptance Criteria (alpha)
- Process an email with a single PDF attachment into a queued fax job.
- Reject unsupported types and oversize attachments with a status reply.
- Inbound fax triggers an email with the PDF attached to distro.
- No plaintext passwords; tokens file stored locally; logs redact addresses.

## Checklist (live; update as implemented)
- [ ] Settings: server flags and validation
- [ ] Admin endpoint: /admin/emailfax/status
- [ ] Mail OAuth token file read (dev-only)
- [ ] IMAP polling loop (basic poll, 60s) with dedupe
- [ ] Parser: `fax:+E164` in subject/body; sanitize number
- [ ] Attachments: filter PDF/TXT; enforce 10 MB; TXT→PDF
- [ ] Submit to `/fax`; map HTTP errors to email reply text
- [ ] SMTP send: status replies + inbound fanout
- [ ] UI stub (feature-gated) with status and config help
- [ ] Docs link from UI to Apps/Email section

## Risks / Notes
- HIPAA: Disabled by default; require explicit enable + warnings.
- OAuth device-code flow deferred; alpha uses pre-provisioned tokens file.
- Mail provider throttling; add exponential backoff.
- Timezone/locale parsing; keep logic minimal (E.164 only).
