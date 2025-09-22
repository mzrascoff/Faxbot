#!/usr/bin/env bash
set -euo pipefail

# Fetch fresh OpenAPI JSON from a running Faxbot API and regenerate YAML
# Usage: ./scripts/regenerate-openapi-yaml.sh [BASE_URL]
# Default BASE_URL: http://localhost:8080

BASE_URL="${1:-http://localhost:8080}"

echo "Fetching OpenAPI from ${BASE_URL}/openapi.json ..."
curl -sfSL "${BASE_URL}/openapi.json" | jq . > openapi.json
echo "Saved fresh JSON to openapi.json ($(wc -c < openapi.json | tr -d ' ') bytes)"

python3 convert_openapi.py
echo "Done. Wrote docs/openapi.yaml (anyOf removed, OAS 3.1 type unions)."
