# Network & Transports

Guidance for securing MCP transports and webhooks when running Faxbot in production.

## MCP Transports
- HTTP (Node MCP): protect with MCP_HTTP_API_KEY; strict CORS; TLS via proxy.
- SSE (Node/Python): require OAuth2/JWT; TLS; validate against IdP.
- WebSocket (Node MCP): protect with MCP_WS_API_KEY; TLS or authenticated proxy.

## Webhooks & Callbacks
- Phaxio outbound: POST /phaxio-callback with HMAC signature
- Phaxio inbound: POST /phaxio-inbound (HMAC)
- Sinch inbound: POST /sinch-inbound (Basic + optional HMAC)
- SIP/Asterisk inbound: POST /_internal/asterisk/inbound with X-Internal-Secret, private network only

## Reverse Proxy Recommendations
Enforce TLS, add security headers, size limits, rate limits/IP restrictions, and avoid logging PHI.
