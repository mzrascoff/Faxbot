
# Diagnostics Matrix

Each check maps to a fix, relevant environment variables, and the UI path to change it.

[:material-stethoscope: Diagnostics Guide](diagnostics.md){ .md-button }
[:material-book-open: Backends](../setup/index.md){ .md-button }
[:material-shield-lock: Security](../security/index.md){ .md-button }

---

## Backend: Phaxio

Missing API key/secret
: :material-wrench: Fix — set `PHAXIO_API_KEY`, `PHAXIO_API_SECRET`  
  :material-cog: UI — Settings → Backend → Phaxio

Callback unreachable or unset
: :material-wrench: Fix — set `PHAXIO_CALLBACK_URL` (or `PHAXIO_STATUS_CALLBACK_URL`) to `<PUBLIC_API_URL>/phaxio-callback`  
  :material-cog: UI — Settings → Backend → Phaxio; also verify `PUBLIC_API_URL` in Settings → Security

Signature verification disabled
: :material-wrench: Fix — enable `PHAXIO_VERIFY_SIGNATURE=true`  
  :material-cog: UI — Settings → Backend → Phaxio (Verify signatures)

## Backend: Sinch

Missing project/credentials
: :material-wrench: Fix — set `SINCH_PROJECT_ID`, `SINCH_API_KEY`, `SINCH_API_SECRET`  
  :material-cog: UI — Settings → Backend → Sinch

Wrong region/base URL
: :material-wrench: Fix — set `SINCH_BASE_URL` to the correct regional endpoint  
  :material-cog: UI — Settings → Backend → Sinch

## Backend: SIP/Asterisk

AMI unreachable or auth failed
: :material-wrench: Fix — verify `ASTERISK_AMI_HOST`, `ASTERISK_AMI_PORT`, `ASTERISK_AMI_USERNAME`, `ASTERISK_AMI_PASSWORD`  
  :material-cog: UI — Settings → Backend → SIP/Asterisk

TIFF conversion unavailable
: :material-wrench: Fix — install Ghostscript (`gs`) on API host  
  :material-cog: UI — N/A (server dependency); rerun Diagnostics after install

## Public URL / HTTPS

Missing or HTTP in production
: :material-wrench: Fix — set `PUBLIC_API_URL` to your HTTPS domain; enable `ENFORCE_PUBLIC_HTTPS=true`  
  :material-cog: UI — Settings → Security

## Security posture

API key not required
: :material-wrench: Fix — set `API_KEY` to a strong value; restart if necessary  
  :material-cog: UI — Settings → Security

Audit logging off (HIPAA profile)
: :material-wrench: Fix — `AUDIT_LOG_ENABLED=true`; optionally configure file/syslog  
  :material-cog: UI — Settings → Security → Audit

## Storage (Inbound)

Local path unwritable
: :material-wrench: Fix — check `FAX_DATA_DIR` permissions or switch to S3  
  :material-cog: UI — Settings → Storage

S3 not accessible
: :material-wrench: Fix — verify bucket/region/prefix/endpoint; use role/env credentials; (optional) enable diagnostics for HeadBucket  
  :material-cog: UI — Settings → Storage

## File limits

Uploads rejected as too large
: :material-wrench: Fix — raise `MAX_FILE_SIZE_MB` and communicate the limit in the UI  
  :material-cog: UI — Settings → Security → File limits

---

## Actions

- After each change, click “Apply & Reload” and rerun Diagnostics  
- Use “Restart API” when prompted (if enabled) for backend client reinitialization
