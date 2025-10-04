# HumbleFax Integration (Outbound + Inbound)

This guide summarizes the verified request format, environment variables, and end-to-end testing steps for HumbleFax.

Notes
- Verified against HumbleFax quickSendFax: `multipart/form-data` with `file` field and `jsonData` object.
- `jsonData` requires `recipients` (array of integers), `includeCoversheet`, `pageSize` (Letter|Legal|A4|B4), and typically `resolution` (Fine).
- Optional `fromNumber` (integer) and `uuid` (idempotency).
- Debug logging is available via `HUMBLEFAX_DEBUG=true` (PHI is masked in logs).

Environment
- `HUMBLEFAX_ACCESS_KEY` (required)
- `HUMBLEFAX_SECRET_KEY` (required)
- `HUMBLEFAX_FROM_NUMBER` (optional, recommended)
- `HUMBLEFAX_WEBHOOK_SECRET` (optional, HMAC verification)
- `HUMBLEFAX_CALLBACK_BASE` (optional, used by the Admin UI register helper)
- `HUMBLEFAX_DEBUG` (optional; set `true` for request/response debug without PHI)

Direct API Validation
```
set -euo pipefail
set -o allexport && [ -f .env ] && . ./.env && set +o allexport
: "${HUMBLEFAX_ACCESS_KEY:?}"; : "${HUMBLEFAX_SECRET_KEY:?}"
TO_FAX="+15551234567"; TO_FAX_DIGITS="$(printf "%s" "$TO_FAX" | tr -cd '0-9')"
FROM_DIGITS="$(printf "%s" "${HUMBLEFAX_FROM_NUMBER:-}" | tr -cd '0-9')"
if [ ${#FROM_DIGITS} -ge 10 ]; then
  BODY_JSON=$(printf '{"recipients":[%s],"includeCoversheet":false,"pageSize":"Letter","resolution":"Fine","fromNumber":%s}' "$TO_FAX_DIGITS" "$FROM_DIGITS")
else
  BODY_JSON=$(printf '{"recipients":[%s],"includeCoversheet":false,"pageSize":"Letter","resolution":"Fine"}' "$TO_FAX_DIGITS")
fi
echo "Faxbot HumbleFax outbound test $(date -u)" > /tmp/faxbot-test.txt
curl -sS -L 'https://api.humblefax.com/quickSendFax' \
  -u "$HUMBLEFAX_ACCESS_KEY:$HUMBLEFAX_SECRET_KEY" \
  -F "jsonData=${BODY_JSON}" \
  -F "file=@/tmp/faxbot-test.txt;type=text/plain" | jq .
```

Faxbot API End-to-End
```
export HUMBLEFAX_DEBUG=true
curl -sS -X POST http://localhost:8080/fax \
  -H "X-API-Key: ${API_KEY:-fbk_live_local_admin}" \
  -F "to=+15551234567" \
  -F "file=@README.md"

# Poll job (replace {job_id})
curl -sS http://localhost:8080/fax/{job_id} -H "X-API-Key: ${API_KEY}"
```

Webhooks
- Endpoint: `/inbound/humblefax/webhook`
- Always returns `202` promptly; deduped by `(provider, external_id)`
- HMAC-SHA256 verification when `HUMBLEFAX_WEBHOOK_SECRET` is set using headers: `X-Humblefax-Signature` (variants tolerated)
- SentFax: updates outbound job status by `provider_sid`
- IncomingFax: background task downloads PDF and stores via configured storage backend

Admin UI
- Use Setup Wizard (HumbleFax) to enter keys and webhook secret.
- “Register HumbleFax Webhook” button registers callbacks to `${public_api_url}/inbound/humblefax/webhook`.
 - Run diagnostics: Tools → Tunnels → “Run HumbleFax Diagnostics” or `GET /admin/diagnostics/humblefax`.

Security
- No PHI is logged (only job IDs and meta counters). Recipients and fromNumber are masked in debug logs.
- Webhooks are idempotent and return 202 Accepted.

One‑shot tunnel + webhook setup
- scripts/setup-humblefax-tunnel.sh starts the API + Cloudflare sidecar, detects the public URL, sets HUMBLEFAX_CALLBACK_BASE, and registers the webhook.
- Requirements: Docker running; API_KEY (defaults to fbk_live_local_admin if unset).

Diagnostics
```
curl -sS -H "X-API-Key: ${API_KEY:-fbk_live_local_admin}" \
  http://localhost:8080/admin/diagnostics/humblefax | jq .
```
Fields
- `dns_ok`: provider host resolves from inside the container
- `auth_present`/`auth_ok`: credentials configured and accepted by the endpoint
- `webhook_url_ok`: your computed webhook URL is reachable (tolerant of 405)
  - If false, set `PUBLIC_API_URL` or `HUMBLEFAX_CALLBACK_BASE` to a stable HTTPS URL and retry.

Run
```
scripts/setup-humblefax-tunnel.sh
```
After this, check Admin Console → Tools → Tunnels; you should see Connected with the public URL, and Inbox → Refresh should receive HumbleFax callbacks.
