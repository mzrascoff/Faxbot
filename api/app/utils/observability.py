from __future__ import annotations

import json
import time
from typing import Any, Dict, Optional


def log_event(logger, *, event_type: str, provider: str, status_canonical: str, status_raw: Optional[str] = None, signature_valid: Optional[bool] = None, extra: Optional[Dict[str, Any]] = None, start_ns: Optional[int] = None) -> None:
    data: Dict[str, Any] = {
        "event_type": event_type,
        "provider": provider,
        "status_canonical": status_canonical,
    }
    if status_raw is not None:
        data["status_raw"] = status_raw
    if signature_valid is not None:
        data["signature_valid"] = bool(signature_valid)
    if extra:
        data.update(extra)
    if start_ns is not None:
        data["processing_ms"] = round((time.time_ns() - start_ns) / 1_000_000, 3)
    try:
        logger.info(json.dumps(data, separators=(",", ":")))
    except Exception:
        logger.info(str(data))


