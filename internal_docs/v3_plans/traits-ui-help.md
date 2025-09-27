# UI Help as Traits — TODO

Goal: Ensure every help tip and “Learn more” link in the Admin Console is derived from provider traits, so guidance remains accurate, versioned, and non‑ephemeral.

Why:
- Prevent accidental loss of carefully crafted tips.
- Guarantee backend‑specific, HIPAA‑safe guidance appears only for the active provider.
- Enable plugin‑provided UI help for third‑party providers.

Plan:
- Add trait keys for UI help bundles per provider (e.g., `ui_help.diagnostics`, `ui_help.settings`, `ui_help.wizard`).
- Extend `/admin/config` to expose `traits.registry` help payloads with docsBase token expansion.
- In Admin UI, consume help bundles to render tooltips and “Learn more” lists.
- Enforce presence of at least one help tip per complex control (build‑time check).

Phases:
1) Schema: define `ui_help` structure in `config/provider_traits.json` + manifests.
2) Server: include `ui_help` in traits registry output; validate required keys.
3) UI: wire Diagnostics, Settings, and Wizard to render from `ui_help`.
4) Tests: snapshot help bundles per provider; lint for missing/empty tips.

Notes:
- Respect docsBase; avoid hard‑coded URLs in UI.
- Keep tips short in UI; point to docs for deep dives.
