Phase 2 Runbook — Trait-Based Auth & User Management (into auto-tunnel)
Feature flags & required env

Add these to .env (dev) and your secret stores (stage/prod):

# Phase 2 global toggles
FAXBOT_SESSIONS_ENABLED=false
FAXBOT_CSRF_ENABLED=false

# Security (REQUIRED)
CONFIG_MASTER_KEY=<44-char base64 fernet>        # fail fast if missing
FAXBOT_SESSION_PEPPER=<random hex 64>           # fail fast if missing

# Optional bootstrap
FAXBOT_BOOTSTRAP_PASSWORD=<one-time admin password>  # unset after first use


Rule: Admin Console stays on API-key auth until you explicitly switch FAXBOT_SESSIONS_ENABLED=true (late in Phase 2).

Database models & Alembic migrations (async-ready)
1) Models (place in api/app/plugins/identity/providers/sqlalchemy.py)

(If they don’t exist already; align names if they do.)

# Models (as provided earlier, unchanged), ensure importable by Alembic:
# DBUser, DBGroup, DBSession, user_groups (Table)

2) Alembic revision (create + upgrade)

Create an Alembic migration for Phase 2:

# from repo root
bash -lc 'set -euo pipefail \
&& alembic revision -m "phase2 users, groups, sessions" --autogenerate \
&& alembic upgrade head'


If you don’t autogenerate, create versions/<ts>_phase2.py with explicit DDL:

# alembic migration skeleton (explicit, safe)
from alembic import op
import sqlalchemy as sa

