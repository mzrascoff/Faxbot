# Try It: InterFAX Manifest

This walkthrough shows how to add an InterFAX manifest, enable it, and send a quick test.

## Prerequisites

- Enable v3 plugins on the API:

```env
FEATURE_V3_PLUGINS=true
```

- Restart the API if you changed env.

## 1) Create the manifest file

Create `config/providers/interfax/manifest.json` on the API host:

```json
{
  "id": "interfax",
  "name": "InterFAX API",
  "auth": { "scheme": "basic" },
  "traits": { "kind": "cloud", "requires_ghostscript": true, "requires_tiff": false, "supports_inbound": false, "inbound_verification": "none", "needs_storage": false, "outbound_status_only": false },
  "actions": {
    "send_fax": {
      "method": "POST",
      "url": "https://rest.interfax.net/outbound/faxes?faxNumber={{to}}",
      "headers": { "Content-Location": "{{file_url}}", "Content-Type": "application/pdf" },
      "body": { "kind": "none", "template": "" },
      "response": { "faxId": "id" }
    },
    "get_status": {
      "method": "GET",
      "url": "https://rest.interfax.net/outbound/faxes/{{fax_id}}",
      "body": { "kind": "none", "template": "" },
      "response": { "status": "status" }
    }
  },
  "allowed_domains": ["rest.interfax.net"]
}
```

## 2) Enable + configure

1. Admin Console → Plugins → `interfax` → Enable  
2. Provide account credentials (Basic auth)  
3. Save/Apply

## 3) Test

```bash
BASE="http://localhost:8080"; API_KEY="your_api_key"
curl -X POST "$BASE/fax" -H "X-API-Key: $API_KEY" -F to=+15551234567 -F file=@./example.pdf
```

