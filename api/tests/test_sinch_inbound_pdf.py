import os
import hashlib
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app
import uuid
from app.db import SessionLocal, InboundFax


def test_sinch_inbound_stores_readable_pdf(tmp_path, monkeypatch):
    # Environment setup for inbound via Sinch
    monkeypatch.setenv("INBOUND_ENABLED", "true")
    monkeypatch.setenv("FAX_INBOUND_BACKEND", "sinch")
    monkeypatch.setenv("SINCH_API_KEY", "key")
    monkeypatch.setenv("SINCH_API_SECRET", "secret")
    monkeypatch.setenv("FAX_DATA_DIR", str(tmp_path))

    sid = f"fax_{uuid.uuid4().hex[:8]}"
    payload = {
        "id": sid,
        "from": "+15550001111",
        "to": "+15551234567",
        "num_pages": 1,
        "status": "received",
        "file_url": "https://example.com/media/fax.pdf",
    }

    # Minimal valid PDF bytes
    pdf_bytes = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n%%EOF"

    class FakeResp:
        def __init__(self):
            self.status_code = 200
            self.content = pdf_bytes

    async def fake_get(url, auth=None):
        # Expect basic auth with Sinch creds
        assert auth == ("key", "secret")
        return FakeResp()

    with TestClient(app) as client:
        with patch("httpx.AsyncClient.get", side_effect=fake_get):
            r = client.post("/sinch-inbound", json=payload)
            assert r.status_code == 200
            data = r.json()
            assert data.get("status") == "ok"

    # Verify DB record created and file readable as PDF
    with SessionLocal() as db:
        rows = db.query(InboundFax).filter(InboundFax.provider_sid == sid).all()
        assert len(rows) == 1
        fx = rows[0]
        assert fx.pdf_path
        # Local storage will retain a local path; s3 path would start with s3://
        assert not str(fx.pdf_path).startswith("s3://")
        with open(fx.pdf_path, "rb") as f:
            content = f.read()
        assert content.startswith(b"%PDF-")
        assert hashlib.sha256(content).hexdigest() == fx.sha256

