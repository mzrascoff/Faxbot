You are implementing Faxbot v4 in the **auto-tunnel** branch. CRITICAL RULES:

- Work only in `auto-tunnel`. Never touch `main`. Merge to `development` only via PR after green CI.
- Do NOT rename any existing routes: keep `/phaxio-callback`, `/phaxio-inbound`, `/sinch-inbound`, and current Admin paths.
- Traits > names; plugins > legacy services; Admin Console is primary (must remain functional).
- Config is DB-first; `.env` is an outage fallback only.
- Webhooks must return **202 Accepted** and be **idempotent** (dedupe by `provider_id + external_id`); DLQ headers allowlisted (no secrets).
- One metrics endpoint (`/metrics`) and a single health monitor/circuit breaker.
- Fail fast if `CONFIG_MASTER_KEY` (44-char base64) or `FAXBOT_SESSION_PEPPER` are missing.
- Docker Compose is the canonical dev path; do not require host installs.
- Keep patches minimal; touch only the files listed; include acceptance greps and explain outcomes.

Branch: `auto-tunnel`

""""
DONE
PR1 — Transport shims + Canonical Provider Traits → UI (no behavior change)
Goal: expose canonical traits to the UI and introduce TransportPlugin shims that wrap existing services. No route changes, no logic changes.
Touch only these files
	•	api/app/plugins/manager.py — add get_by_type_and_id(type,id) and get_active_by_type(type).
	•	api/app/plugins/transport/shims/{phaxio,sinch,sip,freeswitch}/plugin.py — shims that call the current services, async-safe.
	•	config/provider_traits.json — normalize keys to canonical form:
	◦	traits.webhook.path
	◦	traits.webhook.verification = "hmac_sha256" (Phaxio), "basic_auth" (Sinch)
	◦	traits.webhook.verify_header = "X-Phaxio-Signature" (Phaxio), "Authorization" (Sinch)
	◦	traits.auth.methods = ["basic"] or ["basic","oauth2"]
	◦	traits.regions where applicable
	◦	traits.sample_payload is PHI-free (dummy numbers)
Acceptance
	•	Server boots unchanged.
	•	/admin/providers (with API-key) lists providers & canonical traits.
	•	CI: traits schema job passes; greps from PR0 do not fail.
Smoke (local; bundled)

bash -lc 'set -euo pipefail \
&& echo "[build]" && docker compose build \
&& echo "[up]" && docker compose up -d \
&& echo "[providers]" && curl -fsS -H "X-API-Key: ${API_KEY:-dev}" http://localhost:8080/admin/providers | jq . | head -n 60'

""""

PR2 — Webhooks: 202 Accepted + Idempotency Guard (brownfield-safe)
Goal: make inbound handlers idempotent and return 202 immediately after verification/queueing. Keep current routes intact.
Touch only these files
	•	api/app/main.py (or the router module actually hosting these handlers):
	◦	/phaxio-callback, /phaxio-inbound, /sinch-inbound
	◦	Verify per traits (webhook.verification & webhook.verify_header).
	◦	Idempotency guard: dedupe on (provider_id, external_id) using DB unique index OR Redis SETNX with TTL 10m.
	◦	Enqueue/persist canonical status/event (no PHI), then return JSONResponse({"ok": true}, status_code=202)
	•	(If you have a DLQ) ensure header allowlist excludes Authorization, Cookie.
Acceptance
	•	A repeated callback for the same (provider, external_id) returns 202 without reprocessing.
	•	Greps from PR0 show status_code=202 on those routes.
	•	No route names were changed.
Smoke (local; bundled)

bash -lc 'set -euo pipefail \
&& echo "[simulate phaxio callback #1]" \
&& curl -sS -o /dev/null -w "%{http_code}\n" -X POST http://localhost:8080/phaxio-callback \
   -H "X-Phaxio-Signature: test" -H "Content-Type: application/json" \
   -d "{\"id\":\"dup1\",\"status\":\"success\"}" \
&& echo "[simulate phaxio callback duplicate]" \
&& curl -sS -o /dev/null -w "%{http_code}\n" -X POST http://localhost:8080/phaxio-callback \
   -H "X-Phaxio-Signature: test" -H "Content-Type: application/json" \
   -d "{\"id\":\"dup1\",\"status\":\"success\"}"'

"""

PR3 — Observability Unification (one /metrics, single health monitor)

Goal: expose exactly one Prometheus metrics endpoint (/metrics) on the API port and ensure there is one ProviderHealthMonitor/CircuitBreaker. No feature changes.

Touch only these files

api/app/monitoring/metrics.py — centralize Prometheus client registration (native prometheus_client, not OTel Prom reader).

api/app/main.py (or equivalent app factory) — mount GET /metrics once; wire existing Phase-3 ProviderHealthMonitor; remove/disable any duplicate monitor or duplicate metrics mount.

deployment/kubernetes/faxbot-v4.yaml (if present) — make scrape annotations and port match the real API port that serves /metrics (e.g., 8080).
Do not add a second metrics port unless the app really listens there.

Implement

Native Prom client only (simple, reliable):

# api/app/monitoring/metrics.py
from prometheus_client import CollectorRegistry, CONTENT_TYPE_LATEST, generate_latest
registry = CollectorRegistry()  # optional custom reg; default is fine too

def render_prometheus():
    data = generate_latest()     # default registry
    return (data, CONTENT_TYPE_LATEST)


Mount endpoint once:

# api/app/main.py
from fastapi import Response
from api.app.monitoring.metrics import render_prometheus

@app.get("/metrics")
async def metrics():
    data, ctype = render_prometheus()
    return Response(content=data, media_type=ctype)


Health monitor: keep the Phase-3 ProviderHealthMonitor; remove duplicates (don’t instantiate a second one in Phase-5 code).

Acceptance

rg -n "/metrics" api/app | wc -l → 1

rg -n "class .*ProviderHealthMonitor" api/app | wc -l → 1

If repository previously used OTel PrometheusMetricReader and native prom, ensure only one stack remains serving /metrics.

Smoke (local; bundled)

bash -lc 'set -euo pipefail \
&& docker compose build && docker compose up -d \
&& echo "[/metrics]" && curl -fsS http://localhost:8080/metrics | head -n 10 \
&& echo "[health grep]" && rg -n "class .*ProviderHealthMonitor" api/app'

"""

