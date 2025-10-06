---
title: Setup Wizard
---

# Setup Wizard

Configure Faxbot end‑to‑end from a guided flow: outbound provider, optional inbound, storage, and security.

!!! tip "Quick links"
    [Settings](/admin-console/settings/){ .md-button } [Diagnostics](/admin-console/diagnostics/){ .md-button } [Plugin Builder](/admin-console/plugin-builder/){ .md-button .md-button--primary }

=== "Evaluate (Quick Tunnel)"

    1) Choose a cloud provider (Phaxio, Sinch, SignalWire, Documo, HumbleFax)
    2) Enter credentials and click Validate
    3) Open Tools → Tunnels and start a quick tunnel to get a public URL
    4) Set `PUBLIC_API_URL` and register webhooks where supported

=== "Production (HIPAA)"

    1) Execute a BAA and disable provider document retention (cloud)
    2) Use a named tunnel or domain (HTTPS)
    3) Enable inbound with the correct verification (HMAC/Basic)
    4) Rotate keys and restrict Admin access

!!! tip "Backend isolation"
    The wizard shows provider‑specific fields only for the selected backend. Links and help are scoped; nothing is mixed across providers.

Next steps

- [Settings](/admin-console/settings/)
- [Diagnostics](/admin-console/diagnostics/)
- [Plugins](/admin-console/plugin-builder/)
