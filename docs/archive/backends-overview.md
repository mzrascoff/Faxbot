
<div class="home-hero">
  <img src="/assets/images/faxbot_full_logo.png" alt="Faxbot logo" />
</div>

# Fax Backends

Every backend is selected and configured through the Admin Console → **Setup Wizard**. Pick the provider that matches your deployment, fill in the guided form, and Faxbot writes the plugin config for you—no manual YAML or environment gymnastics required.

{: .highlight }
**New in v3**: Hybrid configurations allow different providers for outbound (sending) and inbound (receiving) operations. Mix cloud and self-hosted backends for optimal cost and control.

{: .highlight }
Switching providers later is a guided flow. The wizard keeps configs isolated so Phaxio users never see SIP fields and vice versa.

## Cloud backends (fastest to production)

| Backend | Best for | Notes |
| ------- | -------- | ----- |
| [Phaxio](../setup/phaxio.md) | Healthcare & business teams that need BAAs and HIPAA-safe defaults | HMAC verification on by default; needs a public HTTPS URL for PDF fetch + callbacks |
| [Sinch Fax API v3](../setup/sinch.md) | “Phaxio by Sinch” accounts who prefer direct uploads | Uploads document to Sinch instead of providing a fetch URL; still HIPAA eligible |
| [Documo (mFax)](../setup/documo.md) | Hosted fax with quick number provisioning | Storage disabled by default to protect PHI |
| [SignalWire Compatibility](../setup/signalwire.md) | Teams already on SignalWire/Twilio-style APIs | Uses MediaUrl callbacks that Faxbot mints for each job |

## Self-hosted telephony (SIP/Freeswitch)

| Backend | Best for | Extra work |
| ------- | -------- | ---------- |
| [SIP/Asterisk](../setup/sip-asterisk.md) | High-volume operators who want total control | Requires SIP trunk, Asterisk dialplan, network isolation, AMI credentials |
| [FreeSWITCH](../setup/freeswitch.md) | Teams standardised on mod_spandsp | Uses `txfax` with dialplan result hooks back to Faxbot |

{: .warning }
Self-hosted backends expose PHI if you misconfigure networking. Keep AMI/ESL on private networks, restrict SIP ports to trunk provider IPs, and review the Security checklist inside each guide.

## Test & sandbox modes

- [Test Mode](../setup/test-mode.md) simulates every API response without ever calling a provider. Ideal for CI/CD and demos.
- The wizard exposes **Fax Disabled** as a provider choice. You can leave real credentials blank and still exercise the Admin Console and SDKs.

## Common prerequisites

The Setup Wizard links to these helper docs whenever a step requires extra context:

- [Public Access & Tunnels](../setup/public-access.md) — how to provide a short-lived HTTPS URL during evaluation.
- [Storage Choices](../guides/images-and-pdfs.md) — local vs S3/SSE-KMS handling for generated PDFs and TIFFs.
- [Callback Verification](../setup/webhooks.md) — enabling HMAC signatures for Phaxio, Sinch, and SignalWire.

Work through the page that matches your provider, apply the wizard changes, and you are ready to send from the Admin Console or either SDK.