PR4 — Phase-1 Core: Manifest-First Discovery (using the shims)

Goal: implement manifest-first plugin discovery for transports (and storage later), validating manifests, while continuing to use the already-merged transport shims under the hood. No route changes; /fax still uses the shims.

Touch only these files

api/app/plugins/manifest.schema.json — JSON-Schema for plugin manifests (type/id/name/version/traits/config_schema).

api/app/plugins/manager.py — add directory scan & validation:

scan api/app/plugins/<type>/<id>/manifest.json

validate against manifest.schema.json

register with get_by_type_and_id() / get_active_by_type()

map manifests → shim classes (e.g., transport/phaxio → transport/shims/phaxio/plugin.py)

Manifests (examples):

api/app/plugins/transport/phaxio/manifest.json

api/app/plugins/transport/sinch/manifest.json

api/app/plugins/transport/sip/manifest.json

api/app/plugins/transport/freeswitch/manifest.json

(optional now) transport/humblefax, transport/signalwire, transport/test

Implement

Manifest example (phaxio):

{
  "id": "phaxio",
  "name": "Phaxio Cloud Fax",
  "version": "1.0.0",
  "type": "transport",
  "traits": {
    "send_fax": true,
    "status_callback": true,
    "inbound_supported": true,
    "webhook": {
      "path": "/phaxio-callback",
      "verification": "hmac_sha256",
      "verify_header": "X-Phaxio-Signature"
    },
    "auth": { "methods": ["basic"] }
  },
  "config_schema": { "type": "object", "properties": {} }
}


Manager wiring (pseudo):

# manager.py
def load_all(self):
    for type_dir in ["transport"]:  # storage later
        for id_dir in list_dirs(f"api/app/plugins/{type_dir}"):
            m = load_json(.../manifest.json); validate(m)
            cls = shim_for(type_dir, m["id"])  # map to shims
            instance = cls()
            self.register(type_dir, m["id"], instance, manifest=m)


Acceptance

/admin/providers lists plugins discovered from manifests; trait fields match manifest.

Sending a fax still works (shims call the legacy service code).

CI traits schema & OpenAPI diff remain green.

Smoke (local; bundled)

bash -lc 'set -euo pipefail \
&& docker compose build && docker compose up -d \
&& echo "[providers]" && curl -fsS -H "X-API-Key: ${API_KEY:-dev}" http://localhost:8080/admin/providers | jq . \
&& echo "[send (expect 200/queued or a provider error if creds missing)]" \
&& curl -sS -X POST http://localhost:8080/fax -H "X-API-Key: ${API_KEY:-dev}" \
   -F to=+15551234567 -F file=@tests/fixtures/tiny.pdf | jq .'

""""

PR5 — UI: Trait-First Gating (remove provider name checks)

Goal: update the Admin Console to render provider-specific UX by traits, not IDs; surface inbound path and verification mode from traits; remove hardcoded fallbacks.

Touch only these files

api/admin_ui/src/hooks/useTraits.ts

api/admin_ui/src/components/Diagnostics.tsx

(Optionally) any small component that still does 'sinch'|'phaxio'|'sip' checks.

Implement

Hook helpers:

// useTraits.ts
export function traitValue(traits: any, key: string, fallback?: any) {
  // dot-path read, e.g., "webhook.path"
  return key.split('.').reduce((acc, k) => (acc && acc[k] !== undefined ? acc[k] : undefined), traits) ?? fallback;
}
export function hasTrait(traits: any, key: string): boolean {
  return !!traitValue(traits, key);
}


Diagnostics:

Replace any if (activeProvider === 'sinch'|...) with:

const webhookPath = traitValue(providerTraits, 'webhook.path', '—');
const verification = traitValue(providerTraits, 'webhook.verification', 'none'); // hmac_sha256 | basic_auth | none
const verifyHeader = traitValue(providerTraits, 'webhook.verify_header', '—');
// render rows for these three; hide name-specific branches


Remove fallback maps keyed by provider name for webhook samples once the server traits include webhook.* and sample_payload.

Acceptance

Grep shows no provider name checks:

rg -n "=== 'sinch'|=== 'phaxio'|=== 'sip'|active\.outbound" api/admin_ui/src | wc -l


→ 0

Diagnostics renders inbound path & verification from traits for the active provider.

No TS type errors.

Smoke (local; bundled)

bash -lc 'set -euo pipefail \
&& docker compose build && docker compose up -d \
&& echo "[providers json]" && curl -fsS -H "X-API-Key: ${API_KEY:-dev}" http://localhost:8080/admin/providers | jq . | head -n 80 \
&& echo "[manual check] Open UI Diagnostics and confirm it shows webhook path + verification from traits."'

