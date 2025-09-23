# Local Terminal (Admin Console)

Faxbot provides a local-only terminal inside the Admin Console for convenience. It runs inside the API container/process and shares the same privileges as the service user.

Security
- Local-only. Do not expose through public tunnels by default.
- Gate access with `ENABLE_LOCAL_ADMIN=true` and ensure API key protection.

Endpoint
- WebSocket: `/admin/terminal` (admin auth required).
- The backend uses `expect` to provide a TTY.

Best Practices
- Use for quick diagnostics, not long-running tasks.
- Avoid printing PHI to the terminal.
- Prefer scripted checks exposed via the Diagnostics screen when possible.

