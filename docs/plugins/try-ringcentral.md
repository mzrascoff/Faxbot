# Try It: RingCentral Manifest

This walkthrough shows how to add a RingCentral manifest, enable it, and send a quick test.

## Prerequisites

- Enable v3 plugins on the API:

```env
FEATURE_V3_PLUGINS=true
```

- Restart the API if you changed env.

## 1) Create the manifest file

Create `config/providers/ringcentral/manifest.json` on the API host:

```json
{
  "id": "ringcentral",
  "name": "RingCentral Fax API",
  "auth": { "scheme": "bearer" },
  "traits": {
    "kind": "cloud",
    "requires_ghostscript": true,
    "requires_tiff": false,
    "supports_inbound": false,
    "inbound_verification": "none",
    "needs_storage": false,
    "outbound_status_only": false
  },
  "actions": {
    "send_fax": {
      "method": "POST",
      "url": "https://platform.ringcentral.com/restapi/v1.0/account/~/extension/~/fax",
      "body": {
        "kind": "multipart",
        "template": "request={\\"to\\":[{\\"phoneNumber\\":\\"{{to}}\\"}]}&attachment={{file}}"
      },
      "response": { "faxId": "id" }
    },
    "get_status": {
      "method": "GET",
      "url": "https://platform.ringcentral.com/restapi/v1.0/account/~/message-store/{{fax_id}}",
      "body": { "kind": "none", "template": "" },
      "response": { "status": "messageStatus", "sentPages": "faxPageCount" }
    }
  },
  "allowed_domains": ["platform.ringcentral.com"],
  "timeout_ms": 15000
}
```

Notes
- Do not put secrets in the manifest. Credentials are provided via Admin Console or env.

## 2) Enable + configure in Admin Console

1. Open Admin Console → Plugins  
2. Select `ringcentral` → toggle Enabled  
3. Fill required settings (tokens/keys) per your account  
4. Click Save/Apply

Alternatively (API):

```bash
BASE="http://localhost:8080"; API_KEY="your_admin_api_key"
curl -sS -X PUT "$BASE/plugins/ringcentral/config" \
  -H "X-API-Key: $API_KEY" -H 'content-type: application/json' \
  -d '{"enabled":true, "settings": {"access_token":"..."}}'
```

## 3) Send a quick test

Use the Admin Console → Send Fax, or run:

```bash
BASE="http://localhost:8080"; API_KEY="your_api_key"
curl -X POST "$BASE/fax" \
  -H "X-API-Key: $API_KEY" \
  -F to=+15551234567 \
  -F file=@./example.pdf
```

Then check status:

```bash
curl -H "X-API-Key: $API_KEY" "$BASE/fax/$JOB_ID"
```

