from __future__ import annotations
import json
import logging
from typing import Any, Dict


def log_event(event: str, **fields: Any) -> None:
    """Emit a structured JSON log with canonical keys.

    Do not include PHI. Caller is responsible for redaction of any sensitive data.
    """
    try:
        payload: Dict[str, Any] = {"event": event}
        payload.update(fields or {})
        logging.getLogger("faxbot").info(json.dumps(payload, default=str))
    except Exception:
        # Best effort only; never raise from logging
        logging.getLogger("faxbot").info(f"event={event}")

