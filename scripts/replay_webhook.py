#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Any

import httpx


def main() -> int:
    ap = argparse.ArgumentParser(description="Replay a saved inbound webhook payload against a local Faxbot endpoint")
    ap.add_argument("endpoint", help="Target endpoint URL (e.g., http://localhost:8080/phaxio-inbound)")
    ap.add_argument("file", help="Path to JSON file containing {headers, body}")
    ap.add_argument("--api-key", dest="api_key", default=None, help="X-API-Key if required")
    args = ap.parse_args()

    with open(args.file, "r", encoding="utf-8") as f:
        data: Any = json.load(f)
    headers = dict(data.get("headers") or {})
    body = data.get("body")
    if isinstance(body, dict):
        body_bytes = json.dumps(body).encode()
        headers.setdefault("Content-Type", "application/json")
    elif isinstance(body, str):
        body_bytes = body.encode()
    else:
        print("Invalid body format in replay file; expected object or string", file=sys.stderr)
        return 2
    if args.api_key:
        headers["X-API-Key"] = args.api_key
    start = time.time()
    with httpx.Client(timeout=30.0) as client:
        r = client.post(args.endpoint, content=body_bytes, headers=headers)
    print(f"Status: {r.status_code} ({round((time.time()-start)*1000)} ms)")
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print(r.text)
    return 0 if r.status_code < 400 else 1


if __name__ == "__main__":
    raise SystemExit(main())


