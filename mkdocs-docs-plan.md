# Docs Autopilot Plan (heuristic)
Base: origin/development

## Changed files

## Suggested updates
- No high‑signal changes detected; run periodic doc hygiene (links, anchors).

## Context snapshots
### AGENTS.md (excerpt)
# AGENTS.md - Critical Instructions for AI Assistants

Important: When you create a useful developer script or helper, add it to this file under "Quick Scripts" so it’s discoverable and maintained. Avoid one-off hacks that get lost.


There has **NEVER** been an open source, locally hostable fax server API with AI assistant integration. **EVER.** None of this exists in any AI training data. You **CANNOT** make assumptions about how this works, what patterns to follow, or what "normal" looks like.

**EVERY DECISION MUST BE BASED ON THE ACTUAL CODEBASE AND DOCUMENTATION PROVIDED**

## Project Identity: Faxbot

**Correct Name:** "Faxbot" (main project) and "faxbot-mcp" (MCP server)  

**Status:** Production deployment capable, handling PHI/PII in healthcare environments

## Revolutionary Architecture Overview (v3 Modular Plugins)

Faxbot is the first and only open source fax transmission system that combines:

1. **Modular Provider Plugins (v3)** — Outbound, inbound, auth, and storage provider slots are resolved at runtime via a single config file. Providers are implemented as plugins (Python for backend execution; Node plugins for MCP/UI helpers only).
2. **Multiple Backends via Plugins** — Cloud (Phaxio, Sinch), Self‑hosted (SIP/Asterisk), and Test Mode are expressed as plugins bound to provider slots.
3. **AI Assistant Integration** — Two MCP servers (Node + Python) with three transports each (stdio/HTTP/SSE) derive tools from active capabilities.
4. **Developer SDKs** — Node.js and Python with identical APIs (OpenAPI alignment), stable error mapping.
5. **HIPAA Compliance** — Built‑in controls for healthcare PHI handling across plugins (HMAC verification, secure storage options, no secret logging).
6. **Non‑Healthcare Flexibility** — Configurable security for non‑PHI scenarios; safe defaults remain available.

**Architecture Flow:**
```
AI Assistant (Claude) → MCP Server → Fax API → Backend → Fax Transmission
    ↓                      ↓            ↓         ↓
SDK Client          → Fax API → Backend → Fax Transmission
```

## Admin Console First (GUI Mandate)

**Effective immediately, Faxbot’s north star is a complete, GUI-first experience through the Admin Console. Users should never need a terminal for routine operations beyond starting the Docker container/console.**

What this means for all agents and contributors
- No CLI-only features: every capability must be operable from the Admin Console.
- UX completeness: every setting, diagnostic, and job view includes inline help and deep links to docs.
- Contextual help everywhere: tooltips, helper text, and “Learn more” links across all screens.
- Backend isolation in the UI: show provider-specific guidance only for the selected backend.
- Mobile-first polish: layouts, spacing, and controls must be legible and usable on phones.

v3 UI additions
- Plugins tab: manage active provider plugins with enable/disable toggles and schema‑driven config forms.
- Curated registry search: discover available pl

