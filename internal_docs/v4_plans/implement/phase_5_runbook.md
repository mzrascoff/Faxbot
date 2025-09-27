# Phase 5 Runbook — Production Excellence (auto-tunnel)

This runbook defines the pre-push smoke tests and acceptance gates to run locally for each Phase 5 PR before opening a PR targeting `auto-tunnel`.

Always follow AGENTS.md guardrails: traits over names, single `/metrics`, 202 for inbound callbacks with idempotency, and no PHI in logs.

## Standard Pre‑Push Smokes (every PR)

- Contract greps and guardrails
  - `bash scripts/ci/greps.sh || true`

- Build and start locally (detached)
  - `docker compose build && docker compose up -d`

- Health and metrics
  - `curl -fsS http://localhost:8080/health || true`
  - `curl -fsS http://localhost:8080/metrics | head -n 3 || true`

- Provider traits validation (schema + runtime issues)
  - `python3 scripts/ci/validate_provider_traits.py`
  - Optional: `curl -fsS -H "X-API-Key: ${API_KEY:-dev}" http://localhost:8080/admin/traits/validate | jq .issues`

- Admin providers registry
  - `curl -fsS -H "X-API-Key: ${API_KEY:-dev}" http://localhost:8080/admin/providers | jq .active`

- Callback 202 ACK smoke (non‑strict)
  - Phaxio: `curl -s -o /dev/null -w "%{http_code}\n" -X POST http://localhost:8080/phaxio-callback -H "X-Phaxio-Signature: test" -H "Content-Type: application/json" -d '{"id":"p5smoke","status":"success"}'`
  - Sinch: `curl -s -o /dev/null -w "%{http_code}\n" -X POST http://localhost:8080/sinch-inbound -H "Authorization: Basic dGVzdDp0ZXN0" -H "Content-Type: application/json" -d '{"id":"p5smoke"}'`

Note: In CI the callbacks may return 200 due to `FAXBOT_TEST_MODE`/`CALLBACK_COMPAT_200`; locally they should return 202 unless you set those flags.

## PR Loop (repeat per PR)

1) Branch from `auto-tunnel` and implement the minimal, atomic change.
2) Run the Standard Pre‑Push Smokes above; fix issues until green.
3) Push the feature branch and open a PR targeting `auto-tunnel` with:
   - Title: `P5-PRX: <short summary>`
   - Body: include the smoke outputs and affected files.
4) Wait for CI to go green (OpenAPI diff, traits schema, greps, builds). Auto‑merge is enabled; if anything stays pending or red, it did not merge.
5) After merge, `git checkout auto-tunnel && git pull` and run a sanity build: `docker compose build && docker compose up -d`.

## Definition of Done (Phase 5)

- One metrics endpoint at `/metrics` on API port; no duplicate Prometheus/OTel exporters.
- Inbound callbacks return 202 + are idempotent (dedupe by provider_id + external_id); no PHI in logs.
- Trait registry uses canonical keys where applicable: `webhook.path`, `webhook.verification`, `webhook.verify_header`, `auth.methods`, `regions`.
- Health monitor is the single Phase‑3 `ProviderHealthMonitor` (no duplicates).
- Sinch uses async I/O for file uploads; HumbleFax inbound path is webhook‑first (IMAP offloaded/threadpooled when enabled).
- Secrets enforced in deploy: `CONFIG_MASTER_KEY`, `FAXBOT_SESSION_PEPPER`.

## Quick Revert

If a PR slips through and causes issues on `auto-tunnel`:

```
git checkout auto-tunnel && git pull
git log --oneline  # copy the merge commit SHA
git revert -m 1 <merge-commit-sha>
git push
```

