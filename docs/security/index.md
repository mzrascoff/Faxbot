# Security

Configuration and guidance for HIPAA‑aligned deployments and OAuth/OIDC setup.

Webhooks and Callbacks
- Outbound status (Phaxio): `POST /phaxio-callback` with HMAC verification. Keep callback URLs HTTPS.
- Inbound (cloud): `POST /phaxio-inbound` (HMAC) and `POST /sinch-inbound` (consider Basic auth and IP allowlists). Never disable signature checks where the provider supports them.
- Inbound (self‑hosted): `POST /_internal/asterisk/inbound` with `X-Internal-Secret` on a private network.

MCP Transports
- HTTP: protect with an API key and strict CORS.
- SSE: require OAuth2/JWT; configure issuer/audience/JWKS; run behind TLS.
- WebSocket (Node helper): protect with an API key; run behind TLS or an authenticated proxy.

Recommended reading
- HIPAA Requirements: ../HIPAA_REQUIREMENTS.md
- OAuth/OIDC Setup: oauth-setup.md
- Compliance overview: https://faxbot.net/compliance/

