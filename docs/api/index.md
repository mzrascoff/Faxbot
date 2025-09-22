---
layout: default
title: API Reference
nav_order: 8
has_children: true
permalink: /api/
---

# API Reference

Complete REST API documentation for Faxbot.

## OpenAPI Specification

- **[📋 Copy & Paste API Docs](/Faxbot/api-docs.html)** - **GUARANTEED TO WORK** with any tool
- **[OpenAPI JSON](/Faxbot/openapi.json)** - Standard JSON format (most compatible)
- **[OpenAPI YAML](/Faxbot/openapi.yaml)** - YAML format
- **[🔍 Swagger UI](https://petstore.swagger.io/?url=https://faxbot.github.io/Faxbot/openapi.json)** - Interactive API explorer

## Quick Start

### Authentication
```bash
# Set your API key (optional but recommended)
export API_KEY="your_api_key_here"
```

### Send a Fax
```bash
curl -X POST "http://localhost:8080/fax" \
  -H "X-API-Key: $API_KEY" \
  -F "to=+15551234567" \
  -F "file=@document.pdf"
```

### Check Status
```bash
curl -H "X-API-Key: $API_KEY" \
  "http://localhost:8080/fax/{job_id}"
```

## Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/fax` | Send a fax |
| `GET` | `/fax/{id}` | Get fax status |
| `GET` | `/fax/{id}/pdf` | Download fax PDF (tokenized access) |
| `GET` | `/health` | Service health check |
| `GET` | `/inbound` | List received faxes (when enabled) |
| `GET` | `/inbound/{id}` | Get inbound fax details |
| `GET` | `/inbound/{id}/pdf` | Download inbound PDF |

## Webhook Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/phaxio-callback` | Phaxio status webhooks |
| `POST` | `/sinch-inbound` | Sinch inbound webhooks |
| `POST` | `/signalwire-callback` | SignalWire status webhooks |

## Admin Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/admin/config` | Get system configuration |
| `POST` | `/admin/config` | Update system settings |
| `GET` | `/admin/providers` | Get provider information |
| `GET` | `/admin/diagnostics/run` | Run system diagnostics |
| `POST` | `/admin/api-keys` | Create API key |
| `GET` | `/admin/api-keys` | List API keys |

## Response Formats

### Fax Job Response
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "to_number": "+15551234567",
  "status": "SUCCESS",
  "pages": 3,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:32:15Z"
}
```

### Error Response
```json
{
  "detail": "Invalid phone number format",
  "error_code": "INVALID_PHONE"
}
```

## Status Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | `SUCCESS` | Fax transmitted successfully |
| 202 | `QUEUED` | Fax queued for transmission |
| 202 | `IN_PROGRESS` | Fax transmission in progress |
| 400 | `FAILED` | Transmission failed |

## Error Codes

| HTTP | Code | Description |
|------|------|-------------|
| 400 | `INVALID_PHONE` | Phone number format invalid |
| 400 | `MISSING_FILE` | No file provided |
| 401 | `UNAUTHORIZED` | Invalid or missing API key |
| 413 | `FILE_TOO_LARGE` | File exceeds 10MB limit |
| 415 | `UNSUPPORTED_TYPE` | File type not supported (PDF/TXT only) |
| 404 | `NOT_FOUND` | Fax job not found |

## Rate Limits

- **Outbound fax**: No built-in limits (provider-dependent)
- **Inbound list**: 30 requests/minute (configurable)
- **Inbound get**: 60 requests/minute (configurable)
- **Admin endpoints**: Varies by operation

## File Requirements

- **Supported formats**: PDF, TXT
- **Maximum size**: 10MB
- **Page limit**: Provider-dependent (typically 50-100 pages)

## SDKs

Official SDKs available:
- **[Node.js SDK](/Faxbot/sdks/#nodejs-sdk)**
- **[Python SDK](/Faxbot/sdks/#python-sdk)**

## Examples

See the [API Tests](/Faxbot/api-tests) page for comprehensive examples and test scenarios.
