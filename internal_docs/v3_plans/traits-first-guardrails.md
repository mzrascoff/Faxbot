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


A DIFFERENT ROUTE BUT SIMILAR: 

You’re right—the fragile spots are the cloud provider integrations. Let’s make traits the contract at the adapter boundary, normalize their webhooks/statuses, and verify inbound signatures—all without a huge refactor.

Below is a single, copy-paste command that scaffolds a minimal “Provider Conformance Layer” focused on Sinch and Phaxio first (you can add others the same way). It:

Adds a small provider adapter API + registry.

Adds config/provider_traits.json with verification hints per provider.

Adds config/provider_status_map.json for canonical status mapping.

Creates a unified /webhooks/inbound FastAPI route that:

Detects provider from headers or ?provider=.

Enforces traits (supports_inbound, inbound_verification).

Verifies HMAC for Sinch/Phaxio.

Normalizes payloads into one canonical event shape.

Patches api/app/main.py to include the new router.

Run this from the repo root on your development branch. No comments are inside heredocs.

bash -euxo pipefail <<'SCRIPT'
git fetch origin && git checkout development && git pull --ff-only

mkdir -p config api/app/providers api/app/webhooks api/tests/providers

cat > config/provider_traits.json <<'JSON'
{
  "schema_version": 1,
  "providers": {
    "sinch": {
      "requires_ghostscript": false,
      "requires_ami": false,
      "requires_tiff": false,
      "supports_inbound": true,
      "inbound_verification": "hmac",
      "inbound_signature_header": "X-Sinch-Signature",
      "inbound_signature_algo": "sha256",
      "needs_storage": false,
      "outbound_status_only": true
    },
    "phaxio": {
      "requires_ghostscript": false,
      "requires_ami": false,
      "requires_tiff": false,
      "supports_inbound": true,
      "inbound_verification": "hmac",
      "inbound_signature_header": "X-Phaxio-Signature",
      "inbound_signature_algo": "sha1",
      "needs_storage": false,
      "outbound_status_only": false
    },
    "freeswitch": {
      "requires_ghostscript": true,
      "requires_ami": false,
      "requires_tiff": true,
      "supports_inbound": true,
      "inbound_verification": "none",
      "needs_storage": true,
      "outbound_status_only": false
    }
  }
}
JSON

cat > config/provider_status_map.json <<'JSON'
{
  "schema_version": 1,
  "canonical": ["queued","processing","delivered","failed","canceled","unknown"],
  "providers": {
    "phaxio": {
      "queued": ["queued","pending"],
      "processing": ["sending","in_progress","processing"],
      "delivered": ["success","completed","delivered"],
      "failed": ["failure","failed","error","no_answer","busy","disconnected"],
      "canceled": ["canceled","cancelled"]
    },
    "sinch": {
      "queued": ["queued","submitted","pending"],
      "processing": ["processing","sending","in_progress"],
      "delivered": ["success","completed","delivered","succeeded"],
      "failed": ["failed","error","terminated","undeliverable"],
      "canceled": ["canceled","cancelled"]
    }
  }
}
JSON

cat > api/app/providers/base.py <<'PY'
from pathlib import Path
import json, os, hmac, hashlib, re
from typing import Dict, Any, Optional

ROOT = Path(__file__).resolve().parents[3]
TRAITS_PATH = ROOT / "config" / "provider_traits.json"
STATUS_MAP_PATH = ROOT / "config" / "provider_status_map.json"

def load_traits() -> Dict[str, Any]:
    try:
        return json.loads(TRAITS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"schema_version": 1, "providers": {}}

def load_status_map() -> Dict[str, Any]:
    try:
        return json.loads(STATUS_MAP_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"schema_version": 1, "canonical": [], "providers": {}}

STATUS_MAP = load_status_map()

