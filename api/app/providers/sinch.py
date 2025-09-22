from __future__ import annotations
import hmac
import hashlib
from typing import Any, Dict, Tuple


def verify_webhook(headers: Dict[str, str], body: bytes, secret: str, strict: bool = False) -> bool:
    """Verify Sinch webhook using HMAC-SHA256 when X-Sinch-Signature present.

    - If header present: validate (returns True/False). In strict=True, False → raise.
    - If header missing: return True in non-strict mode (compatibility); False in strict.
    """
    sig = headers.get("X-Sinch-Signature") or headers.get("x-sinch-signature")
    if not sig:
        if strict:
            return False
        return True
    if not secret:
        return not strict
    mac = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    ok = hmac.compare_digest(mac, sig.strip())
    return ok


def parse_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize Sinch inbound JSON/multipart form into a canonical event.

    Canonical fields: id, from_number, to_number, status, pages, file_url.
    """
    return {
        "id": str(data.get("id") or data.get("fax_id") or ""),
        "from_number": _n(data.get("from") or data.get("from_number")),
        "to_number": _n(data.get("to") or data.get("to_number")),
        "status": str(data.get("status") or data.get("fax_status") or "received").lower(),
        "pages": _i(data.get("pages") or data.get("num_pages")),
        "file_url": str(data.get("file_url") or data.get("media_url") or ""),
        "provider": "sinch",
    }


def _n(v: Any) -> str | None:
    return str(v) if v is not None and str(v).strip() else None


def _i(v: Any) -> int | None:
    try:
        return int(v) if v is not None else None
    except Exception:
        return None

