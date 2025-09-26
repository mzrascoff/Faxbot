#!/usr/bin/env python3
"""Validate config/provider_traits.json against config/provider_traits.schema.json.

Usage:
  python scripts/ci/validate_provider_traits.py

Exits non-zero on validation error.
"""
import json
import sys
from pathlib import Path

try:
    import jsonschema
except Exception as e:
    print("jsonschema is required (pip install jsonschema)", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[2]
schema_path = ROOT / "config" / "provider_traits.schema.json"
traits_path = ROOT / "config" / "provider_traits.json"

with schema_path.open("r", encoding="utf-8") as f:
    schema = json.load(f)
with traits_path.open("r", encoding="utf-8") as f:
    traits = json.load(f)

try:
    jsonschema.validate(instance=traits, schema=schema)
except jsonschema.ValidationError as e:
    print("provider_traits.json validation error:", file=sys.stderr)
    print(e.message, file=sys.stderr)
    print("At:", list(e.path), file=sys.stderr)
    sys.exit(1)

print("provider_traits.json is valid")

