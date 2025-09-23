# Curated Registry

Admin endpoints (admin scope):
- GET /plugins
- GET /plugins/{id}/config
- PUT /plugins/{id}/config
- GET /plugin-registry

Config store uses atomic writes and `.bak` rollback.