### provider_traits.json (excerpt)
{
  "_schema": {
    "version": 1,
    "canonical_trait_keys": [
      "requires_ghostscript",
      "requires_ami",
      "requires_tiff",
      "supports_inbound",
      "inbound_verification",
      "needs_storage",
      "outbound_status_only"
    ],
    "notes": "This file is JSON (no comments). Traits apply to provider ids. Manifest traits override these defaults."
  },
  "phaxio": {
    "id": "phaxio",
    "kind": "cloud",
    "traits": {
      "requires_ghostscript": true,
      "requires_ami": false,
      "requires_tiff": false,
      "supports_inbound": true,
      "inbound_verification": "hmac",
      "needs_storage": true,
      "outbound_status_only": false
    }
  },
  "sinch": {
    "id": "sinch",
    "kind": "cloud",
    "traits": {
      "requires_ghostscript": true,
      "requires_ami": false,
      "requires_tiff": false,
      "supports_inbound": true,
      "inbound_verification": "basic",
      "needs_storage": true,
      "outbound_status_only": false
    }
  },
  "signalwire": {
    "id": "signalwire",
    "kind": "cloud",
    "traits": {
      "requires_ghostscript": true,
      "requires_ami": false,
      "requires_tiff": false,
      "supports_inbound": false,
      "inbound_verification": "none",
      "needs_storage": false,
      "outbound_status_only": true
    }
  },
  "documo": {
    "id": "documo",
    "kind": "cloud",
    "traits": {
      "requires_ghostscript": true,
      "requires_ami": false,
      "requires_tiff": false,
      "supports_inbound": false,
      "inbound_verification": "none",
      "needs_storage": false,
      "outbound_status_only": false
    }
  },
  "sip": {
    "id": "sip",
    "kind": "self_hosted",
    "traits": {
      "requires_ghostscript": true,
      "requires_ami": true,
      "requires_tiff": true,
      "supports_inbound": true,
      "inbound_verification": "internal_secret",
      "needs_storage": true,
      "outbound_status_only": false
    }
  },
  "freeswitch": {
    "id": "freeswitch",


### .env.example (excerpt)
# API Configuration
# Note: In Docker, /faxdata is mounted as a volume (see compose)
FAX_DATA_DIR=/faxdata
MAX_FILE_SIZE_MB=10
FAX_DISABLED=false
API_KEY=your_secure_api_key_here
# Enforce API key on all requests even if API_KEY is blank (recommended for HIPAA prod)
REQUIRE_API_KEY=false

# Backend Selection - Choose ONE or use hybrid configuration
# Options: "sip" (self-hosted), "phaxio" (cloud fetch), or "sinch" (cloud direct upload)
FAX_BACKEND=sip

# === HYBRID BACKEND CONFIGURATION (v3+) ===
# Override FAX_BACKEND for independent outbound/inbound providers
# FAX_OUTBOUND_BACKEND=sinch     # Provider for sending faxes
# FAX_INBOUND_BACKEND=sip        # Provider for receiving faxes
# If unset, both directions use FAX_BACKEND value

# === PHAXIO CLOUD BACKEND ===
# Only needed if FAX_BACKEND=phaxio
PHAXIO_API_KEY=your_phaxio_api_key_here
PHAXIO_API_SECRET=your_phaxio_api_secret_here
PUBLIC_API_URL=http://localhost:8080
# Preferred name per docs
PHAXIO_CALLBACK_URL=http://localhost:8080/phaxio-callback
# Backward‑compatible alias (either variable is accepted)
# PHAXIO_STATUS_CALLBACK_URL=http://localhost:8080/phaxio-callback
PHAXIO_VERIFY_SIGNATURE=true
ENFORCE_PUBLIC_HTTPS=false

# === SINCH FAX API v3 (Phaxio by Sinch) ===
# Only needed if FAX_BACKEND=sinch
# If left blank, SINCH_API_* fall back to PHAXIO_* values.
SINCH_PROJECT_ID=your_sinch_project_id
SINCH_API_KEY=
SINCH_API_SECRET=
# Optional region override (defaults to https://fax.api.sinch.com/v3)
# SINCH_BASE_URL=https://us.fax.api.sinch.com/v3

# === MCP SSE (OAuth2/JWT) ===
# Set these when running SSE transports (Node or Python)
OAUTH_ISSUER=
OAUTH_AUDIENCE=faxbot-mcp
OAUTH_JWKS_URL=

# === SIP/ASTERISK BACKEND ===
# Only needed if FAX_BACKEND=sip
ASTERISK_AMI_HOST=asterisk
ASTERISK_AMI_PORT=5038
ASTERISK_AMI_USERNAME=api
# WARNING: Change this in production. Do NOT leave as 'changeme'.
ASTERISK_AMI_PASSWORD=changeme

# SIP Trunk Settings (from your provider)
SIP_USERNAME=17209000233
SIP_PASSWORD=eqdcM

### OpenAPI (truncated)
{
  "openapi": "3.1.0",
  "info": {
    "title": "Faxbot API",
    "description": "The first and only open-source, self-hostable fax API. Send faxes with a single function call.",
    "contact": {
      "name": "Faxbot Support",
      "url": "https://faxbot.net/",
      "email": "support@faxbot.net"
    },
    "license": {
      "name": "MIT",
      "url": "https://github.com/dmontgomery40/faxbot/blob/main/LICENSE"
    },
    "version": "1.0.0"
  },
  "paths": {
    "/health": {
      "get": {
        "summary": "Health",
        "operationId": "health_health_get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          }
        }
      }
    },
    "/health/ready": {
      "get": {
        "summary": "Health Ready",
        "description": "Readiness probe. Returns 200 when core dependencies are ready.\nChecks: DB connectivity; backend configuration; storage configuration when inbound is enabled.",
        "operationId": "health_ready_health_ready_get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {}
              }
            }
          }
        }
      }
    },
    "/admin/config": {
      "get": {
        "summary": "Get Admin Config",
        "description": "Return sanitized effective configuration for operators.\nDoes not include secrets. Requires admin auth (bootstrap env key or keys:manage).",
        "operationId": "get_admin_config_admin_config_get",
        "parameters": [
          {
            "name": "x-api-key",
            "in": "header",
            "required": false,
            "schema": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
              