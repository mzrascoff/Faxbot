from __future__ import annotations
from typing import Any, Dict, Optional
from ..config import settings, active_outbound
from ..phaxio_service import get_phaxio_service
from ..sinch_service import get_sinch_service


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
        res = await svc.send_fax_file(to, file_path)
        return _canonical_from_sinch_send(res)

    async def get_status(self, provider_sid: str) -> Dict[str, Any]:
        svc = get_sinch_service()
        if not svc or not svc.is_configured():
            raise RuntimeError("Sinch not configured")
        res = await svc.get_fax_status(provider_sid)
        return _canonical_from_sinch_status(res)

    async def cancel(self, provider_sid: str) -> Dict[str, Any]:
        # Sinch cancellation may not be supported in current flow; return not implemented
        return {"ok": False, "error": "cancel_not_supported"}


def get_outbound_adapter() -> OutboundAdapter:
    ob = active_outbound()
    if ob == "phaxio":
        return PhaxioAdapter()
    if ob == "sinch":
        return SinchAdapter()
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
