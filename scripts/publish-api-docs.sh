#!/usr/bin/env bash
set -euo pipefail

# Publish API docs to the sibling website repo for Netlify: ../faxbot.net
# - Pulls fresh OpenAPI JSON from the running API (fallback to api/openapi.json)
# - Converts to YAML (using convert_openapi.py)
# - Copies into faxbot.net/public/api/v1/
# - Creates lightweight Redoc + Swagger UI pages if missing
# - Commits and pushes to main (Netlify auto-deploys)

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
SITE_DIR=${SITE_DIR:-"$ROOT_DIR/../faxbot.net"}
PUB_API_DIR="$SITE_DIR/public/api"
V1_DIR="$PUB_API_DIR/v1"

if [ ! -d "$SITE_DIR/.git" ]; then
  echo "fatal: Expected sibling repo at $SITE_DIR (faxbot.net)." >&2
  exit 1
fi

echo "• Fetching OpenAPI JSON ..."
TMP_JSON="$ROOT_DIR/openapi.json"
if curl -sfS http://localhost:8080/openapi.json >/dev/null; then
  curl -sfS http://localhost:8080/openapi.json | jq . > "$TMP_JSON"
  echo "  - Fetched from local API ($(wc -c < "$TMP_JSON" | tr -d ' ') bytes)"
else
  cp "$ROOT_DIR/api/openapi.json" "$TMP_JSON"
  echo "  - API offline; using repo api/openapi.json ($(wc -c < "$TMP_JSON" | tr -d ' ') bytes)"
fi

echo "• Converting to YAML ..."
python3 "$ROOT_DIR/convert_openapi.py" >/dev/null 2>&1 || true
YAML_SRC="$ROOT_DIR/docs/openapi.yaml"

echo "• Writing site files ..."
mkdir -p "$V1_DIR"
cp "$TMP_JSON" "$V1_DIR/openapi.json"
[ -f "$YAML_SRC" ] && cp "$YAML_SRC" "$V1_DIR/openapi.yaml" || true

# Redoc page
if [ ! -f "$V1_DIR/index.html" ]; then
  cat > "$V1_DIR/index.html" <<'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Faxbot API — v1 Reference</title>
  <style>
    html, body { margin: 0; padding: 0; height: 100%; }
    body { font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial; }
    #redoc-container { height: 100%; }
  </style>
  <link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
  <link rel="dns-prefetch" href="//cdn.jsdelivr.net">
  <meta http-equiv="Cache-Control" content="no-store" />
  <meta http-equiv="Pragma" content="no-cache" />
  <meta http-equiv="Expires" content="0" />
  <link rel="icon" href="/favicon-32x32.png" />
  <meta name="theme-color" content="#2563eb" />
  <meta name="robots" content="index,follow" />
  <meta name="description" content="Faxbot API reference (v1). Open-source, self-hostable fax API with modular backends and HIPAA-aligned controls." />
  <meta property="og:title" content="Faxbot API — v1 Reference" />
  <meta property="og:description" content="Open-source, self-hostable fax API with modular backends and HIPAA-aligned controls." />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://faxbot.net/api/v1/" />
  <meta property="og:image" content="/og-image.png" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="Faxbot API — v1 Reference" />
  <meta name="twitter:description" content="Open-source, self-hostable fax API with modular backends and HIPAA-aligned controls." />
  <meta name="twitter:image" content="/og-image.png" />
</head>
<body>
  <div id="redoc-container"></div>
  <script>
    const p = new URLSearchParams(window.location.search);
    const specUrl = p.get('spec') || 'openapi.json';
  </script>
  <script src="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"></script>
  <script>
    Redoc.init(specUrl, {
      hideDownloadButton: false,
      expandResponses: '200,201,400,401,403,404,413,415',
      pathInMiddlePanel: true,
      theme: { colors: { primary: { main: '#2563eb' } } }
    }, document.getElementById('redoc-container'));
  </script>
  <noscript>Enable JavaScript to view the API reference.</noscript>
</body>
</html>
EOF
fi

# Swagger page
if [ ! -f "$V1_DIR/swagger.html" ]; then
  cat > "$V1_DIR/swagger.html" <<'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Faxbot API — Swagger UI (v1)</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
  <style> html, body { margin:0; padding:0; height:100%; } #swagger-ui { height:100%; }</style>
</head>
<body>
  <div id="swagger-ui"></div>
  <script>
    const params = new URLSearchParams(window.location.search);
    const url = params.get('url') || 'openapi.json';
  </script>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-standalone-preset.js"></script>
  <script>
    window.ui = SwaggerUIBundle({
      url,
      dom_id: '#swagger-ui',
      deepLinking: true,
      presets: [SwaggerUIBundle.presets.apis, SwaggerUIStandalonePreset],
      layout: 'StandaloneLayout',
      tryItOutEnabled: false
    });
  </script>
</body>
</html>
EOF
fi

# API landing index
if [ ! -f "$PUB_API_DIR/index.html" ]; then
  mkdir -p "$PUB_API_DIR"
  cat > "$PUB_API_DIR/index.html" <<'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Faxbot API</title>
  <style>
    body { font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial; max-width: 840px; margin: 2rem auto; padding: 0 1rem; }
    .card { border: 1px solid #e5e7eb; border-radius: 12px; padding: 1.25rem; background: #fafafa; }
    a { color: #2563eb; text-decoration: none; } a:hover { text-decoration: underline; }
    .badge { display:inline-block; background:#059669; color:#fff; padding:0.1rem 0.5rem; border-radius:6px; font-size:0.85rem; margin-left:0.5rem; }
  </style>
</head>
<body>
  <h1>Faxbot API Documentation</h1>
  <p>Open-source, self-hostable fax API with modular backends and HIPAA-aligned controls.</p>

  <div class="card">
    <h3>API v1 <span class="badge">Current</span></h3>
    <p><a href="/api/v1/">📚 Redoc Reference</a> · <a href="/api/v1/swagger.html">🔍 Swagger UI</a></p>
    <p>Spec: <a href="/api/v1/openapi.json">JSON</a> · <a href="/api/v1/openapi.yaml">YAML</a></p>
  </div>
</body>
</html>
EOF
fi

echo "• Committing to website repo ..."
cd "$SITE_DIR"
git add public/api
if git diff --staged --quiet; then
  echo "No changes to commit."
else
  git commit -m "docs(api): update /api/v1 OpenAPI + reference"
  git push origin main
fi

echo "✅ Done. Netlify will auto-deploy to /api and /api/v1"

