# SIP/Asterisk Setup (Self-hosted)

## Overview
- Self-hosted backend using Asterisk and a SIP trunk with T.38 fax.
- Send-only. You don’t need to accept inbound faxes to send.
- Full control, no per-fax cloud charges (you still pay your trunk provider).
- Requires networking setup; this guide assumes minimal prior knowledge.

## What is Asterisk AMI?
- AMI (Asterisk Manager Interface) is a TCP interface on port 5038 that lets applications control Asterisk (originate calls, subscribe to events). Faxbot uses AMI to originate fax calls (outbound) and to receive fax results (events).
- Security: AMI must stay on private networks only. Never expose 5038 to the internet.

## What Is SIP? (Crash Course)
- SIP: signaling protocol to set up calls over the internet.
- SIP Trunk: your account/connection to a carrier that places calls to the PSTN.
- DID: a phone number you can buy from a SIP provider. For sending only, a DID is optional but recommended.
- T.38: protocol for fax over IP using UDPTL; more reliable than voice codecs for fax.
- UDPTL: transport for T.38; open/forward a port range for it.
- E.164: the international phone number format (e.g., `+15551234567`).

## Requirements
- A SIP trunk that supports T.38 over UDPTL
- A public/static IP or NAT configured to forward required ports
- Docker and Docker Compose

## Networking
- SIP signaling: `5060/tcp+udp`
- AMI (Manager): `5038/tcp` (internal only)
- T.38 UDPTL media: `4000–4999/udp`
- If behind NAT, forward 5060 (tcp+udp) and 4000–4999/udp to the Asterisk host. Keep 5038 internal.

## Configure Environment
Edit `.env`:
```
FAX_BACKEND=sip

# AMI (used by API to originate fax calls)
ASTERISK_AMI_HOST=asterisk
ASTERISK_AMI_PORT=5038
ASTERISK_AMI_USERNAME=api
ASTERISK_AMI_PASSWORD=change_me_safe

# SIP trunk (from your provider)
SIP_USERNAME=your_username
SIP_PASSWORD=your_password
SIP_SERVER=sip.provider.example
SIP_FROM_USER=+15551234567
SIP_FROM_DOMAIN=sip.provider.example

# Presentation
FAX_LOCAL_STATION_ID=+15551234567
FAX_HEADER=Your Org Name
```

## Start Services
```
docker compose up -d --build
```
- API on `8080`, Asterisk on `5060/udp`, `5060/tcp`, AMI on `5038`, UDPTL `4000–4999/udp`.

## How It Works
1. API converts input file to PDF, then to fax-optimized TIFF (Ghostscript).
2. API creates a job and originates a Local channel via AMI.
3. Asterisk dials your SIP trunk; on answer, executes `SendFAX()` in T.38.
4. Asterisk emits `UserEvent(FaxResult, ...)`; API updates job status.

## Logs & Debugging
- API: `docker compose logs -f api`
- Asterisk: `docker compose logs -f asterisk`
- Inside Asterisk shell: `docker exec -it <asterisk_container> asterisk -rvvv`
  - Check module load: `module show like fax`
  - Call flow: watch for `SendFAX` and `FaxResult` events

## Common Pitfalls
- T.38 disabled at provider → enable UDPTL and verify `udptl.conf` range.
- NAT issues → enable `rtp_symmetric`, `force_rport`, correct `match` and `from_domain`.
- Wrong credentials → check `pjsip.conf` generated from templates.
- Ghostscript missing → install for production.
- CGNAT / no port forwarding → use a cloud VM or Phaxio backend.

## Test Send
```
curl -X POST http://localhost:8080/fax \
  -H "X-API-Key: fbk_live_<keyId>_<secret>" \
  -F to=+15551234567 \
  -F file=@./example.pdf
```

Auth tip
- For production, set `REQUIRE_API_KEY=true` and create per‑user/service keys via `POST /admin/api-keys` using a temporary bootstrap env `API_KEY`.

## Inbound Receiving Quickstart (Optional)

Enable inbound in your `.env`:
```
INBOUND_ENABLED=true
ASTERISK_INBOUND_SECRET=<random>
```

Add a minimal inbound dialplan (example):
```
[fax-inbound]
exten => _X.,1,NoOp(Fax inbound DID ${EXTEN} from ${CALLERID(num)})
 same => n,Set(FAXFILE=/faxdata/${UNIQUEID}.tiff)
 same => n,ReceiveFAX(${FAXFILE})
 same => n,System(curl -s -X POST http://api:8080/_internal/asterisk/inbound \
   -H "X-Internal-Secret: ${ASTERISK_INBOUND_SECRET}" \
   -H "Content-Type: application/json" \
   -d '{"tiff_path":"${FAXFILE}","to_number":"${EXTEN}","from_number":"${CALLERID(num)}","faxstatus":"${FAXSTATUS}","faxpages":"${FAXPAGES}","uniqueid":"${UNIQUEID}"}')
 same => n,Hangup()
```

Verify inbound with helper scripts:
- Internal smoke (no SIP required): `scripts/inbound-internal-smoke.sh`
- E2E watch: `scripts/e2e-inbound-sip.sh`
