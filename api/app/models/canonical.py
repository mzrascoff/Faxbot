from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class NormalizedStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    delivered = "delivered"
    failed = "failed"
    canceled = "canceled"
    unknown = "unknown"


@dataclass
class CanonicalError:
    code: str
    message: str
    provider: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


@dataclass
class InboundFaxEvent:
    event_id: str
    provider: str
    received_at: str
    to_number: Optional[str] = None
    from_number: Optional[str] = None
    pages: Optional[int] = None
    status_canonical: NormalizedStatus = NormalizedStatus.delivered
    status_raw: Optional[str] = None
    signature_valid: Optional[bool] = None
    error: Optional[CanonicalError] = None


@dataclass
class OutboundFaxEvent:
    job_id: str
    provider: str
    provider_sid: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    to_number: Optional[str] = None
    pages: Optional[int] = None
    status_canonical: NormalizedStatus = NormalizedStatus.queued
    status_raw: Optional[str] = None
    error: Optional[CanonicalError] = None


