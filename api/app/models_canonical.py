from __future__ import annotations

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class InboundCanonicalEvent(BaseModel):
    id: str = Field(..., description="Provider event id or fax id")
    provider: str = Field(..., description="Provider identifier")
    from_number: Optional[str] = None
    to_number: Optional[str] = None
    status: str = Field(..., description="Canonical status: queued|in_progress|success|failed")
    pages: Optional[int] = None
    file_url: Optional[str] = None
    signature_valid: Optional[bool] = None
    raw: Optional[Dict[str, Any]] = None


class OutboundSendResult(BaseModel):
    ok: bool = True
    provider: str
    job_id: Optional[str] = None
    status: str = Field(..., description="Canonical status after submit")
    raw: Optional[Dict[str, Any]] = None


class OutboundStatusCanonical(BaseModel):
    ok: bool = True
    provider: str
    status: str = Field(..., description="Canonical status for the job")
    raw: Optional[Dict[str, Any]] = None


class ProviderErrorCanonical(BaseModel):
    code: str
    message: str
    provider: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

