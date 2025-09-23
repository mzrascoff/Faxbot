# Admin Console (Local‑Only)

The Admin Console ships with Faxbot and runs from the API service. It is local‑only by default and uses the same REST API surface as external clients.

Highlights
- Local‑only by default; middleware blocks remote access.
- Uses `X-API-Key` for admin actions; secrets are masked in responses.
- Includes Settings, Diagnostics, Jobs, Inbound (when enabled), Plugins (preview), and a local Terminal.

Security
- The Admin UI is intended for operators on the host machine.
- Do not expose the Admin Console or Terminal through public tunnels unless explicitly allowed for demo.
- See [Security](../security/) for HIPAA posture and auth guidance.

Key Endpoints (server)
- `GET /admin/settings`, `PUT /admin/settings`, `POST /admin/settings/reload`
- `GET /admin/api-keys`, `POST /admin/api-keys`, `DELETE /admin/api-keys/{id}`, `POST /admin/api-keys/{id}/rotate`
- `GET /health`, `POST /fax`, `GET /fax/{id}`

Usage
- Access at `http://localhost:8080/admin/ui/` on the server.
- Provide an API key with `keys:manage` scope (or bootstrap `API_KEY`) when prompted.

