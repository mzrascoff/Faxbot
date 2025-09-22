from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple


class ProviderAdapter(ABC):
    """Base adapter boundary for provider integrations.

    Adapters implement outbound (send/status/cancel) and inbound (verify/parse) surfaces.
    """

    id: str

    @abstractmethod
    async def verify_webhook(self, headers: Dict[str, str], body: bytes, secrets: Dict[str, str]) -> Tuple[bool, Optional[str]]:
        """Return (valid, reason)."""

    @abstractmethod
    async def parse_inbound(self, headers: Dict[str, str], body: bytes) -> Dict[str, Any]:
        """Return normalized inbound event dict (matches InboundFaxEvent fields)."""

    @abstractmethod
    async def send(self, to_number: str, file_path: str, **kwargs: Any) -> Dict[str, Any]:
        """Return normalized outbound event with job metadata."""

    @abstractmethod
    async def status(self, job_id: str, provider_sid: Optional[str] = None) -> Dict[str, Any]:
        """Return normalized outbound status."""

    @abstractmethod
    async def cancel(self, job_id: str, provider_sid: Optional[str] = None) -> Dict[str, Any]:
        """Return final canceled status or capability error."""


