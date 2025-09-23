# Diagnostics

Run checks for provider auth, callback reachability, AMI connection, Ghostscript, storage, and clock drift. Each check links to a fix.

- Provider auth: verifies current credentials without sending a fax
- Webhooks: validates callback URL, signature status
- SIP/Asterisk: tests AMI login and required ports
- Storage: confirms write/read to storage backend
