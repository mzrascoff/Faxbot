from __future__ import annotations

import os
import json
import httpx
import anyio
import asyncio
from typing import Any, Dict, Optional
import logging

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
        self.DEBUG = os.getenv("HUMBLEFAX_DEBUG", "false").lower() in {"1", "true", "yes"}
        self.logger = logging.getLogger(__name__)

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

    async def quick_send(self, to_number: str, file_path: str, uuid: Optional[str] = None) -> Dict[str, Any]:
        """Send using QuickSendFax with exact documented format.

        - Multipart field name MUST be "file".
        - jsonData includes integer recipients array, includeCoversheet, pageSize, resolution.
        - Optional fromNumber and uuid for idempotency.
        - Handles rate limits and timeouts with bounded backoff.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(file_path)
        url = f"{self.BASE_URL}/quickSendFax"

        # Prepare jsonData with required fields
        to_digits = self._digits(to_number)
        if not to_digits or len(to_digits) < 10 or len(to_digits) > 11:
            raise ValueError("Invalid destination number: must be 10-11 digits")
        body: Dict[str, Any] = {
            "recipients": [int(to_digits)],
            "includeCoversheet": False,
            "resolution": "Fine",
            "pageSize": "Letter",
        }
        if uuid:
            body["uuid"] = uuid
        from_digits = self._digits(self.from_number)
        if from_digits and len(from_digits) >= 10:
            try:
                body["fromNumber"] = int(from_digits)
            except Exception:
                pass

        async with httpx.AsyncClient(timeout=60.0) as client:
            # Up to 3 attempts on rate limit/timeout
            max_retries = 3
            for attempt in range(max_retries):
                async with await anyio.open_file(file_path, 'rb') as fh:
                    content = await fh.read()
                files = {
                    # Correct field name is "file"
                    "file": (os.path.basename(file_path), content, "application/pdf"),
                }
                data = {"jsonData": json.dumps(body)}

                if self.DEBUG:
                    # Avoid logging PHI (mask recipients, fromNumber)
                    masked = dict(body)
                    if masked.get("recipients"):
                        masked["recipients_count"] = len(masked.get("recipients") or [])
                        masked.pop("recipients", None)
                    if masked.get("fromNumber"):
                        masked["fromNumber"] = "***"
                    self.logger.info("[HumbleFax] QuickSendFax Request")
                    self.logger.info(f"  URL: {url}")
                    self.logger.info(f"  Auth: {self.access_key[:4]}***")
                    self.logger.info(f"  jsonData(meta): {json.dumps(masked, separators=(',',':'))}")
                    try:
                        size = os.path.getsize(file_path)
                    except Exception:
                        size = 0
                    self.logger.info(f"  File: {os.path.basename(file_path)} ({size} bytes)")

                try:
                    resp = await client.post(url, auth=self._basic_auth(), data=data, files=files)
                except httpx.TimeoutException as e:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # 1s, 2s
                        if self.DEBUG:
                            self.logger.info(f"[HumbleFax] Timeout, retrying in {wait_time}s")
                        await asyncio.sleep(wait_time)
                        continue
                    raise RuntimeError(f"HumbleFax timeout after {max_retries} attempts: {str(e)}")

                if self.DEBUG:
                    self.logger.info("[HumbleFax] Response")
                    self.logger.info(f"  Status: {resp.status_code}")
                    try:
                        self.logger.info(f"  Headers: {dict(resp.headers)}")
                    except Exception:
                        pass
                    self.logger.info(f"  Body: {resp.text[:1000]}")

                # Rate limit handling
                if resp.status_code == 429:
                    if attempt < max_retries - 1:
                        wait_time = min(65, 30 * (attempt + 1))
                        if self.DEBUG:
                            self.logger.info(f"[HumbleFax] Rate limited, waiting {wait_time}s before retry {attempt+1}/{max_retries}")
                        await asyncio.sleep(wait_time)
                        continue
                    raise RuntimeError(f"HumbleFax rate limit exceeded after {max_retries} attempts")

                if resp.status_code >= 400:
                    error_msg = self._extract_error(resp.text, resp.status_code)
                    raise RuntimeError(f"HumbleFax API error {resp.status_code}: {error_msg}")
                try:
                    result = resp.json()
                except Exception:
                    raise RuntimeError(f"Invalid JSON response: {resp.text[:400]}")

                # Validate fax id exists (handle multiple structures)
                fax_data = (result.get("data") or {}).get("fax") or (result.get("data") or {}).get("sentFax") or {}
                fax_id = fax_data.get("id") or result.get("id") or result.get("faxId")
                if not fax_id:
                    err = (
                        (result.get("error", {}) or {}).get("message") if isinstance(result.get("error"), dict) else result.get("error")
                    ) or result.get("message") or "Missing fax ID in response"
                    raise RuntimeError(f"HumbleFax send failed: {err}")

                if self.DEBUG:
                    status = fax_data.get("status")
                    self.logger.info(f"[HumbleFax] Success - Fax ID: {fax_id}, Status: {status if isinstance(status, str) else (status or ['queued'])[0]}")
                return result

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

    async def send_via_tmpfax(self, to_number: str, file_path: str, uuid: Optional[str] = None) -> Dict[str, Any]:
        """Alternative multi-step send flow for when QuickSend fails."""
        to_digits = self._digits(to_number)
        if not to_digits or len(to_digits) < 10 or len(to_digits) > 11:
            raise ValueError("Invalid destination number: must be 10-11 digits")

        tmp_fax_data: Dict[str, Any] = {
            "recipients": [int(to_digits)],
            "fromName": "Faxbot",
            "includeCoversheet": False,
            "resolution": "Fine",
            "pageSize": "Letter",
        }
        if uuid:
            tmp_fax_data["uuid"] = uuid
        from_digits = self._digits(self.from_number)
        if from_digits and len(from_digits) >= 10:
            tmp_fax_data["fromNumber"] = int(from_digits)

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Step 1: Create TmpFax
            r1 = await client.post(f"{self.BASE_URL}/tmpFax", json=tmp_fax_data, auth=self._basic_auth(), headers={"Content-Type": "application/json"})
            if r1.status_code >= 400:
                error = self._extract_error(r1.text, r1.status_code)
                raise RuntimeError(f"CreateTmpFax failed: {error}")
            try:
                result1 = r1.json()
            except Exception:
                raise RuntimeError(f"CreateTmpFax invalid JSON: {r1.text[:200]}")
            tmp_fax_id = (result1.get("data", {}).get("tmpFax", {}) or {}).get("id")
            if not tmp_fax_id:
                raise RuntimeError(f"No tmpFax ID in response: {r1.text[:200]}")
            if self.DEBUG:
                self.logger.info(f"[HumbleFax] Created tmpFax: {tmp_fax_id}")

            # Step 2: Upload attachment
            async with await anyio.open_file(file_path, 'rb') as fh:
                content = await fh.read()
            files = {"file": (os.path.basename(file_path), content, "application/pdf")}
            r2 = await client.post(f"{self.BASE_URL}/attachment/{tmp_fax_id}", files=files, auth=self._basic_auth())
            if r2.status_code >= 400:
                error = self._extract_error(r2.text, r2.status_code)
                raise RuntimeError(f"CreateAttachment failed: {error}")
            if self.DEBUG:
                self.logger.info(f"[HumbleFax] Uploaded attachment to tmpFax {tmp_fax_id}")

            # Step 3: Send the fax
            r3 = await client.post(f"{self.BASE_URL}/tmpFax/{tmp_fax_id}/send", auth=self._basic_auth())
            if r3.status_code >= 400:
                error = self._extract_error(r3.text, r3.status_code)
                raise RuntimeError(f"SendTmpFax failed: {error}")
            try:
                result3 = r3.json()
            except Exception:
                raise RuntimeError(f"SendTmpFax invalid JSON: {r3.text[:200]}")
            if self.DEBUG:
                self.logger.info(f"[HumbleFax] Sent tmpFax: {json.dumps(result3)[:200]}")
            return result3

    async def quick_send_with_fallback(self, to_number: str, file_path: str, uuid: Optional[str] = None) -> Dict[str, Any]:
        """Try QuickSend first, fallback to TmpFax for specific error classes."""
        try:
            return await self.quick_send(to_number, file_path, uuid)
        except RuntimeError as e:
            s = str(e).lower()
            if any(x in s for x in ["missing fax id", "invalid", "unsupported"]):
                if self.DEBUG:
                    self.logger.info(f"[HumbleFax] QuickSend failed, trying TmpFax fallback: {str(e)[:200]}")
                try:
                    return await self.send_via_tmpfax(to_number, file_path, uuid)
                except Exception as e2:
                    raise RuntimeError(f"Both QuickSend and TmpFax failed. QuickSend: {str(e)[:100]}, TmpFax: {str(e2)[:100]}")
            raise

    def _extract_error(self, response_text: str, status_code: int) -> str:
        """Extract error message from response text (best effort)."""
        try:
            data = json.loads(response_text)
            if isinstance(data.get("error"), dict):
                return data.get("error", {}).get("message") or response_text[:200]
            return data.get("error") or data.get("message") or response_text[:200]
        except Exception:
            return response_text[:200]


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