def canonical_status(provider: str, value: str) -> str:
    v = (value or "").strip().lower()
    table = STATUS_MAP.get("providers", {}).get(provider, {})
    for canon, variants in table.items():
        if v in [s.lower() for s in variants]:
            return canon
    if re.search(r"success|complete|deliver", v):
        return "delivered"
    if re.search(r"fail|error|undeliver|terminate|disconnect", v):
        return "failed"
    if re.search(r"cancel", v):
        return "canceled"
    if re.search(r"queue|submit|pend", v):
        return "queued"
    if re.search(r"progress|process|sending", v):
        return "processing"
    return "unknown"

def secure_compare(a: str, b: str) -> bool:
    try:
        return hmac.compare_digest(a.strip(), b.strip())
    except Exception:
        return False

def hmac_signature_ok(algo: str, header_value: str, body: bytes, secret: str) -> bool:
    if not header_value or not secret:
        return False
    hv = header_value
    if "=" in hv:
        parts = hv.split("=", 1)
        hv = parts[1] if len(parts) == 2 else hv
    if algo.lower() == "sha256":
        digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    elif algo.lower() == "sha1":
        digest = hmac.new(secret.encode(), body, hashlib.sha1).hexdigest()
    else:
        return False
    return secure_compare(hv, digest)

class ProviderAdapter:
    name = "base"
    def traits(self) -> Dict[str, Any]:
        return {}
    def verify_webhook(self, headers: Dict[str,str], body: bytes, secrets: Dict[str,str]) -> bool:
        return True
    def parse_inbound(self, headers: Dict[str,str], body: bytes) -> Dict[str,Any]:
        return {"provider": self.name, "status": "unknown", "raw": {}}
PY

cat > api/app/providers/registry.py <<'PY'
import os, json
from typing import Dict, Any
from .base import load_traits
from .sinch import SinchAdapter
from .phaxio import PhaxioAdapter

PROVIDERS = {
    "sinch": SinchAdapter(),
    "phaxio": PhaxioAdapter()
}

def provider_traits(name: str) -> Dict[str, Any]:
    t = load_traits()
    return t.get("providers", {}).get(name, {})

def get_active_backend_name() -> str:
    env_name = os.getenv("FAXBOT_BACKEND")
    if env_name:
        return env_name
    try:
        from ..config import settings
        return getattr(settings, "fax_backend")
    except Exception:
        return "phaxio"

def get_adapter(name: str):
    return PROVIDERS.get(name)

def get_active_adapter():
    return get_adapter(get_active_backend_name())
PY

cat > api/app/providers/sinch.py <<'PY'
import json, os
from typing import Dict, Any
from .base import ProviderAdapter, canonical_status, hmac_signature_ok
from .registry import provider_traits

class SinchAdapter(ProviderAdapter):
    name = "sinch"
    def traits(self) -> Dict[str,Any]:
        return provider_traits(self.name)
    def verify_webhook(self, headers: Dict[str,str], body: bytes, secrets: Dict[str,str]) -> bool:
        traits = self.traits()
        if traits.get("inbound_verification") != "hmac":
            return True
        header = traits.get("inbound_signature_header") or "X-Sinch-Signature"
        algo = traits.get("inbound_signature_algo") or "sha256"
        hv = headers.get(header) or headers.get(header.lower()) or ""
        secret = secrets.get("SINCH_WEBHOOK_SECRET") or os.getenv("SINCH_WEBHOOK_SECRET") or ""
        return hmac_signature_ok(algo, hv, body, secret)
    def parse_inbound(self, headers: Dict[str,str], body: bytes) -> Dict[str,Any]:
        try:
            data = json.loads(body.decode("utf-8"))
        except Exception:
            data = {}
        fax_id = str(data.get("id") or data.get("faxId") or data.get("fax_id") or "")
        status_in = str(data.get("status") or data.get("state") or "")
        status = canonical_status(self.name, status_in)
        remote = str(data.get("from") or data.get("caller") or data.get("source") or "")
        local = str(data.get("to") or data.get("destination") or "")
        pages = data.get("pages") if isinstance(data.get("pages"), int) else None
        media = data.get("mediaUrl") or data.get("file_url") or ""
        return {
            "provider": self.name,
            "direction": "inbound",
            "fax_id": fax_id,
            "status": status,
            "remote": remote,
            "local": local,
            "pages": pages,
            "media_url": media,
            "raw": data
        }
