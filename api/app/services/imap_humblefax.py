"""
HumbleFax IMAP polling scaffold (Phase 5):

- Disabled by default; enable with HUMBLEFAX_IMAP_ENABLED=true
- Offloads blocking IMAP ops to a thread to avoid blocking the event loop
- PDF-only attachments; sanitize filenames; cap count and total bytes
- No PHI in logs; records inbound faxes with minimal canonical fields
"""

from __future__ import annotations

import imaplib
import email
from email.message import Message
import os
import time
import hashlib
from pathlib import Path
from typing import List, Tuple, Optional

import anyio

from ..config import settings
from ..db import SessionLocal
from ..audit import audit_event


def _env_bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name, str(default).lower())
    return str(v).lower() in {"1", "true", "yes", "on"}


def _sanitize_filename(name: str) -> str:
    base = name.replace("\\", "/").split("/")[-1]
    # keep alnum, dash, underscore, dot
    safe = "".join(ch for ch in base if ch.isalnum() or ch in {"-", "_", "."})
    if not safe:
        safe = "attachment.pdf"
    return safe[:128]


class HumbleFaxImapWorker:
    def __init__(self) -> None:
        self.enabled = _env_bool("HUMBLEFAX_IMAP_ENABLED", False)
        self.server = os.getenv("HUMBLEFAX_IMAP_SERVER", "")
        self.username = os.getenv("HUMBLEFAX_IMAP_USERNAME", "")
        self.password = os.getenv("HUMBLEFAX_IMAP_PASSWORD", "")
        self.port = int(os.getenv("HUMBLEFAX_IMAP_PORT", "993") or "993")
        self.use_ssl = _env_bool("HUMBLEFAX_IMAP_SSL", True)
        self.poll_seconds = max(30, int(os.getenv("HUMBLEFAX_IMAP_POLL_INTERVAL", "300") or "300"))
        self.max_attach_count = max(1, int(os.getenv("HUMBLEFAX_IMAP_MAX_ATTACH_COUNT", "3") or "3"))
        self.max_attach_mb = max(1, int(os.getenv("HUMBLEFAX_IMAP_MAX_ATTACH_MB", "25") or "25"))
        self._stop = False

    def configured(self) -> bool:
        return bool(self.server and self.username and self.password)

    async def run_forever(self) -> None:
        if not self.enabled or not self.configured():
            return
        while not self._stop:
            try:
                await anyio.to_thread.run_sync(self._poll_once)
            except Exception:
                # Swallow errors; back off briefly
                await anyio.sleep(5)
            # Jittered backoff around poll interval (±10%)
            jitter = max(1, int(self.poll_seconds * 0.1))
            await anyio.sleep(self.poll_seconds - jitter)
            await anyio.sleep(jitter)

    def stop(self) -> None:
        self._stop = True

    def _connect(self) -> imaplib.IMAP4:
        if self.use_ssl:
            return imaplib.IMAP4_SSL(self.server, self.port)
        return imaplib.IMAP4(self.server, self.port)

    def _poll_once(self) -> None:
        """Blocking IMAP poll — runs in a worker thread."""
        try:
            imap = self._connect()
        except Exception:
            return
        try:
            imap.login(self.username, self.password)
            imap.select("INBOX")
            typ, data = imap.search(None, 'UNSEEN')
            if typ != 'OK':
                return
            uids = (data[0].decode().split() if data and data[0] else [])
            for uid in uids:
                try:
                    self._process_message(imap, uid)
                    # Mark seen
                    try:
                        imap.store(uid, '+FLAGS', '(\\Seen)')
                    except Exception:
                        pass
                except Exception:
                    # Skip on error, continue with next message
                    continue
        finally:
            try:
                imap.logout()
            except Exception:
                pass

    def _process_message(self, imap: imaplib.IMAP4, uid: str) -> None:
        typ, msg_data = imap.fetch(uid, '(RFC822)')
        if typ != 'OK' or not msg_data:
            return
        raw = None
        for part in msg_data:
            if isinstance(part, tuple):
                raw = part[1]
                break
        if not raw:
            return
        msg: Message = email.message_from_bytes(raw)
        attach_saved = 0
        total_bytes = 0
        for part in msg.walk():
            if part.get_content_disposition() != 'attachment':
                continue
            filename = part.get_filename() or 'attachment.pdf'
            safe_name = _sanitize_filename(filename)
            ctype = (part.get_content_type() or '').lower()
            if not safe_name.lower().endswith('.pdf') and 'pdf' not in ctype:
                continue
            payload = part.get_payload(decode=True) or b''
            size = len(payload)
            # Enforce caps
            if attach_saved >= self.max_attach_count:
                break
            if (total_bytes + size) > (self.max_attach_mb * 1024 * 1024):
                break

            # Persist safely into fax data dir
            job_id = email.utils.make_msgid().strip('<>') or str(int(time.time()))
            out_dir = Path(settings.fax_data_dir) / 'inbound' / 'humblefax'
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"{job_id}-{safe_name}"
            with open(out_path, 'wb') as f:
                f.write(payload)
            sha256_hex = hashlib.sha256(payload).hexdigest()

            # Record in DB (minimal canonical fields)
            from ..db import InboundFax  # type: ignore
            from datetime import datetime
            with SessionLocal() as db:
                fx = InboundFax(
                    id=job_id,
                    from_number=None,
                    to_number=None,
                    status='received',
                    backend='humblefax',
                    inbound_backend='humblefax',
                    provider_sid=uid,
                    pages=None,
                    size_bytes=size,
                    sha256=sha256_hex,
                    pdf_path=str(out_path),
                    tiff_path=None,
                    mailbox_label='imap',
                    retention_until=None,
                    pdf_token=None,
                    pdf_token_expires_at=None,
                    created_at=datetime.utcnow(),
                    received_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                try:
                    db.add(fx)
                    db.commit()
                except Exception:
                    db.rollback()
            try:
                audit_event('inbound_received', job_id=job_id, backend='humblefax')
            except Exception:
                pass

            attach_saved += 1
            total_bytes += size

