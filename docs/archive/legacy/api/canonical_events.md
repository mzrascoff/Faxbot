# Canonical Event & Error Model

Status: Draft (v1)

This document defines the provider‑agnostic event and error shapes returned by adapters and surfaced in internal APIs and logs.

## Canonical Status

NormalizedStatus (string enum):
- queued
- processing
- delivered
- failed
- canceled
- unknown

Providers map raw states to this set (see `config/provider_status_map.json`).

## Errors

Error `code` values (string enum):
- capability_missing
- signature_invalid
- unsupported_operation
- rate_limited
- provider_timeout

Common fields:
- code: string
- message: string (operator‑readable; no PHI)
- provider?: string (id)
- details?: object (safe metadata only)

## InboundFaxEvent (normalized)

Fields:
- event_id: string (provider SID or dedupe hash)
- provider: string (id)
- received_at: ISO datetime (UTC)
- to_number?: string (E.164)
- from_number?: string (E.164)
- pages?: number
- status_canonical: NormalizedStatus
- status_raw?: string
- signature_valid?: boolean
- error?: Error

## OutboundFaxEvent (normalized)

Fields:
- job_id: string (Faxbot job id)
- provider: string (id)
- provider_sid?: string
- created_at: ISO datetime
- updated_at?: ISO datetime
- to_number: string (E.164)
- pages?: number
- status_canonical: NormalizedStatus
- status_raw?: string
- error?: Error

## JSON Examples

### Phaxio inbound (normalized)
```json
{
  "event_id": "phaxio_abc123",
  "provider": "phaxio",
  "received_at": "2025-09-22T02:00:00Z",
  "to_number": "+15551234567",
  "from_number": "+15557654321",
  "pages": 3,
  "status_canonical": "delivered",
  "status_raw": "received",
  "signature_valid": true
}
```

### Sinch inbound (normalized)
```json
{
  "event_id": "sinch_evt_789",
  "provider": "sinch",
  "received_at": "2025-09-22T02:05:00Z",
  "to_number": "+15551234567",
  "from_number": "+15550000000",
  "status_canonical": "delivered",
  "status_raw": "completed",
  "signature_valid": true
}
```

### Outbound status (any provider)
```json
{
  "job_id": "b0f9d2d2-6b0e-4f0d-bd2c-8a1f62e1e111",
  "provider": "phaxio",
  "provider_sid": "fax_456",
  "created_at": "2025-09-22T01:55:00Z",
  "updated_at": "2025-09-22T02:00:10Z",
  "to_number": "+15551234567",
  "pages": 2,
  "status_canonical": "delivered",
  "status_raw": "success"
}
```

### Error example
```json
{
  "code": "capability_missing",
  "message": "AMI required by inbound provider",
  "provider": "sip",
  "details": { "trait": "requires_ami" }
}
```

## Observability

Emit structured logs with keys:
- event_type: inbound|outbound
- provider
- status_canonical
- status_raw
- signature_valid (bool)
- processing_ms (number)

These keys back counters for provider/status dashboards (Grafana‑ready).
