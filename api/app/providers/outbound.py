from __future__ import annotations
from typing import Any, Dict, Optional
import logging
from ..config import settings, active_outbound
from ..phaxio_service import get_phaxio_service
from ..sinch_service import get_sinch_service
try:
    from ..humblefax_service import get_humblefax_service  # type: ignore
except Exception:  # pragma: no cover
    get_humblefax_service = None  # type: ignore


class OutboundAdapter:
    async def send(self, to: str, file_path: str, *, job_id: Optional[str] = None, pdf_url: Optional[str] = None) -> Dict[str, Any]:
        raise NotImplementedError

    async def get_status(self, provider_sid: str) -> Dict[str, Any]:
        raise NotImplementedError

    async def cancel(self, provider_sid: str) -> Dict[str, Any]:  # optional
        raise NotImplementedError


class PhaxioAdapter(OutboundAdapter):
    async def send(self, to: str, file_path: str, *, job_id: Optional[str] = None, pdf_url: Optional[str] = None) -> Dict[str, Any]:
        svc = get_phaxio_service()
        if not svc or not svc.is_configured():
            raise RuntimeError("Phaxio not configured")
        if not job_id or not pdf_url:
            raise ValueError("Phaxio send requires job_id and pdf_url")
        res = await svc.send_fax(to_number=to, pdf_url=pdf_url, job_id=job_id)
        return _canonical_from_phaxio_send(res)

    async def get_status(self, provider_sid: str) -> Dict[str, Any]:
        svc = get_phaxio_service()
        if not svc or not svc.is_configured():
            raise RuntimeError("Phaxio not configured")
        res = await svc.get_fax_status(provider_sid)
        return _canonical_from_phaxio_status(res)

    async def cancel(self, provider_sid: str) -> Dict[str, Any]:
        svc = get_phaxio_service()
        if not svc or not svc.is_configured():
            raise RuntimeError("Phaxio not configured")
        try:
            ok = await svc.cancel_fax(provider_sid)
        except Exception as e:
            return {"ok": False, "error": str(e)}
        return {"ok": bool(ok)}


class SinchAdapter(OutboundAdapter):
    async def send(self, to: str, file_path: str, *, job_id: Optional[str] = None, pdf_url: Optional[str] = None) -> Dict[str, Any]:
        svc = get_sinch_service()
        if not svc or not svc.is_configured():
            raise RuntimeError("Sinch not configured")
        try:
            res = await svc.send_fax_file(to, file_path)
            return _canonical_from_sinch_send(res)
        except Exception as e:
            # Surface provider error text to caller
            return {"ok": False, "error": str(e)[:300]}

    async def get_status(self, provider_sid: str) -> Dict[str, Any]:
        svc = get_sinch_service()
        if not svc or not svc.is_configured():
            raise RuntimeError("Sinch not configured")
        res = await svc.get_fax_status(provider_sid)
        return _canonical_from_sinch_status(res)

    async def cancel(self, provider_sid: str) -> Dict[str, Any]:
        # Sinch cancellation may not be supported in current flow; return not implemented
        return {"ok": False, "error": "cancel_not_supported"}


class HumbleFaxAdapter(OutboundAdapter):
    async def send(self, to: str, file_path: str, *, job_id: Optional[str] = None, pdf_url: Optional[str] = None) -> Dict[str, Any]:
        logger = logging.getLogger(__name__)
        if get_humblefax_service is None:
            return {"ok": False, "error": "HumbleFax service module not available", "provider": "humblefax"}
        svc = get_humblefax_service()
        if not svc:
            return {"ok": False, "error": "HumbleFax service not initialized", "provider": "humblefax"}
        if not svc.is_configured():
            return {"ok": False, "error": "HumbleFax credentials missing or invalid", "provider": "humblefax"}
        try:
            # Pass job_id as idempotency UUID when present
            res = await svc.quick_send(to, file_path, uuid=job_id)
            return _canonical_from_hf_send(res)
        except FileNotFoundError as e:
            return {"ok": False, "error": f"File not found: {str(e)}", "provider": "humblefax"}
        except ValueError as e:
            return {"ok": False, "error": f"Invalid input: {str(e)}", "provider": "humblefax"}
        except RuntimeError as e:
            # API errors from service
            error_msg = str(e)
            logger.warning(f"HumbleFax API error for job {job_id}: {error_msg[:200]}")
            return {"ok": False, "error": error_msg, "provider": "humblefax"}
        except Exception as e:  # pragma: no cover
            logger.error(f"Unexpected HumbleFax error for job {job_id}: {type(e).__name__}")
            return {"ok": False, "error": f"Unexpected error: {str(e)[:200]}", "provider": "humblefax"}

    async def get_status(self, provider_sid: str) -> Dict[str, Any]:
        if get_humblefax_service is None:
            raise RuntimeError("HumbleFax service not available")
        svc = get_humblefax_service()
        if not svc or not svc.is_configured():
            raise RuntimeError("HumbleFax not configured")
        try:
            res = await svc.get_fax_status(provider_sid)
        except Exception as e:
            return {"ok": False, "error": str(e)}
        return _canonical_from_hf_status(res)

    async def cancel(self, provider_sid: str) -> Dict[str, Any]:
        return {"ok": False, "error": "cancel_not_supported"}


