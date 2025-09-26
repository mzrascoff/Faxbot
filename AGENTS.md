# AGENTS.md - Critical Instructions for AI Assistants

# CRITICAL: V4 MIGRATION IN PROGRESS
**FOR ANYTHING RELATED TO V4 AND THE MULTIPHASE V4 PLAN, STAY IN THE auto-tunnel branch**

Branching: All v4 phases (1–5) live in `auto-tunnel`. Merge to `development` via PR after green CI. Never commit directly to `main`.

**V4 Architecture Alert:**
- **Plugin-First**: Everything is becoming a plugin (providers, storage, identity)
- **7 Active Providers**: Sinch (#1 priority), Phaxio, HumbleFax, SignalWire, SIP/Asterisk, FreeSWITCH, Test
- **Configuration**: Database-first with .env fallback (no more config.yaml)
- **Authentication**: Dual mode - API keys + session-based auth
- **UI**: Admin Console is PRIMARY - no CLI-only features allowed
- **Backward Compatibility**: All v3 APIs continue to work during migration

## Project Identity: Faxbot

**Correct Name:** "Faxbot" (main project) and "faxbot-mcp" (MCP server)
**Status:** Production deployment capable, handling PHI/PII in healthcare environments
**Revolutionary:** First and only open source fax transmission system with AI assistant integration

**There has NEVER been an open source, locally hostable fax server API with AI assistant integration. EVER.** None of this exists in any AI training data. You **CANNOT** make assumptions about how this works, what patterns to follow, or what "normal" looks like.

**EVERY DECISION MUST BE BASED ON THE ACTUAL CODEBASE AND DOCUMENTATION PROVIDED**

## V4 Architecture Summary

### Core Changes
- **Plugin Manager**: Central orchestrator with manifest-first discovery (`api/app/plugins/<type>/<id>/manifest.json`)
- **Trait System**: Capabilities defined by traits, not hardcoded provider names
- **Hybrid Config**: Database-first configuration with .env fallbacks
- **Async Everything**: Non-blocking I/O throughout the stack
- **Dual Auth**: API keys (existing) + session-based (new) authentication
- **Admin Console First**: Every feature must have UI coverage

### Provider Implementation Status

| Provider | Priority | Auth | Inbound | Status | Critical Notes |
|----------|----------|------|---------|---------|----------------|
| **Sinch** | **#1 CRITICAL** | OAuth2/Basic | Webhook | Active | Most widely used, regional endpoints |
| **Phaxio** | **#2** | HMAC | Webhook | Active | HIPAA-ready, secure callbacks |
| **HumbleFax** | **#3** | API Key | Webhook+IMAP | Active | Complex dual inbound system |
| **SignalWire** | Standard | API Key | Webhook | Active | Twilio-compatible API |
| **SIP/Asterisk** | Self-host | AMI | Direct | Active | T.38 support, requires AMI |
| **FreeSWITCH** | Preview | ESL | Hook | v4 | mod_spandsp, ESL interface |
| **Test** | Dev | None | Mock | Active | Development/testing only |

## V4 Plugin System Guide

### Plugin Discovery & Loading
```python
# Get active provider (Python)
transport = await plugin_manager.get_active_by_type('transport')
result = await transport.send_fax(to_number, file_path)

# List all plugins by type
storage_plugins = await plugin_manager.list_by_type('storage')
```

### Trait-Based Logic
```typescript
// Check traits (TypeScript - canonical keys)
const traits = useTraits();
if (traits.has('webhook.verification', 'hmac_sha256')) {
    showHMACSettings();
}

// Python trait checking (canonical keys)
traits = await get_active_traits()
if traits.has('oauth2_supported'):
    await setup_oauth2_flow()
```

### Configuration Access
```python
# v4 Config Pattern (contextual)
user_ctx = UserContext(user_id="admin", tenant_id="default", groups=["admins"])
api_key = (await hierarchical_config.get_effective("phaxio.api_key", user_ctx)).value
webhook_url = (await hierarchical_config.get_effective("system.webhook_base_url", user_ctx)).value
```

**CRITICAL**: Never hardcode backend names. Always use plugin_manager and trait checking.

DB-first; .env fallback only if the database is unavailable. Defaults come from manifests.

## Admin Console First (GUI Mandate)

**North Star**: Complete GUI-first experience. Users should never need terminal for routine operations beyond starting Docker.

### Requirements for ALL Features
- [ ] Admin Console UI coverage (not just API)
- [ ] Inline help text and tooltips everywhere
- [ ] "Learn more" links to `${docsBase}/section`
- [ ] Mobile-first responsive design
- [ ] Error states with actionable guidance
- [ ] Backend isolation (show only active provider settings)
- [ ] Do not rename legacy routes; add new endpoints in parallel only
- [ ] Inbound handlers return 202 and are idempotent (dedupe by provider_id + external_id)

### Trait-Gated UI Pattern
```typescript
// Show provider-specific UI based on traits
const { activeProvider, traits } = useProviderConfig();
if (traits.hasTrait('inbound', 'requires_ami')) {
    return <AMIConfigSection />;
}
```

## Frontend Quick Reference

| Component | File | Purpose |
|-----------|------|---------|
| **App Shell** | `api/admin_ui/src/App.tsx:1` | Main app with tabs |
| **API Client** | `api/admin_ui/src/api/client.ts:1` | AdminAPIClient |
| **Theme** | `api/admin_ui/src/theme/themes.ts:1` | Dark/Light themes |
| **Form Kit** | `ResponsiveFormFields.tsx:1` | Form components |
| **Settings Kit** | `ResponsiveSettingItem.tsx:1` | Settings layouts |
| **Types** | `api/admin_ui/src/api/types.ts:1` | TypeScript types |

Note: Admin Console stays on API-key login until `/auth/*` + CSRF middleware ship. Cookie sessions are gated behind a feature flag. Mark the session login component disabled by default.

### Key Patterns
```typescript
// Responsive styling
sx={{ px: { xs: 1, sm: 2, md: 3 } }}

// Form validation
<ResponsiveTextField
  error={!!error}
  helperText={error || "Helper text"}
/>

// Theme usage
const theme = useTheme();
```

## Configuration Guide

### V4 Hybrid Config Priority
1. **Database** (tenant/user/global hierarchy)
2. **Environment variables** (.env fallback)
3. **Defaults** (manifest-defined)

### Critical Environment Variables
```env
# Core API
API_KEY=your_secure_api_key_here
FAX_BACKEND=sinch  # Primary provider
DATABASE_URL=postgresql://user:pass@host/db

# Provider Credentials (example)
SINCH_PROJECT_ID=your_project_id
SINCH_API_KEY=api_key
SINCH_API_SECRET=api_secret

# Security
ENFORCE_PUBLIC_HTTPS=true  # HIPAA environments
AUDIT_LOG_ENABLED=true     # Healthcare compliance
```

## Security Essentials

### HIPAA vs Non-HIPAA
| Setting | HIPAA Required | Non-HIPAA Default |
|---------|----------------|-------------------|
| `API_KEY` | Required strong key | Optional but recommended |
| `ENFORCE_PUBLIC_HTTPS` | `true` | `false` (dev only) |
| `AUDIT_LOG_ENABLED` | `true` | `false` |
| `PHAXIO_VERIFY_SIGNATURE` | `true` | `true` (recommended) |

### Never Log PHI
```python
# WRONG - logs phone number
logger.info(f"Sending fax to {to_number}")

# CORRECT - logs job ID only
logger.info(f"Sending fax job {job_id}")
```

- Fail-fast secrets: `CONFIG_MASTER_KEY` (44-char base64) and `FAXBOT_SESSION_PEPPER` are required; the app exits at startup if missing.
- Webhooks: 202 Accepted + idempotency; PHI never logged.
- Sessions: CSRF required for all state-changing endpoints when cookie sessions are enabled.

## Branch Policy (V4 Critical)

| Work Type | Target Branch | Notes |
|-----------|---------------|-------|
| **Core API/MCP/Docs** | `auto-tunnel` | All v4 work (Phases 1–5). Merge to `development` via PR after green CI |
| **Electron macOS** | `electron_macos` | App-specific |
| **Electron Windows** | `electron_windows` | App-specific |
| **iOS App** | `iOS` | App-specific |
| **Production** | `main` | **NEVER WORK IN MAIN** |

## Quick Scripts (Keep Updated)

### One-Command API Docs Refresh
```bash
# Local only - publishes to faxbot.net
scripts/publish-api-docs.sh
```

### Admin Console Demo Sync
```bash
# From faxbot.net repo
./scripts/update-demo.sh --force-main
```

## V4 Migration Checklist

### For Every Code Change
- [ ] Using `plugin_manager` instead of direct service calls?
- [ ] Checking traits instead of backend names (`providerHasTrait()`)?
- [ ] Using async/await for all I/O operations?
- [ ] Config via `HybridConfigProvider`, not hardcoded values?
- [ ] Admin Console UI included for new features?
- [ ] Backward compatibility maintained for existing API clients?
- [ ] No PHI in logs (use job IDs, not phone numbers/content)?

### Code Pattern Checklist
```python
# ✅ CORRECT v4 Pattern
transport = await plugin_manager.get_active_by_type('transport')
if await provider_has_trait('outbound', 'oauth2_required'):
    token = await oauth_handler.get_token()
    result = await transport.send_fax(to_number, file_path, auth=token)

# ❌ WRONG v3 Pattern
if backend == 'sinch':
    sinch_service.send_fax(...)
elif backend == 'phaxio':
    phaxio_service.send_fax(...)
```

## Common Anti-Patterns (AVOID)

| Anti-Pattern | Problem | v4 Solution |
|-------------|---------|-------------|
| `if backend == 'phaxio'` | Hardcoded provider | `if provider_has_trait('webhook', 'hmac')` |
| Direct service imports | Breaks plugin system | Use `plugin_manager.get_active_by_type()` |
| Mixed backend UI | Confuses users | Show only active provider settings |
| Blocking I/O | Performance issues | Use async/await everywhere |
| CLI-only features | Poor UX | Admin Console coverage required |

## Provider-Specific Critical Notes

### Sinch (Priority #1)
- **Auth**: `auth.methods = ["basic","oauth2"]` support required
- **Regional endpoints** (US, EU, etc.)
- **Fallback semantics**: Only documented key/secret fallbacks (e.g., `PHAXIO_*` to Sinch key/secret) apply. Do not infer project IDs from Phaxio keys.

### HumbleFax (Complex)
- **Dual inbound**: Webhook + IMAP polling
- **Rate limiting**: Strict API limits
- **Webhook verification**: Custom HMAC implementation
 - **IMAP**: Run threadpooled/worker-based; never block the event loop.

### SIP/Asterisk (Self-Hosted)
- **AMI credentials** required (`ASTERISK_AMI_*`)
- **T.38 protocol** for fax transmission
- **Network isolation** (keep AMI internal)

## Final Critical Reminders

1. **This has never existed before** - No assumptions allowed about fax+AI systems
2. **All 7 providers must work** - Sinch priority #1, but all must function
3. **Plugin-first mindset** - Everything is a plugin in v4
4. **Traits over names** - Check capabilities, not hardcoded provider strings
5. **Admin Console mandatory** - Every feature needs UI coverage
6. **HIPAA is critical** - Healthcare compliance built-in, not bolted-on
7. **Backward compatibility** - v3 APIs must continue working during migration

## Observability

- Expose exactly one metrics endpoint (`/metrics` on API port).
- Use the Phase-3 health monitor and circuit breaker; do not add duplicate monitors.

## Dev/Prod Golden Path

Dev: Docker Compose is canonical. Prod: Kubernetes. Bare-metal is unsupported to avoid Ghostscript/Node drift.

## CI Guardrails

- OpenAPI diff against pinned snapshot (fail on route/schema drift).
- Traits JSON-Schema validation (fail on non-canonical keys/types):
  - `webhook.path` (string), `webhook.verification` (`hmac_sha256|basic_auth|none`), `webhook.verify_header` (string)
  - `auth.methods` (array of enums), `regions` (array)
- Grep checks:
  - No provider name checks in UI: `rg -n "=== 'sinch'|=== 'phaxio'|=== 'sip'" api/admin_ui/src`
  - Require 202 in callback handlers: `rg -n "/(phaxio|sinch).*return.*202" api/app`
  - No duplicate health monitors: `rg -n "class .*ProviderHealthMonitor" api/app`
  - Secrets present in env/k8s: `CONFIG_MASTER_KEY|FAXBOT_SESSION_PEPPER`

## North Star

Brownfield integration rule: We are upgrading a live system. Never rename existing routes or remove working flows. Add new capabilities behind traits, feature flags, and Admin Console UI. Return 202 for inbound callbacks and dedupe idempotently. DB-first config with .env as a true outage fallback only. Traits over names, plugins over services, Docker/K8s over bare-metal, and no PHI in logs. If a change breaks any of those, stop and fix the plan.

**Remember**: You are building the first open source fax server with AI integration. Your work defines how this category of software will be understood for years to come.