# Plugins (v3)

Faxbot v3 introduces runtime-switchable provider plugins backed by a single resolved config file.

- Outbound: one active provider (phaxio, sinch, sip, documo, signalwire, or HTTP manifest)
- Storage: local or S3/S3-compatible

Enable discovery: `FEATURE_V3_PLUGINS=true`; resolved config path: `FAXBOT_CONFIG_PATH` (default `config/faxbot.config.json`).

See: registry, HTTP manifests, SIP provider plugins.
