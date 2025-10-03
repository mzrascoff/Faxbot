#!/usr/bin/env bash
set -euo pipefail

# One-shot: start API + Cloudflare tunnel, detect public URL, set callback base, and register HumbleFax webhook.
# Usage: scripts/setup-humblefax-tunnel.sh

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "[error] docker is required" >&2; exit 1
fi

API_KEY=${API_KEY:-fbk_live_local_admin}

echo "[1/5] Starting API + Cloudflare tunnel sidecar (compose profile) ..."
docker compose --profile cloudflare up -d --build api cloudflared >/dev/null

LOG_PATH="${ROOT_DIR}/cloudflared-logs/cloudflared.log"
echo "[2/5] Waiting for public URL in: ${LOG_PATH}"
for i in $(seq 1 60); do
  if [ -f "$LOG_PATH" ]; then
    URL=$(grep -Eo 'https://[a-zA-Z0-9-]+\.trycloudflare\.com' "$LOG_PATH" | tail -1 || true)
    if [ -n "$URL" ]; then echo "$URL" > /tmp/HF_TUNNEL_URL; break; fi
  fi
  sleep 1
done

if [ ! -s /tmp/HF_TUNNEL_URL ]; then
  echo "[error] Could not detect Cloudflare public URL in logs." >&2
  echo "Check logs: docker compose logs cloudflared | tail -n 100" >&2
  exit 1
fi

HF_TUNNEL=$(cat /tmp/HF_TUNNEL_URL)
echo "[info] Detected tunnel: $HF_TUNNEL"

echo "[3/5] Waiting for API readiness ..."
for i in $(seq 1 60); do
  if curl -sS "http://localhost:8080/health" >/dev/null; then break; fi
  sleep 1
done

echo "[3/5] Setting HumbleFax callback base and selecting humblefax inbound/outbound ..."
PAYLOAD="{\"humblefax_callback_base\":\"$HF_TUNNEL\",\"inbound_backend\":\"humblefax\",\"outbound_backend\":\"humblefax\"}"
for i in $(seq 1 5); do
  set +e
  RESP=$(curl -sS -X PUT "http://localhost:8080/admin/settings" \
    -H "X-API-Key: ${API_KEY}" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")
  code=$?
  set -e
  if [ $code -eq 0 ]; then echo "$RESP" >/dev/null; break; fi
  echo "[warn] settings update retry $i ..."; sleep 2
done

echo "[4/5] Registering HumbleFax webhook ..."
curl -sS -X POST "http://localhost:8080/admin/inbound/register-humblefax" \
  -H "X-API-Key: ${API_KEY}" -H "Content-Type: application/json"

echo
echo "[5/5] Current callbacks:"
curl -sS "http://localhost:8080/admin/inbound/callbacks" -H "X-API-Key: ${API_KEY}" || true

echo
echo "[done] Webhook points to: $HF_TUNNEL/inbound/humblefax/webhook"