PY

cat > api/app/providers/phaxio.py <<'PY'
import json, os
from typing import Dict, Any
from .base import ProviderAdapter, canonical_status, hmac_signature_ok
from .registry import provider_traits

class PhaxioAdapter(ProviderAdapter):
    name = "phaxio"
    def traits(self) -> Dict[str,Any]:
        return provider_traits(self.name)
    def verify_webhook(self, headers: Dict[str,str], body: bytes, secrets: Dict[str,str]) -> bool:
        traits = self.traits()
        if traits.get("inbound_verification") != "hmac":
            return True
        header = traits.get("inbound_signature_header") or "X-Phaxio-Signature"
        algo = traits.get("inbound_signature_algo") or "sha1"
        hv = headers.get(header) or headers.get(header.lower()) or ""
        secret = secrets.get("PHAXIO_WEBHOOK_SECRET") or os.getenv("PHAXIO_WEBHOOK_SECRET") or ""
        return hmac_signature_ok(algo, hv, body, secret)
    def parse_inbound(self, headers: Dict[str,str], body: bytes) -> Dict[str,Any]:
        try:
            data = json.loads(body.decode("utf-8"))
        except Exception:
            data = {}
        fax = data.get("fax") or data
        fax_id = str(fax.get("id") or fax.get("faxId") or "")
        status_in = str(fax.get("status") or fax.get("state") or "")
        status = canonical_status(self.name, status_in)
        remote = str(fax.get("from_number") or fax.get("from") or "")
        local = str(fax.get("to_number") or fax.get("to") or "")
        pages = fax.get("num_pages") if isinstance(fax.get("num_pages"), int) else None
        media = fax.get("file_url") or fax.get("mediaUrl") or ""
        return {
            "provider": self.name,
            "direction": "inbound",
            "fax_id": fax_id,
            "status": status,
            "remote": remote,
            "local": local,
            "pages": pages,
            "media_url": media,
            "raw": data
        }
PY

cat > api/app/webhooks/inbound.py <<'PY'
from fastapi import APIRouter, Request, HTTPException
import os, json
from typing import Dict, Any
from ..providers.registry import get_active_adapter, get_adapter, provider_traits

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

def detect_provider(headers: Dict[str,str], fallback: str) -> str:
    h = {k.lower():v for k,v in headers.items()}
    if "x-phaxio-signature" in h:
        return "phaxio"
    if "x-sinch-signature" in h:
        return "sinch"
    return fallback

def strict_mode() -> bool:
    v = os.getenv("TRAITS_STRICT","false").strip().lower()
    return v in {"1","true","yes","on"}

def secrets_dict() -> Dict[str,str]:
    return {
        "PHAXIO_WEBHOOK_SECRET": os.getenv("PHAXIO_WEBHOOK_SECRET",""),
        "SINCH_WEBHOOK_SECRET": os.getenv("SINCH_WEBHOOK_SECRET","")
    }

@router.post("/inbound")
async def inbound(request: Request) -> Any:
    body = await request.body()
    headers = dict(request.headers)
    provider_q = request.query_params.get("provider")
    active = get_active_adapter()
    active_name = active.name if active else "phaxio"
    name = provider_q or detect_provider(headers, active_name)
    adapter = get_adapter(name)
    if not adapter:
        raise HTTPException(status_code=400, detail={"code":"unknown_provider","provider":name})
    traits = provider_traits(name)
    if strict_mode() and not traits.get("supports_inbound", False):
        raise HTTPException(status_code=400, detail={"code":"capability_missing","required":["supports_inbound"],"direction":"inbound"})
    ok = adapter.verify_webhook(headers, body, secrets_dict())
    if strict_mode() and not ok:
        raise HTTPException(status_code=401, detail={"code":"signature_invalid","provider":name})
    event = adapter.parse_inbound(headers, body)
    return {"ok": True, "provider": name, "event": event}
