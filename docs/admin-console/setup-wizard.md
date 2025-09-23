# Setup Wizard (Beginner Friendly)

New to fax? Start here. This wizard gets you sending in minutes and explains each choice in plain language, with direct links to the third‑party pages you’ll need.

What you’re choosing
- Phaxio by Sinch (cloud): A developer fax API (Phaxio is part of Sinch). Two flows in Faxbot:
  - Phaxio: provider fetches your PDF from a public URL. Best if you have a domain/tunnel. Supports webhooks.
  - Sinch (Direct Upload): Faxbot uploads the PDF directly. Send‑only works without a public URL.
- Documo (mFax): Direct upload; no public URL required for sending.
- SIP / Asterisk (self‑hosted): Uses your SIP trunk. Advanced.

Do I need a domain?
- No, if you pick “Sinch (Direct Upload)”.
- Yes (or a tunnel) if you pick “Phaxio” and want status callbacks or provider PDF fetch.

Beginner 5‑minute path (no domain required)
1) Choose backend: “Sinch (Direct Upload)”.
2) Sign up at the Sinch dashboard; create a project; get Project ID and API key/secret.
3) Paste values into the wizard and Apply. Send a test fax in Admin Console.

If you have a domain (or can run a temporary tunnel)
1) Choose backend: “Phaxio (Recommended)”.
2) Get `PHAXIO_API_KEY` and `PHAXIO_API_SECRET`.
3) Set `PUBLIC_API_URL` and Apply. Use the tunnel helper if needed.
