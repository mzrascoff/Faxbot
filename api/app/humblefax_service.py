from __future__ import annotations

import os
import json
import httpx
import anyio
from typing import Any, Dict, Optional

from .config import settings, reload_settings


class HumbleFaxService:
    """HumbleFax API integration using Basic Auth.

    Implements QuickSendFax (multipart/form-data) for outbound sending and a
    lightweight status getter when available.
    """

    BASE_URL = os.getenv("HUMBLEFAX_BASE_URL", "https://api.humblefax.com").rstrip("/")

    def __init__(self, access_key: str, secret_key: str, from_number: Optional[str] = None):
        self.access_key = (access_key or "").strip()
        self.secret_key = (secret_key or "").strip()
        self.from_number = (from_number or "").strip()

    def is_configured(self) -> bool:
        return bool(self.access_key and self.secret_key)

    def _basic_auth(self) -> tuple[str, str]:
        return (self.access_key, self.secret_key)

    @staticmethod
    def _digits(num: Optional[str]) -> Optional[str]:
        if not num:
            return None
        d = "".join(ch for ch in str(num) if ch.isdigit())
        return d or None

    async def quick_send(self, to_number: str, file_path: str) -> Dict[str, Any]:
        """Send using QuickSendFax endpoint with one or more attachments.

        For our flow we attach a single PDF and pass recipients in jsonData.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(file_path)
        url = f"{self.BASE_URL}/quickSendFax"

        # Prepare jsonData with required fields
        to_digits = self._digits(to_number)
        if not to_digits:
            raise ValueError("Invalid destination number")
        body: Dict[str, Any] = {
            "recipients": [int(to_digits)],
            "includeCoversheet": False,
        }
        from_digits = self._digits(self.from_number)
        if from_digits:
            try:
                body["fromNumber"] = int(from_digits)
            except Exception:
                pass

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with await anyio.open_file(file_path, 'rb') as fh:
                content = await fh.read()
            files = {
                # file fields; HumbleFax accepts multiple, we attach one
                os.path.basename(file_path): (os.path.basename(file_path), content, "application/pdf"),
            }
            data = {
                "jsonData": json.dumps(body),
            }
            resp = await client.post(url, auth=self._basic_auth(), data=data, files=files)
        if resp.status_code >= 400:
            raise RuntimeError(f"HumbleFax QuickSendFax error {resp.status_code}: {resp.text[:400]}")
        try:
            return resp.json()
        except Exception:
            return {"status_code": resp.status_code, "text": resp.text[:400]}

    async def get_fax_status(self, fax_id: str) -> Dict[str, Any]:
        """Best-effort status polling.

        HumbleFax docs show SentFax details endpoints; some deployments use
        `GET /sentFax/{id}`. If it is unavailable, return a minimal payload.
        """
        url_variants = [
            f"{self.BASE_URL}/sentFax/{fax_id}",
            f"{self.BASE_URL}/getSentFax?id={fax_id}",
        ]
        last: Optional[tuple[str, int | str, str]] = None
        async with httpx.AsyncClient(timeout=15.0) as client:
            for url in url_variants:
                try:
                    r = await client.get(url, auth=self._basic_auth())
                    if r.status_code < 400:
                        try:
                            return r.json()
                        except Exception:
                            return {"status_code": r.status_code, "text": r.text[:400]}
                    last = (url, r.status_code, r.text[:200])
                except Exception as e:
                    last = (url, "exception", str(e))
                    continue
        raise RuntimeError(f"HumbleFax get status failed: {last}")


_hf_service: Optional[HumbleFaxService] = None


def get_humblefax_service() -> Optional[HumbleFaxService]:
    global _hf_service
    reload_settings()
    ak = getattr(settings, 'humblefax_access_key', '')
    sk = getattr(settings, 'humblefax_secret_key', '')
    fn = getattr(settings, 'humblefax_from_number', '')
    if not (ak and sk):
        _hf_service = None
        return None
    if _hf_service is None:
        _hf_service = HumbleFaxService(ak, sk, from_number=fn)
    return _hf_service

