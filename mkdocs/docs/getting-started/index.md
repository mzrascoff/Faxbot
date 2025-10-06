---
title: Getting Started
---

# Getting Started

Launch Faxbot locally, send your first fax, and explore the Admin Console.

## Quick start

1) Start the stack (Docker or local) and open the Admin Console
2) Run Setup Wizard to select a backend and validate credentials
3) Send a test fax from the UI or API

=== "curl"

    ```bash
    curl -sS -X POST "$PUBLIC_API_URL/fax" \
      -H "X-API-Key: ${API_KEY:?}" \
      -F to=+15551234567 -F file=@README.md | jq .
    ```

=== "Admin Console"

    Use the Send Fax panel, upload a PDF/TXT, and submit.

## Next steps

- [Go‑Live Checklists](/go-live/)
- [Networking & Tunnels](/networking/tunnels/)
- [Webhooks](/setup/webhooks/)