def get_outbound_adapter() -> OutboundAdapter:
    ob = active_outbound()
    if ob == "phaxio":
        return PhaxioAdapter()
    if ob == "sinch":
        return SinchAdapter()
    if ob == "humblefax":
        return HumbleFaxAdapter()
    # For other backends, we can add adapters later
    raise RuntimeError(f"No outbound adapter for backend: {ob}")


def _canonical_from_phaxio_send(res: Dict[str, Any]) -> Dict[str, Any]:
    from ..status_map import canonical_status
    raw = str(res.get("status") or res.get("data", {}).get("status") or "queued").lower()
    status = canonical_status("phaxio", raw)
    jid = str(res.get("provider_sid") or res.get("data", {}).get("id") or res.get("id") or "")
    return {"ok": True, "job_id": jid, "provider": "phaxio", "status": status, "raw": res}


def _canonical_from_phaxio_status(res: Dict[str, Any]) -> Dict[str, Any]:
    from ..status_map import canonical_status
    raw = str(res.get("data", {}).get("status") or res.get("status") or "").lower()
    status = canonical_status("phaxio", raw)
    return {"ok": True, "status": status, "provider": "phaxio", "raw": res}


def _canonical_from_sinch_send(res: Dict[str, Any]) -> Dict[str, Any]:
    from ..status_map import canonical_status
    jid = str(res.get("id") or res.get("data", {}).get("id") or "")
    raw = str(res.get("status") or res.get("data", {}).get("status") or "in_progress").lower()
    status = canonical_status("sinch", raw)
    return {"ok": True, "job_id": jid, "provider": "sinch", "status": status, "raw": res}


def _canonical_from_sinch_status(res: Dict[str, Any]) -> Dict[str, Any]:
    from ..status_map import canonical_status
    raw = str(res.get("status") or res.get("data", {}).get("status") or "").lower()
    status = canonical_status("sinch", raw)
    return {"ok": True, "status": status, "provider": "sinch", "raw": res}


def _canonical_from_hf_send(res: Dict[str, Any]) -> Dict[str, Any]:
    """Parse HumbleFax response with proper error handling.

    Observed structure (verified): { result: "success", data: { sentFax: { id, status, ... } } }
    Fallbacks for other shapes are included.
    """
    from ..status_map import canonical_status

    data = res.get("data") or {}
    fax_data = data.get("fax") or data.get("sentFax") or {}
    jid = str(fax_data.get("id") or res.get("id") or res.get("faxId") or "")
    if not jid:
        error_msg = (
            (res.get("error", {}) or {}).get("message") if isinstance(res.get("error"), dict) else res.get("error")
        ) or res.get("message") or "Missing fax ID - send failed"
        return {"ok": False, "error": error_msg, "provider": "humblefax", "raw": res}

    # Extract status; HumbleFax sometimes returns an array under sentFax.status
    raw_status_val = fax_data.get("status") or res.get("status") or "in progress"
    if isinstance(raw_status_val, list) and raw_status_val:
        raw = str(raw_status_val[0]).lower()
    else:
        raw = str(raw_status_val).lower()
    status = canonical_status("humblefax", raw)

    return {"ok": True, "job_id": jid, "provider": "humblefax", "status": status, "raw": res}


def _canonical_from_hf_status(res: Dict[str, Any]) -> Dict[str, Any]:
    from ..status_map import canonical_status
    data = res.get("data") or {}
    raw_status_val = (data.get("fax") or {}).get("status") or (data.get("sentFax") or {}).get("status") or res.get("status") or ""
    if isinstance(raw_status_val, list) and raw_status_val:
        raw = str(raw_status_val[0]).lower()
    else:
        raw = str(raw_status_val).lower()
    status = canonical_status("humblefax", raw)
    return {"ok": True, "status": status, "provider": "humblefax", "raw": res}
