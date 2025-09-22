#!/usr/bin/env bash
set -euo pipefail

# Serve the docs/ folder locally and open ReDoc and Swagger UI
# Usage: ./scripts/preview-openapi-docs.sh [PORT]
PORT=${1:-8081}

cd "$(dirname "$0")/.."/docs

echo "Serving docs/ at http://localhost:${PORT}"
echo "ReDoc:    http://localhost:${PORT}/redoc.html"
echo "Swagger:  http://localhost:${PORT}/swagger.html"
echo "YAML:     http://localhost:${PORT}/openapi.yaml"

python3 -m http.server "${PORT}"

