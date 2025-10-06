---
title: Desktop (Electron)
---

# Desktop (Electron)

A native shell around the Admin Console for desktop workflows.

## Usage

1) Launch the app and point it at your Faxbot server (e.g., `https://your-domain`)
2) Sign in with an Admin API key
3) Use the Admin Console tabs for Setup, Settings, Jobs, Inbox, and Diagnostics

!!! note "Security"
    The renderer runs sandboxed; no Node APIs are exposed to web content. Keep your server on HTTPS and never expose Admin Terminal over public tunnels.

See also
- [Admin Console: Settings](/admin-console/settings/)
- [Admin Console: Diagnostics](/admin-console/diagnostics/)

