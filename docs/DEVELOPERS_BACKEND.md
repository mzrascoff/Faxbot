# Faxbot Backend Developer Guide (v3)

Audience: Backend engineers (API/adapters)

## Architecture at a glance
- Traits‑first capabilities: `config/provider_traits.json` (+ manifests) are the single source of truth.
- Adapters boundary: `api/app/providers/base.py` defines verify_webhook, parse_inbound, send, status, cancel.
- Canonical models: `api/app/models/canonical.py` (NormalizedStatus, InboundFaxEvent, OutboundFaxEvent, CanonicalError).
- Status mapping: `config/provider_status_map.json` → `api/app/status_map.py` loader; `canonical_status()` helper.
- Middleware: `api/app/middleware/traits.py::requires_traits` with `TRAITS_STRICT` to enforce capability checks.
- Observability: `api/app/utils/observability.py::log_event` structured logs (no PHI).
- Admin surface: `/admin/config` exposes `traits.active`, `traits.registry`, and a providers summary; `/admin/providers` and `/admin/traits/validate` exist for tooling/CI.

## Day‑to‑day workflows
- Adding a provider trait: update `config/provider_traits.json`, run `/admin/traits/validate`, and guard code/UI by `providerHasTrait()`/`useTraits()`.
- Mapping provider statuses: add raw→canonical aliases in `config/provider_status_map.json`; loader validates at startup.
- Enforcing capability checks: decorate handlers with `@requires_traits(direction, keys=[...])`. In strict mode (TRAITS_STRICT=true) violations return HTTP 400 with `{ code:"capability_missing" }`.
- Logging canonical events: call `log_event(logger, event_type, provider, status_canonical, status_raw?, signature_valid?, start_ns?)`.
- Replaying webhooks: `scripts/replay_webhook.py https://localhost:8080/phaxio-inbound file.json --api-key fbk_live_...`.

## Inbound webhooks (summary)
- Cloud providers: `POST /phaxio-inbound`, `POST /sinch-inbound` guarded by `@requires_traits('inbound', ['supports_inbound'])`.
- SIP internal: `POST /_internal/asterisk/inbound` guarded by `@requires_traits('inbound', ['supports_inbound','requires_ami'])`.
- Idempotency: unique constraint via InboundEvent (provider_sid,event_type).

## Outbound (summary)
- `POST /fax` → adapter.send(); `GET /fax/{id}` → adapter.status(); `DELETE /fax/{id}` (future) → adapter.cancel() when supported.
- Normalize statuses via `canonical_status(provider, raw)` before returning.

## Error contract
- Common codes: capability_missing, signature_invalid, unsupported_operation, rate_limited, provider_timeout.
- Prefer `{ code, message, provider?, details? }` in `detail` for user‑facing errors; do not include PHI.

## Testing checklist
- Trait schema validation passes; no unknown keys (strict mode error, warn otherwise).
- Status map validation passes; required canonical buckets exist.
- Provider adapters: good/bad signature vectors → 200/401; payload→canonical normalization.
- Middleware: capability_missing enforced in strict mode; logged warning in warn mode.

## Future Work (Sr. Dev notes)
- Outbound normalization v1
  - Wire `/fax` send/status to `api/app/providers/outbound.py` and return canonical statuses consistently; add optional cancel route (501 when unsupported).
- Canonical Pydantic models
  - Replace dataclasses with Pydantic models for stricter type checks and OpenAPI alignment.
- Strict traits rollout
  - Expand `@requires_traits` coverage: storage ops when `needs_storage=true`; SIP originate/test when `requires_ami=true`.
- Contract tests
  - Add provider contract tests under `api/tests/providers` (signature vectors; normalization; strict‑mode behavior).
- Persistence option
  - Consider storing full canonical inbound JSON alongside current tables (JSON column), keeping logs as the primary short‑term source.
- Metrics
  - Export counters for `event_type, provider, status_canonical` (Prometheus/OTEL) and wire Grafana dashboards.

## References
- Traits guardrails: `v3_plans/traits-first-guardrails.md`
- Canonical event doc: `docs/api/canonical_events.md`
