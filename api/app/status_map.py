from __future__ import annotations
import json
import os
from typing import Dict, List
from pathlib import Path

_STATUS_MAP: Dict[str, Dict[str, List[str]]] = {}
_SCHEMA_VERSION = 1


def _default_status_map_path() -> str:
    """Resolve provider_status_map.json relative to repo root (stable across cwd).
    Falls back to CWD if necessary.
    """
    try:
        repo_root = Path(__file__).resolve().parents[2]
        p = repo_root / "config" / "provider_status_map.json"
        if p.exists():
            return str(p)
    except Exception:
        pass
    return os.path.join(os.getcwd(), "config", "provider_status_map.json")


def load_status_map(path: str | None = None) -> None:
    global _STATUS_MAP
    p = path or _default_status_map_path()
    try:
        with open(p, "r", encoding="utf-8") as f:
            obj = json.load(f)
        if not isinstance(obj, dict) or "providers" not in obj:
            raise ValueError("invalid status map schema")
        if int(obj.get("schema_version", 0)) != _SCHEMA_VERSION:
            # Accept but warn (best‑effort forward compatibility)
            pass
        _STATUS_MAP = obj.get("providers", {}) or {}
        # Basic validation: each provider has all canonical keys
        for prov, m in _STATUS_MAP.items():
            for key in ("queued", "in_progress", "success", "failed"):
                if key not in m:
                    raise ValueError(f"status map missing key '{key}' for provider '{prov}'")
    except Exception as e:
        # Fail open with empty map; callers should handle gracefully
        _STATUS_MAP = {}


def canonical_status(provider: str, raw_status: str) -> str:
    p = (provider or "").lower()
    raw = (raw_status or "").lower()
    m = _STATUS_MAP.get(p) or {}
    for canon, values in m.items():
        if raw in (values or []):
            return canon
    # default when unmapped
    return raw or "queued"