PY

python3 - <<'PY'
import io, os, re
p="api/app/main.py"
if not os.path.exists(p):
    raise SystemExit(0)
s=open(p,"r",encoding="utf-8").read()
if "webhooks.inbound" not in s:
    s="from .webhooks.inbound import router as inbound_router\n"+s
if "include_router(inbound_router)" not in s:
    s=re.sub(r"(app\s*=\s*FastAPI\([^\)]*\))", r"\\1\napp.include_router(inbound_router)", s, count=1)
open(p,"w",encoding="utf-8").write(s)
print("patched api/app/main.py")
PY

cat > api/tests/providers/test_contract.py <<'PY'
from api.app.providers.registry import PROVIDERS, provider_traits

def test_all_providers_have_traits():
    for name, adapter in PROVIDERS.items():
        tr = provider_traits(name)
        assert isinstance(tr, dict)
        assert "supports_inbound" in tr

def test_adapters_have_name():
    for name, adapter in PROVIDERS.items():
        assert adapter.name == name
PY

git add config/provider_traits.json config/provider_status_map.json api/app/providers/*.py api/app/webhooks/inbound.py api/tests/providers/test_contract.py
git commit -m "feat(api): traits-first conformance layer for cloud providers; unified inbound webhook with HMAC verification and status normalization"
git push origin development
SCRIPT


What this gives you right now:

A single /webhooks/inbound endpoint that works for Sinch and Phaxio, with HMAC verification, trait gating, and status normalization into one canonical set.

Central traits and status maps in config/ so you don’t hardcode per-provider quirks throughout the codebase.

Minimal surfacing of “strict vs warn” via TRAITS_STRICT.

Suggested next tiny steps (one at a time):

Set env secrets on your server/CI:
PHAXIO_WEBHOOK_SECRET and SINCH_WEBHOOK_SECRET.

Flip TRAITS_STRICT=true in staging. Hit the inbound endpoint with a sample webhook to confirm signature checks and normalized event payloads.

In the Admin Console, hide/show inbound sections using supports_inbound and, where relevant, show a note if outbound_status_only=true.

If you want, I can extend this to outbound next: wrap send/status/cancel into the same adapters and gate those by traits too—still incremental, still small-team friendly.


SR. DEV COMMENTS: Sr Dev comments on v3_plans/traits-first-guardrails.md:1

  Overall

  - Strong direction. Making traits the single source of truth + enforcing them (UI + server + SDKs) will stop backend-name drift and eliminate surprises like
  the Sinch guidance regressions.

  What I’d add to make this succeed

  - Include UX meta inside traits (or a sibling providers_meta.json) so UI can render precise, backend‑specific help without bespoke copy:
      - inbound: endpoint, content_types, preferred_content_type, signed, register.supported + verbs + resource + body_variants, docs.setup/portal/api/oauth
      - outbound: auth.methods, preferred, oauth.token_url_hint
  - Version and validate the schema at startup
      - schema_version field, strict validation with readable errors exposed via /admin/traits/validate and surfaced in Diagnostics.
  - Enforce traits in code, not just describe them
      - @requires_traits(direction, keys=[…]) on sensitive endpoints (AMI originate/test, internal inbound handlers, storage ops).
      - OpenAPI x-faxbot-traits on each endpoint; Diagnostics cross‑check annotation vs runtime gating.
  - CI guardrails
      - ESLint rule forbidding backend string gates in UI; require hasTrait/traitValue via useTraits().
      - Grep/lint in server for literal “phaxio|sinch|sip” conditionals outside approved helpers.
  - Observability
      - ADMIN_DEBUG_PROVIDER toggle: log provider call status codes + short body (first 200 chars), always redact secrets; surface in Admin Console Logs. This
  makes “Register with <provider>” failures actionable.
  - Plugin parity
      - Allow HTTP provider manifests to declare traits + UX meta. Admin UI should read them the same way as native providers.

  Implementation plan (pragmatic)

  - Phase A (1–2 days)
      - Add providers_meta.json (or extend provider_traits.json) with the UX meta for Phaxio + Sinch first.
      - Add /admin/providers that returns { schema_version, active {outbound,inbound}, registry, meta }.
      - Wire Setup Wizard + Settings to read meta:
          - Render endpoint, preferred vs supported content types
          - Show visible buttons (Faxbot Setup, Provider Docs, Portal/Access Keys)
          - Provide “Copy curl (JSON)” and “Copy curl (multipart)” where applicable
          - Show Register button only when meta.register.supported
  - Phase B (2–3 days)
      - Implement @requires_traits; annotate endpoints with x-faxbot-traits.
      - Add /admin/traits/validate; surface warnings in Diagnostics.
      - Add ESLint + simple server grep check to block backend-string gates.
  - Phase C (2–3 days)
      - Extend meta for SignalWire, SIP/Asterisk (e.g., requires_ami, needs_storage), FreeSWITCH.
      - Add Admin Action “Webhook Test” that uses meta to test JSON/multipart from server and report exact HTTP status + short body snippet.
  - Phase D (1–2 days hardening)
      - Add ADMIN_DEBUG_PROVIDER; redact and surface to Logs.
      - Enable TRAITS_STRICT in staging; fix any stragglers; make strict default in next minor.

  MVP acceptance criteria

  - /admin/providers exposes traits + meta; UI renders backend‑specific help and copyable tests from it.
  - No UI backend-string gates remain in Settings/Setup Wizard (lint enforced).
  - Sensitive endpoints annotated + gated by @requires_traits.
  - Diagnostics shows traits + schema validation status.
  - Admin Console “Register with <provider>” and “Webhook Test” provide actionable error text.

  Decisions needed

  - Whether to embed UX meta in provider_traits.json or a sibling providers_meta.json. I recommend a sibling file to keep canonical trait keys clean and allow
  richer per‑provider hints.
  - Approval to add ADMIN_DEBUG_PROVIDER and to log provider status/body snippets (with strict redaction).
  - Codeowner for the traits/meta file so changes always go through review.

  Notes on current pain points this will fix

  - Sinch inbound confusion (JSON vs multipart) + “register” ambiguity will come from meta, so UI always presents a preferred + supported list and exact steps.
  - “Register with Sinch” will derive verbs/body variants from meta, not guess.
  - AMI UI controls never show under cloud backends; SIP‑only actions fail with capability_missing.

  If approved, I’ll start by drafting providers_meta.json entries for Phaxio and Sinch and wiring /admin/providers + UI consumption so we immediately get
  consistent, backend‑specific guidance without more one‑off copy.



MANAGER: COMMENTS: Manager: Green-light Phase 1 behind a flag. Scope is right; risks are API drift and client breakage. Mitigate with strict CI trait-lint, capability_missing error contract, and a 4‑phase rollout. Deliverables per milestone: M1 endpoints/hooks/docs; M2 middleware + endpoint annotations; M3 UI sweep + ESLint rule; M4 strict mode default. Success = zero backend-name checks in server/UI, trait-gated E2E tests passing across all backends, and no user-facing regressions. Assign DRIs (API, UI, QA), publish comms to app/SDK owners, and hold a readiness review before flipping TRAITS_STRICT in staging.


consultant: 

## Technical Review & Implementation Recommendations

After reviewing the codebase and current pain points, this traits-first approach is **critical** for Faxbot's success. Here's my analysis:

### Current State Assessment
The codebase shows significant backend-specific conditionals scattered across:
- **Admin UI**: 23+ direct backend string comparisons (`backend === 'phaxio'`, etc.)
- **Server logic**: Mixed provider-specific code without clear abstraction
- **Documentation**: Backend-specific guidance that creates user confusion (especially Sinch vs Phaxio)

### Key Strengths of This Proposal
1. **Eliminates fragile string comparisons** - The current `backend === 'phaxio'` pattern is brittle and error-prone
2. **Future-proofs plugin architecture** - Traits provide a stable contract for v3 plugins
3. **Reduces user confusion** - No more mixed backend guidance in UI
4. **Enables proper testing** - Trait-based behavior can be tested systematically

### Critical Implementation Details

#### Phase A Priority (Immediate Impact)
- **UX Meta Extension**: The Sr Dev's suggestion for `providers_meta.json` is essential. Current UI shows generic "Register with Provider" buttons that don't work for all backends.
- **Endpoint Consolidation**: `/admin/providers` should be the single source of truth, not scattered across multiple endpoints
- **Strict Schema Validation**: Schema drift is a real risk - startup validation with clear errors is mandatory

#### Backend-Specific Pain Points to Address
From the Sinch integration audit, these issues highlight why traits are needed:
- **Verification Confusion**: Sinch uses Basic auth, Phaxio uses HMAC - traits can encode this properly
- **Regional Endpoints**: Sinch needs `SINCH_BASE_URL` overrides - traits can indicate this capability
- **Status Mapping**: Each provider has different status vocabularies - traits can normalize this

#### UI Implementation Strategy
The current Admin Console has extensive backend conditionals that need systematic replacement:
```typescript
// Current anti-pattern (found 23+ instances)
{settings.backend.type === 'phaxio' && <PhaxioSettings />}

// Proposed pattern
const { hasTrait } = useTraits();
{hasTrait('outbound', 'supports_hmac_verification') && <HMACSettings />}
```

### Risk Mitigation Recommendations

#### 1. Migration Safety
- **Dual Mode**: Keep compatibility mode as default longer than planned (not just one minor release)
- **Gradual Rollout**: Start with new features only, then migrate existing code
- **Comprehensive Testing**: Each backend needs trait-based E2E tests

#### 2. Developer Experience
- **Clear Error Messages**: `capability_missing` errors must include actionable remediation
- **Documentation**: Every trait needs clear documentation with examples
- **Tooling**: ESLint rules should suggest trait-based alternatives, not just block string comparisons

#### 3. Plugin Ecosystem
- **Manifest Validation**: HTTP provider manifests need strict schema validation
- **Trait Inheritance**: Consider how plugin traits override/extend base provider traits
- **Registry Curation**: Plugin registry needs quality controls to prevent trait pollution

### Implementation Sequence Refinement

**Phase A (1-2 days)** - Foundation
- Implement `/admin/providers` with full UX meta
- Add schema validation with startup checks
- Create `useTraits()` hook with comprehensive helpers

**Phase B (2-3 days)** - Server Enforcement  
- Add `@requires_traits` middleware with clear error responses
- Implement OpenAPI `x-faxbot-traits` annotations
- Add `/admin/traits/validate` for CI/development visibility

**Phase C (3-4 days)** - UI Migration
- Systematic replacement of all backend string checks
- Add ESLint rule with auto-fix suggestions where possible
- Comprehensive Playwright tests for trait-based UI behavior

**Phase D (1-2 days)** - Hardening
- Enable `TRAITS_STRICT` in staging with comprehensive monitoring
- Add observability for trait violations
- Documentation updates and developer guides

### Success Metrics
- **Zero backend string comparisons** in UI/server code (enforced by CI)
- **All provider capabilities** discoverable via traits API
- **Plugin compatibility** - new providers work without core code changes
- **User experience** - no mixed backend guidance in any UI screen

This proposal addresses the core architectural debt that's causing user confusion and developer friction. The traits-first approach will make Faxbot significantly more maintainable and extensible.






























































































