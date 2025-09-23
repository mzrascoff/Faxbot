# Contributing to Faxbot

Thanks for your interest in Faxbot! Whether you're reporting a bug, requesting a feature, or contributing code, we're here to help.

## Getting Help

Don’t hesitate to open an issue. Faxbot has many moving parts, and we’d rather help you get unstuck than have you struggle alone.

## When Opening an Issue

Include:

### Your Configuration
- Backend: which backend are you using? (`phaxio`, `sinch`, `sip`, or `FAX_DISABLED=true` for testing)
- Compliance: are you bound by HIPAA requirements, or are you a non‑healthcare user?
- MCP integration (if applicable): server/transport in use (Node stdio/HTTP/SSE, or Python stdio/SSE)

### What Happened
- Expected behavior vs actual behavior
- Steps to reproduce

### Supporting Information
- Logs (with PHI redacted)
- Screenshots (if applicable)
- Environment: Docker, local dev, or cloud deployment

### Important: Protect PHI/PII
Never include protected health information (PHI) or personally identifiable information (PII) in issues, logs, or screenshots. Redact sensitive info with `[REDACTED]` or `***`.

## Types of Contributions

### Bug Reports
Use the issue template and include the configuration details above.

### Feature Requests
Describe your use case and why the feature would be valuable. Consider which backends it would apply to.

### Code Contributions
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and test across relevant backends
4. Commit with clear messages
5. Push and open a Pull Request

## Testing

- Test Mode: use `FAX_DISABLED=true` for development (no real faxes sent)
- Backend‑specific: if your change affects a backend, test with that backend
- MCP changes: test the relevant MCP transport (stdio/HTTP/SSE)
- SDK changes: test both Node.js and Python SDKs if applicable

## Code Style

- Python: PEP 8; use `black`
- Node.js: use the project ESLint config
- Docs: update relevant pages under `docs/`

## Security Considerations

Faxbot handles sensitive healthcare data. When contributing:
- Never commit API keys, secrets, or test PHI
- Consider HIPAA implications for new features
- Use secure defaults and document security requirements clearly

## Questions?

Open an issue with the “question” label — maintainers are happy to help.
