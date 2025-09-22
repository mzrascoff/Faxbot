# Images and PDFs (Conversion)

Most real‑world faxes are scans of insurance cards, lab results, licenses, or signed forms. Faxbot supports two content types only: PDF and TXT. This guide explains how to handle image content and how to balance file size with HIPAA concerns.

Quick guidance
- If you have a PDF that is a scan/photo (image‑based): send it as‑is.
- If you have a pure text document: send `.txt` or export as PDF.
- If you have images (PNG/JPG): convert to PDF first, then send.

Conversions
- macOS Preview: File → Export As… → Format: PDF
- macOS CLI: `sips -s format pdf "in.png" --out "out.pdf"`
- Linux: `img2pdf in.png -o out.pdf` or `magick convert in.png out.pdf`
- Windows: open image → Print → “Microsoft Print to PDF”

MCP tooling: which option to use?
- `send_fax` with `filePath` (stdio) — recommended for all PDFs (image or text). Sends the original file.
- HTTP/SSE MCP transports — require base64; keep files small (≤ ~100 KB), or prefer stdio with `filePath` for local usage.

File size and quality
- API default limit is `MAX_FILE_SIZE_MB=10`.
- For scans, use 150–200 DPI and grayscale when possible.

HIPAA considerations
- Healthcare users: use HIPAA‑aligned transports and controls.
  - Prefer OAuth‑protected SSE MCP for assistants or use the REST API/SDKs directly.
  - Use HTTPS for `PUBLIC_API_URL` (cloud backends) and enable signature verification where supported.
- Non‑healthcare: stdio MCP with `filePath` avoids base64 bloat; token limits don’t apply.

Troubleshooting
- “Unsupported file type”: only PDF and TXT are accepted.
- Paths with spaces/special chars: quote the path or rename using a wildcard (e.g., `cp Screenshot*.pdf card.pdf`).