revision = "phase2_users_groups_sessions"
down_revision = "<prev>"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.String(40), primary_key=True),
        sa.Column("username", sa.String(100), nullable=False, unique=True, index=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("password_hash", sa.String(200), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("traits", sa.Text(), nullable=True),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("last_login", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "groups",
        sa.Column("id", sa.String(40), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True, index=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("traits", sa.Text(), nullable=True),
        sa.Column("parent_group_id", sa.String(40), sa.ForeignKey("groups.id"), nullable=True),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "user_groups",
        sa.Column("user_id", sa.String(40), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("group_id", sa.String(40), sa.ForeignKey("groups.id"), primary_key=True),
    )

    op.create_table(
        "user_sessions",
        sa.Column("token", sa.String(128), primary_key=True, index=True),
        sa.Column("user_id", sa.String(40), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("last_activity", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("traits", sa.Text(), nullable=True),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
    )

def downgrade():
    op.drop_table("user_sessions")
    op.drop_table("user_groups")
    op.drop_table("groups")
    op.drop_table("users")

PR sequence (into auto-tunnel) — small steps with acceptance gates

Prepend the same Meta header you used for Phase 1 PRs (branch, rules, no route renames, 202 on callbacks, etc.).

PR6 — Typed bases for Identity + Async DB invariants

Goal: add IdentityPlugin base, async SQLA patterns, and Argon2id helpers; no UI change.

Touch

api/app/plugins/base.py — ensure FaxbotPlugin exists (Phase 1).

api/app/plugins/identity/base.py — IdentityPlugin, IdentityProvider, dataclasses User/Group/Session/AuthResult (as given).

api/app/db/async.py — AsyncSessionLocal, engine (async).

api/app/core/security.py — add AuthContext, DualSecurityCore skeleton (session path returns None if disabled).

Acceptance

rg -n "class IdentityProvider" api/app | wc -l → 1

No db.query(...).first() in new code (use select()/await).

Smoke

bash -lc 'set -e && docker compose build && docker compose up -d && rg -n "\.query\(" api/app | rg -v "tests?/" || true'

PR7 — SQLA Identity Provider (Argon2id + session hashing/pepper)

Goal: working SQLAlchemy identity provider with peppered session tokens (no UI switch yet).

Touch

api/app/plugins/identity/providers/sqlalchemy.py — the full, async provider (use the code you already have, but fix all .query → select).

Hash sessions with FAXBOT_SESSION_PEPPER (_hash_token()); store hash not raw.

Acceptance

rg -n "_hash_token|argon2\.PasswordHasher" api/app | wc -l → ≥2

Missing envs cause startup fail (guard in app bootstrap): CONFIG_MASTER_KEY and FAXBOT_SESSION_PEPPER.

Smoke

bash -lc 'set -e && docker compose build && docker compose up -d \
&& (docker compose logs api | rg -n "CONFIG_MASTER_KEY|FAXBOT_SESSION_PEPPER" && false || true)'

PR8 — /auth endpoints (behind flag), CSRF middleware

Goal: add /auth/login|logout|refresh|me and CSRF middleware; keep FAXBOT_SESSIONS_ENABLED=false by default.

Touch

api/app/routers/auth.py — endpoints from your spec (return 503 if sessions disabled).

api/app/middleware/csrf.py — CSRF as provided; only active if both FAXBOT_SESSIONS_ENABLED=true and FAXBOT_CSRF_ENABLED=true.

api/app/main.py — mount the router & conditional CSRF.

Acceptance

curl -s -o /dev/null -w "%{http_code}\n" -X POST http://localhost:8080/auth/login → 503 (disabled), not 404.

Smoke

bash -lc 'set -e && docker compose build && docker compose up -d \
&& code=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8080/auth/login); echo $code'

PR9 — UnifiedAuthMiddleware (cookie+API key), session activity update

Goal: request pipeline that accepts both API keys and cookies; does not flip UI.

Touch

api/app/middleware/auth.py — full middleware from your spec; cookie first, then Bearer, then X-API-Key.

Backward compatibility: set request.state.auth_info for legacy handlers.

Acceptance

/health works unauthenticated.

Protected endpoint returns 401 without API key or session.

Smoke

bash -lc 'set -e && docker compose build && docker compose up -d \
&& curl -fsS http://localhost:8080/health || true \
&& curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/admin/providers'

PR10 — /admin/ui-config (ETag) + UI fetch (read-only)

Goal: provide trait-based UI config via /admin/ui-config (ETag, private cache).

Touch

api/app/routers/ui_config.py — as given.

UI: add a small client hook to fetch it (read-only; don’t switch login UX yet).

Acceptance

curl -fsS -H 'X-API-Key: dev' http://localhost:8080/admin/ui-config | jq .traits → array

Repeat with If-None-Match returns 304.

Smoke

bash -lc 'set -e && docker compose build && docker compose up -d \
&& etag=$(curl -fsSI -H "X-API-Key: ${API_KEY:-dev}" http://localhost:8080/admin/ui-config | rg -i "^etag:" | awk "{print \$2}" | tr -d "\r") \
&& curl -s -o /dev/null -w "%{http_code}\n" -H "If-None-Match: $etag" -H "X-API-Key: ${API_KEY:-dev}" http://localhost:8080/admin/ui-config'

PR11 — Admin UI: User Management (read-only first)

Goal: add UserManagement.tsx (list only); no edits until endpoints exist.

Touch

api/admin_ui/src/components/UserManagement.tsx — use the concrete code you posted (list users, trait chips, enable/disable once API is ready).

Add it to App tabs (trait-gated by admin_capable).

Acceptance

Rendering works; if /admin/users doesn’t exist yet, the component shows a friendly error banner.

Smoke

bash -lc 'set -e && docker compose up -d && echo "Open Admin -> User Management (should render)."' 

PR12 — /admin/users endpoints (list/create/patch minimal)

Goal: backing endpoints for the UI (minimal CRUD; no PII in logs).

Touch

api/app/routers/admin_users.py — GET /admin/users, POST /admin/users, PATCH /admin/users/{id}; enforce perm admin.users:*.

Use async SQLA; hash password with Argon2id; never return password_hash.

Acceptance

GET /admin/users returns {"users":[...]}; POST with minimal fields creates a user; PATCH toggles is_active.

Smoke

bash -lc 'set -e && docker compose build && docker compose up -d \
&& curl -fsS -H "X-API-Key: ${API_KEY:-dev}" http://localhost:8080/admin/users | jq .'

CI gates (fast, deterministic)

OpenAPI diff — fail if any existing route schema changes.

Traits schema — validate provider_traits.json (already in PR0).

Greps (augment scripts/ci/greps.sh):

# No bare metal secrets missing
rg -n "CONFIG_MASTER_KEY|FAXBOT_SESSION_PEPPER" deployment docker-compose* || exit 1
# Only one ProviderHealthMonitor
[ "$(rg -n "class .*ProviderHealthMonitor" api/app | wc -l)" -eq 1 ] || exit 1
# Webhooks return 202 (Phase 1)
rg -n "return .*status_code=202" api/app | rg "(phaxio|sinch).*(callback|inbound)"
# No UI provider name checks remain
[ "$(rg -n "=== 'sinch'|=== 'phaxio'|=== 'sip'" api/admin_ui/src | wc -l)" -eq 0 ] || exit 1


Contract gate (Phase 2) — new:

# /auth exists (but may be disabled)
rg -n "@router\.(get|post)\(\"/auth/(login|logout|refresh|me)" api/app
# CSRF middleware present
rg -n "class CSRFMiddleware" api/app/middleware
# Session tokens not stored raw (hash function present)
rg -n "def _hash_token" api/app

Rollout plan

Merge PR6–PR10 with FAXBOT_SESSIONS_ENABLED=false.

In staging only, set FAXBOT_SESSIONS_ENABLED=true and FAXBOT_CSRF_ENABLED=true; test Admin Console login/logout/refresh with cookie sessions.

Keep API-key flow intact (legacy clients unaffected).

Merge PR11–PR12; verify user management flows.

Flip flags in production when ready.

Backout plan

Single PR revert: git revert -m 1 <merge-sha> on auto-tunnel.

If cookies cause issues, set:

FAXBOT_SESSIONS_ENABLED=false
FAXBOT_CSRF_ENABLED=false


(Admin Console continues with API-key.)

Contract smokes (per PR; not full E2E)
bash -lc 'set -e \
&& docker compose build && docker compose up -d \
&& curl -fsS http://localhost:8080/metrics | head -n 3 || true \
&& curl -s -o /dev/null -w "%{http_code}\n" -X POST http://localhost:8080/phaxio-callback \
     -H "X-Phaxio-Signature: test" -H "Content-Type: application/json" -d "{\"id\":\"p2smoke\",\"status\":\"success\"}" \
&& curl -s -o /dev/null -w "%{http_code}\n" -X POST http://localhost:8080/sinch-inbound \
     -H "Authorization: Basic dGVzdDp0ZXN0" -H "Content-Type: application/json" -d "{\"id\":\"p2smoke\"}"'

Phase 2 “Definition of Done”

Cookie sessions available and CSRF-protected (flag-controlled).

API-key clients work unchanged.

IdentityProvider (SQLA) functional with Argon2id, token peppering.

Permissions derived from traits; legacy scopes mapped for Admin.

User Management available in Admin Console (list, create, toggle active).

No PHI/secrets in logs; privacy linter present.

Performance targets: session lookup ≤ 5 ms p95; trait resolution ≤ 2 ms p95.

If you want, I’ll format Codex prompts for PR6–PR12 exactly like we did for Phase 1 (copy-paste, with file lists and acceptance).

You said:
yes please 
ChatGPT said:

awesome — here are paste-ready Codex prompts for PR6 → PR12, in the same style as before. Each one includes scope, exact files to touch, concrete implementation notes/snippets (no pseudo), acceptance greps, and a quick contract smoke. All PRs target auto-tunnel.

Prepend this Meta header at the top of each PR prompt:

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

"""""
# Prompts

PR6 — Typed Identity bases + Async DB invariants (no UI change)

Goal: Add typed identity bases (IdentityPlugin / IdentityProvider) and ensure we use Async SQLAlchemy patterns everywhere (no db.query(...).first() in async code).

Touch only

api/app/plugins/base.py — ensure FaxbotPlugin exists (from Phase-1). If missing, add the minimal base (async initialize/shutdown).

api/app/plugins/identity/base.py — add:

IdentityPlugin(FaxbotPlugin) with plugin_type="identity", traits={"user_auth","session_mgmt"}.

Dataclasses: User, Group, Session, AuthResult (as in Phase-2 plan).

Abstract IdentityProvider methods (authenticate/get_user/create_session/etc.).

api/app/db/async.py — export AsyncSessionLocal and engine (async).

Implementation notes

Use select() + await db.execute(select(...)) pattern for all examples in this file.

Do not add any concrete provider here.

Acceptance

rg -n "class IdentityProvider" api/app | wc -l → 1

rg -n "\.query\(" api/app | rg -v "tests?/" returns no matches inside newly-touched identity files.

Contract smoke

bash -lc 'set -e && docker compose build && docker compose up -d \
&& rg -n "class IdentityProvider" api/app \
&& (rg -n "\.query\(" api/app | rg -v "tests?/" && false || echo "no sync .query in async code")'

PR7 — SQLAlchemy Identity Provider (Argon2id + peppered session tokens)

Goal: Implement a default SQLAlchemy identity provider, hashing passwords with Argon2id and storing peppered hashes of session tokens (never raw).

Touch only

api/app/plugins/identity/providers/sqlalchemy.py — implement the concrete provider using the async patterns:

Models: DBUser, DBGroup, DBSession, user_groups (if not already defined elsewhere).

Methods: authenticate, get_user*, create_session, validate_session, refresh_session, revoke_*, and _create_default_admin.

Token hashing:

import os, hmac, hashlib, secrets
PEPPER = os.environ["FAXBOT_SESSION_PEPPER"].encode()
def _hash_token(raw: str) -> str:
    return hmac.new(PEPPER, raw.encode(), hashlib.sha256).hexdigest()


Store _hash_token(raw) in DB, return raw only to client (cookie in later PR).

Acceptance

rg -n "argon2\.PasswordHasher" api/app | wc -l → 1+

rg -n "def _hash_token" api/app | wc -l → 1

API process fails fast on missing FAXBOT_SESSION_PEPPER and CONFIG_MASTER_KEY (wire a startup check if not present already).

Contract smoke

bash -lc 'set -e && docker compose build && docker compose up -d \
&& (docker compose logs api | rg -n "FAXBOT_SESSION_PEPPER|CONFIG_MASTER_KEY" && false || echo "env OK or guarded")'

PR8 — /auth endpoints (behind flag) + CSRF middleware

Goal: Add /auth/login, /auth/logout, /auth/refresh, /auth/me; keep disabled by default via FAXBOT_SESSIONS_ENABLED=false. Add CSRF middleware gated by FAXBOT_CSRF_ENABLED=true.

Touch only

api/app/routers/auth.py — endpoints exactly as in the plan.

If FAXBOT_SESSIONS_ENABLED=false, login returns 503 "Sessions disabled".

api/app/middleware/csrf.py — the CSRF middleware from the plan (cookie fb_csrf + header x-csrf-token), enabled only when both flags are true.

api/app/main.py — include the router and mount CSRF conditionally based on env flags.

Acceptance

curl -s -o /dev/null -w "%{http_code}\n" -X POST http://localhost:8080/auth/login → 503 (disabled), not 404.

CSRF middleware file present:
rg -n "class CSRFMiddleware" api/app/middleware/csrf.py

Contract smoke

bash -lc 'set -e && docker compose build && docker compose up -d \
&& code=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8080/auth/login); echo $code \
&& rg -n "class CSRFMiddleware" api/app/middleware'

PR9 — UnifiedAuthMiddleware (cookie + API key), session activity update

Goal: Authenticate requests via cookie (preferred) or API key, with legacy request.state.auth_info populated for backward compatibility. Update session last_activity on each request.

Touch only

api/app/middleware/auth.py — implement exactly as spec:

Public paths pass through (/docs, /openapi.json, /health, /auth/login).

Extract cookie fb_session, else Authorization: Bearer, else X-API-Key.

On session path, call validate_session() and set request.state.auth_context.

Back-compat: set request.state.auth_info (legacy shape).

On success, call next; on protected path without auth → 401.

Acceptance

/health returns 200 without auth.

/admin/providers returns 401 without API key or cookie.

Contract smoke

bash -lc 'set -e && docker compose build && docker compose up -d \
&& curl -fsS http://localhost:8080/health || true \
&& curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/admin/providers'

PR10 — /admin/ui-config (ETag) + minimal UI fetch hook

Goal: Serve trait-based UI config at /admin/ui-config with ETag; UI reads it (no login UX change yet).

Touch only

api/app/routers/ui_config.py — endpoint per plan (ETag, private cache, returns traits/permissions/ui_adaptations).

Optional: a tiny UI hook fetching /admin/ui-config on Admin mount (read-only).

Acceptance

First GET returns 200 with JSON; second GET with If-None-Match returns 304.

Contract smoke

bash -lc 'set -e && docker compose build && docker compose up -d \
&& etag=$(curl -fsSI -H "X-API-Key: ${API_KEY:-dev}" http://localhost:8080/admin/ui-config | rg -i "^etag:" | awk "{print \$2}" | tr -d "\r") \
&& echo $etag && curl -s -o /dev/null -w "%{http_code}\n" -H "If-None-Match: $etag" -H "X-API-Key: ${API_KEY:-dev}" http://localhost:8080/admin/ui-config'

PR11 — Admin UI: User Management (list-first)

Goal: Add UserManagement.tsx in Admin Console (list users; create/toggle wires can 400 gracefully if API isn’t there yet). Trait-gate tab on admin_capable.

Touch only

api/admin_ui/src/components/UserManagement.tsx — use the concrete component you drafted (list users; edit later).

api/admin_ui/src/App.tsx — add the tab/menu entry, gated by admin_capable trait; keep responsive kits & docsBase links.

Acceptance

Component renders; if /admin/users not implemented yet, shows friendly error banner.

Contract smoke

bash -lc 'set -e && docker compose up -d && echo "Open Admin > User Management (read-only list). Expect graceful error if backend absent."'

PR12 — Admin Users API (list/create/patch minimal)

Goal: Back endpoints for the UI — list users, create user, toggle active. Enforce permission admin.users:*. No PHI in logs.

Touch only

api/app/routers/admin_users.py — endpoints:

GET /admin/users → {users: [...]} (id, username, email, full_name, is_active, traits, groups, created_at, last_login).

POST /admin/users → create (Argon2id password hash; never return password hash).

PATCH /admin/users/{id} → toggle is_active.

Wire Argon2id hashing helper from the provider module (or share a util).

Enforce permission using DualSecurityCore.authorize_action(...).

Acceptance

GET /admin/users returns a JSON list with no secrets.

POST creates a user (400 on missing fields).

PATCH toggles active.

Contract smoke

bash -lc 'set -e && docker compose build && docker compose up -d \
&& curl -fsS -H "X-API-Key: ${API_KEY:-dev}" http://localhost:8080/admin/users | jq . | head -n 40'

CI reminders (for PR6–PR12)

Keep the OpenAPI diff and traits schema validations from Phase 1.

Extend scripts/ci/greps.sh with:

# /auth endpoints present
rg -n "@router\.(get|post)\(\"/auth/(login|logout|refresh|me)" api/app

# CSRF middleware present (and imported)
rg -n "class CSRFMiddleware" api/app/middleware

# Session hashing util present
rg -n "def _hash_token" api/app

# No sync .query in identity provider
rg -n "\.query\(" api/app/plugins/identity | rg -v "tests?/" && exit 1 || true

Rollout

Merge PR6–PR10 with FAXBOT_SESSIONS_ENABLED=false and FAXBOT_CSRF_ENABLED=false.

In staging, set both flags true; test cookie login/logout/refresh for Admin only.

Merge PR11–PR12; verify User Management works.

When stable, enable flags in production.