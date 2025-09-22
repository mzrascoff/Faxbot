# REST API

The full API reference is hosted on the main website:

- API Reference: https://faxbot.net/api/v1/
- Swagger UI: https://faxbot.net/api/v1/swagger

Quick facts
- Base URL (default): `http://localhost:8080`
- Auth header (when enabled): `X-API-Key: <token>`
- File types: PDF and TXT only
- Max upload size: `MAX_FILE_SIZE_MB` (default 10 MB)
- Standard errors: 400, 401, 404, 413, 415
