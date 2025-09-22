# Traits‑First Guardrails Proposal (Faxbot v3)

Status: Draft for CTO review
Owner: Admin/API team
Last updated: 2025‑09‑22

## Executive summary

We will make provider traits the single source of truth for capabilities and enforce them across server, Admin Console, SDKs, and external apps. This removes backend string checks, prevents feature leakage (e.g., AMI UI on cloud backends), and gives a stable contract for future plugins.

## Goals
- Eliminate backend‑name conditionals in server/UI; gate by traits only
- Provide canonical endpoints for traits and active providers
- Enforce capability requirements at runtime via middleware
- Make wrong usage obvious (clear errors; docs; tests)
- Keep backwards compatibility with a safe migration switch

## Non‑goals
- No change to transport or storage architectures beyond trait gating
- No immediate refactor of iOS app code; provide contract and examples only

## Terminology
- Trait: canonical capability flag/value (e.g., requires_ami, needs_storage, inbound_verification)
- Direction: outbound | inbound | any

## API changes (server)

Already implemented in this PR branch:
- GET /admin/providers
  - Returns: `{ schema_version: 1, active: { outbound, inbound }, registry: ProviderRegistry }`
- GET /admin/config
  - Adds `traits: { active: { outbound, inbound }, registry }`
- POST /admin/diagnostics/run
  - Adds `traits` (same shape) for screen‑local use
- GET /admin/traits/validate
  - Returns traits registry and any schema issues (for UI/CI visibility)
- provider_traits.json: `sinch.inbound_verification = "basic"`

Planned (breaking only in strict mode):
- Middleware decorator: `@requires_traits(direction="inbound", keys=["supports_inbound"])`
  - On violation: `400` with `{ code: "capability_missing", required: ["supports_inbound"], direction: "inbound" }`
- OpenAPI extension: `x-faxbot-traits` per endpoint
  - Example: `x-faxbot-traits: { direction: "outbound", required: ["requires_ami"], optional: ["requires_tiff"] }`

## Server enforcement
- Centralize capability reads via `providerHasTrait()`/`providerTraitValue()` and `active_outbound()`/`active_inbound()`
- Add startup validation for `config/provider_traits.json`; unknown keys become errors unless `FEATURE_ALLOW_TRAIT_WARNINGS=true`
- Apply `@requires_traits` to:
  - SIP/Asterisk AMI originations/tests
  - Internal inbound hooks that rely on AMI
  - Storage diagnostics/paths when `needs_storage=false`

## Admin Console changes
- Hook: `useTraits()`
  - Reads `/admin/providers` once; memoizes `{ active, registry }`
  - Helpers: `hasTrait(direction,key)`, `traitValue(direction,key)`
- Diagnostics UI
  - Trait fields rendered as informational chips; excluded from pass/fail counters
- Settings & Setup Wizard
  - Sections shown/hidden strictly by traits (e.g., AMI only when `requires_ami=true`)
- Lint rule: disallow string backend gating in UI; require `useTraits()` (CI check)

## SDKs / iOS contract (no code changes here)
- Clients should load traits via `/admin/providers` (or `/admin/config.traits`) once
- Do not gate by backend names; map behavior to traits
- On server `capability_missing`, map to a first‑class error in SDKs

## Testing strategy
- Unit: trait schema validation (unknown keys/types)
- API contract tests for `/admin/providers`, `/admin/config.traits`, `/admin/diagnostics.run.traits`
- Behavior: iterate all backends and assert `@requires_traits` accept/reject semantics
- UI (Playwright): AMI UI absent for cloud backends; present for SIP

## Migration & compatibility
- Default: compatibility mode (warnings only; no hard failures)
- Opt‑in: `TRAITS_STRICT=true` to enforce middleware rejections
- Document anti‑patterns (string compares) and provide code examples to migrate

## Risks & mitigations
- Risk: Client drift
  - Mitigation: single canonical endpoint (`/admin/providers`); SDK helper to load/cache
- Risk: Plugin trait divergence
  - Mitigation: schema validation; `/admin/traits/validate` surfaced in Admin Console Diagnostics
- Risk: Perceived regressions
  - Mitigation: UI renders trait chips as info; clearer errors and docs

## Rollout plan
- Phase 1 (this PR): endpoints + UI gating + docs; compatibility mode
- Phase 2: add middleware; instrument endpoints; server warnings
- Phase 3: enable `TRAITS_STRICT` in staging; fix callers
- Phase 4: make strict default; keep override for on‑prem users for one minor release

## Documentation updates
- AGENTS.md: added strict traits‑first rules, iOS guidance, and acceptance criteria
- BACKENDS.md: map traits to user‑visible capabilities
- API_REFERENCE.md: document `x-faxbot-traits` and capability_missing errors

## Work items (tracked)
- [x] `/admin/providers`, `/admin/config.traits`, `/admin/diagnostics.traits`
- [x] UI Diagnostics informational chips
- [x] Setup Wizard gated copy
- [ ] `@requires_traits` middleware + endpoint annotations
- [ ] UI `useTraits()` helper and sweep of all screens
- [ ] ESLint rule to ban backend strings
- [ ] Tests: schema/API/behavior/UI
- [ ] Docs: API reference and backend mapping

## Appendix A: Canonical trait keys (schema v1)
- requires_ghostscript: boolean
- requires_ami: boolean
- requires_tiff: boolean
- supports_inbound: boolean
- inbound_verification: "none" | "basic" | "hmac"
- needs_storage: boolean
- outbound_status_only: boolean

## Appendix B: Example usage
Server:
```python
@requires_traits(direction="inbound", keys=["supports_inbound"]) 
@app.post("/_internal/asterisk/inbound")
async def asterisk_inbound(...):
    ...
```

UI:
```ts
const { hasTrait } = useTraits();
if (hasTrait('outbound','requires_ami')) {
  // render AMI section
}
```
