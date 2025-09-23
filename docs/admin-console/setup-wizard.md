# Setup Wizard (Beginner Friendly)

New to fax? Start here. This wizard gets you sending in minutes and explains each choice with inline help and deep links.

What you’re choosing
- Phaxio by Sinch (cloud): Phaxio fetches your PDF from your server via a public URL (webhooks for status). Best if you have a domain/tunnel.
- Sinch (Direct Upload): Faxbot uploads the PDF directly (send‑only works without a public URL).
- Documo (mFax): Direct upload; no public URL required for sending.
- SIP / Asterisk (self‑hosted): No third‑party cloud, uses your SIP trunk (advanced).

Do I need a domain?
- No, if you pick “Sinch (Direct Upload)” or Documo.
- Yes (or a tunnel) if you pick “Phaxio” and want callbacks or provider PDF fetch.

Beginner 5‑minute path (no domain required)
1) Choose backend: “Sinch (Direct Upload)”.
2) Create a Sinch/Phaxio account and project; obtain Project ID, API key/secret.
3) Paste values into the wizard and Apply.

If you have a domain (or can run a temporary tunnel)
1) Choose backend: “Phaxio (Recommended)”.
2) Get `PHAXIO_API_KEY`/`PHAXIO_API_SECRET`.
3) Set `PUBLIC_API_URL` (domain or quick tunnel) and Apply.

After Apply, send a test fax from the console or via SDK.
