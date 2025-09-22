from __future__ import annotations
import hmac
import hashlib
from typing import Any, Dict


def verify_webhook(headers: Dict[str, str], body: bytes, secret: str, strict: bool = False) -> bool:
    """Verify Phaxio webhook using HMAC-SHA1 (X-Phaxio-Signature).

    - If header present: validate against secret.
    - If header missing: non-strict returns True (compat); strict returns False.
    """
    sig = headers.get("X-Phaxio-Signature") or headers.get("x-phaxio-signature")
    if not sig:
        return not strict
    if not secret:
        return not strict
    mac = hmac.new(secret.encode("utf-8"), body, hashlib.sha1).hexdigest()
    ok = hmac.compare_digest(mac, sig.strip())
    return ok


def parse_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize Phaxio inbound payload into a canonical event.

    Canonical fields: id, from_number, to_number, status, pages, file_url.
    """
    return {
        "id": str(data.get("faxId") or data.get("fax_id") or data.get("id") or ""),
        "from_number": _n(data.get("fromNumber") or data.get("from")),
        "to_number": _n(data.get("toNumber") or data.get("to")),
        "status": str(data.get("status") or data.get("faxStatus") or "received").lower(),
        "pages": _i(data.get("numPages") or data.get("pages")),
        "file_url": str(data.get("fileUrl") or data.get("file_url") or ""),
        "provider": "phaxio",
    }


def _n(v: Any) -> str | None:
    return str(v) if v is not None and str(v).strip() else None


def _i(v: Any) -> int | None:
    try:
        return int(v) if v is not None else None
    except Exception:
        return None

