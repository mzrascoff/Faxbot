#!/usr/bin/env python3
"""Static diff of openapi.json against a pinned snapshot.

Place a snapshot at openapi_snapshot.json and run this script in CI.
Fail if the current openapi.json differs (route/shape drift).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
current = ROOT / "openapi.json"
snapshot = ROOT / "openapi_snapshot.json"

if not snapshot.exists():
    print("Snapshot not found (openapi_snapshot.json). Skipping.")
    sys.exit(0)

cur = json.loads(current.read_text(encoding="utf-8"))
snap = json.loads(snapshot.read_text(encoding="utf-8"))

if cur != snap:
    print("OpenAPI diff detected vs snapshot (openapi_snapshot.json)", file=sys.stderr)
    sys.exit(1)

print("OpenAPI unchanged vs snapshot")

