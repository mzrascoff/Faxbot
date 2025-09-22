<p align="center">
  <img src="assets/faxbot_full_logo.png" alt="Faxbot logo" width="100%" />
</p>

<p align="center">
  <a href="https://dmontgomery40.github.io/Faxbot/">
    <img alt="View the Documentation" src="https://img.shields.io/badge/Docs-Faxbot-2b5fff?style=for-the-badge">
  </a>
</p>

The first and only open‑source, self‑hostable fax platform with a GUI‑first Admin Console, multi‑backend adapters (cloud + self‑hosted), and AI assistant integration.

## GUI‑first: Admin Console
- One place to configure backends, keys, inbound, storage, and run diagnostics.
- Open http://localhost:8080 and use the Admin Console (served by the API).
- Traits‑first UI: screens render only what your active provider supports.

## Why Faxbot
- One API, many backends: Phaxio and Sinch (cloud), or self‑hosted SIP/Asterisk.
- HIPAA‑aligned controls: HMAC webhook verification, short‑TTL tokens, no secret logging.
- AI integration: official MCP servers (Node & Python) for stdio/HTTP/SSE.
- Identical SDKs: Node.js and Python with the same surface and errors.

## Quick start (Docker Compose)
1) Copy `.env` (see `.env.example`). Pick a backend:
- Phaxio (recommended): set `FAX_BACKEND=phaxio` and `PHAXIO_API_KEY/PHAXIO_API_SECRET`.
- Sinch: set `FAX_BACKEND=sinch`, `SINCH_PROJECT_ID/SINCH_API_KEY/SINCH_API_SECRET`.
- SIP/Asterisk: set `FAX_BACKEND=sip` and AMI vars (see docs).

2) Start the API (and Admin Console):
```
docker compose up -d --build api
```

3) Open the Admin Console: http://localhost:8080

Health checks:
- API: `curl http://localhost:8080/health`
- Ready: `curl -i http://localhost:8080/health/ready`

Optional MCP servers:
```
docker compose --profile mcp up -d --build faxbot-mcp
docker compose --profile mcp up -d --build faxbot-mcp-sse
```

## Backends
- [Phaxio Setup](docs/PHAXIO_SETUP.md)
- [Sinch Setup](docs/SINCH_SETUP.md)
- [SIP/Asterisk Setup](docs/SIP_SETUP.md)

## SDKs
- Python: `pip install faxbot`
- Node.js: `npm install faxbot`
→ [SDK Usage](docs/SDKS.md)

## Architecture highlights
- Traits‑first capabilities: `/admin/providers` and `/admin/config` expose active providers + traits; UI and API gate features by traits.
- Canonical event & error model: normalized inbound/outbound events, status mapping, and standard error codes.
- Provider adapters: clean boundaries for verify_webhook/parse_inbound/send/status/cancel.

Docs:
- [Canonical Events](docs/api/canonical_events.md)
- [MCP Integration](docs/MCP_INTEGRATION.md)
- [API Reference](docs/API_REFERENCE.md)

## Security
- Use `X-API-Key` (multi‑key) for auth.
- Enforce HTTPS and HMAC signature verification for cloud webhooks.
- No PHI in logs; only IDs/metadata are surfaced.

## Notes
- Receiving is feature‑gated by provider traits; see Admin Console → Diagnostics.
- File types: PDF and TXT only. Convert images to PDF first.

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md). Please open issues/PRs; this project is GUI‑first and traits‑first—avoid backend‑name checks in new code.

