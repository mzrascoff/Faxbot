# Vivi Landing Page Copy - HackerNews/YC Audience

## Hero Section

**Headline:** The first open-source, self-hostable fax server with AI integration
**Subhead:** Born from spite, built for HIPAA, accidentally revolutionary

**CTA:** `git clone https://github.com/dmontgomery40/vivi && docker compose up`

## The Origin Story (Main Section)

### I Built This Because I Was Pissed Off

Last year I had some health issues. Lots of doctor visits, hospital stays, the works. One doctor didn't even take email—everything through some awful patient portal. I'm driving there, running 10 minutes late, call to let them know. Four-minute answering machine message. No skip button.

All I wanted was: "Hey Siri, fax Dr. Henderson that I'm 10 minutes late."

Couldn't do it. Went home angry. Figured there had to be an open-source solution for this, right? Checked GitHub. **Nothing.** Not one self-hostable fax server that wasn't either dead, enterprise-only, or complete garbage.

So I built one.

### I Had No Idea What I Was Doing

Here's the thing: I'm not a telecom expert. When hospitals started asking about HIPAA compliance, I panicked. When they mentioned handling PHI, I panicked harder.

So I overengineered the hell out of everything:
- Made every component pluggable (if something breaks, unplug it)
- Went way overboard on security (HIPAA fines are no joke)
- Built APIs for everything (because I'd probably need them later)
- Added AI integration as a plugin (seemed obvious but apparently nobody else did it)

Being dyslexic didn't help—after coding for hours, text becomes symbol soup. Had to build a UI so good even I could use it when my brain was fried.

### Accidentally Built Something Revolutionary

Turns out, building defensively creates good architecture. Who knew?

**What started as "don't break production"** became:
- Universal plugin system (swap user management, storage, providers, even the UI)
- Security-first design (every request audited, encrypted, validated)
- AI-native architecture (MCP servers, multiple transports, canonical message routing)
- Trait-based access control (HIPAA and non-HIPAA users get different experiences)
- True multi-tenancy (one instance, multiple hospitals, proper isolation)

## Technical Reality Check

### What It Actually Does
- **Sends faxes** via cloud providers (Phaxio, Sinch) or self-hosted SIP/Asterisk
- **Receives faxes** with configurable routing and storage
- **AI integration** through MCP servers (stdio, HTTP, SSE transports)
- **REST APIs** with Node.js and Python SDKs
- **Admin console** that doesn't suck
- **HIPAA compliance** built-in, not bolted-on

### What Makes It Different
- **Everything is pluggable**: User management, storage, providers, even the frontend
- **Security boundaries**: Plugins can't bypass core security or HIPAA controls
- **Canonical message format**: Universal translation layer between any communication method
- **Trait-based permissions**: Users get appropriate UX for their compliance requirements
- **Real documentation**: Written by humans, tested in production

## The Architecture (For the Technical Folks)

```
Core Platform (Unchangeable)
├── API Layer (FastAPI)
├── Security & HIPAA Compliance
├── Audit & Observability
├── MCP Servers (AI Integration)
├── Canonical Message Router
└── Plugin Sandbox

Plugin Extensions (Replaceable)
├── Identity Providers (Built-in, LDAP, SAML, Custom ERP)
├── Communication Channels (Fax, Email, SMS, Webhooks)
├── Storage Backends (Local, S3, PostgreSQL, Custom)
└── Frontend Components (React Admin Console, Custom UIs)
```

**Translation:** The core handles security, compliance, and message routing. Plugins handle everything else. Customers can replace any plugin with their own implementation while keeping all security guarantees.

## Current Status

### Production Ready
- ✅ Multiple hospitals in production
- ✅ Handling PHI in HIPAA-compliant environments
- ✅ Full test suite and diagnostics
- ✅ Docker deployment with docker-compose
- ✅ Comprehensive documentation

### Roadmap
- **Phase 1**: Email-to-fax gateway (for non-HIPAA users)
- **Phase 2**: Enhanced HIPAA features (encrypted storage plugins, PHI detection)
- **Phase 3**: Plugin marketplace and advanced integrations

## For VCs and Business Types

### Traction
- Production deployments at healthcare organizations
- Growing interest from non-healthcare enterprises
- Developer adoption through AI tool integrations
- Revenue from commercial support and hosting

### Market Opportunity
- **Healthcare**: $X billion fax market, moving slowly to digital
- **Enterprise**: Secure document transmission for legal, financial, government
- **Platform Play**: Communication infrastructure for AI agents and automation

### Competitive Advantage
- **Only open-source player** in a proprietary market
- **AI-native architecture** while competitors bolt on AI later
- **Plugin ecosystem** creates customer lock-in through integration, not vendor lock-in through opacity
- **Security-first design** enables expansion into regulated industries

## Get Started

### Developers
```bash
git clone https://github.com/dmontgomery40/vivi
cd vivi
docker compose up
# Admin console at http://localhost:8080/admin/ui
```

### Healthcare/Enterprise
- Self-hosted deployment with full HIPAA compliance
- Commercial support and SLA available
- Custom plugin development services
- Migration assistance from legacy systems

---

## FAQ

**Q: Why "Vivi"?**
A: Named after my daughter. The domain vivi.com costs $429k. vivified.dev was $21.

**Q: Is this actually HIPAA compliant?**
A: Yes. Built-in audit logging, encryption at rest and in transit, access controls, and comprehensive documentation. Multiple healthcare organizations using it in production.

**Q: What about SLA/support?**
A: Open source is free. Commercial support with SLA available. We also offer hosted deployment if you don't want to run infrastructure.

**Q: Can I replace the user management?**
A: Yes. Write a plugin implementing the identity provider interface. Customers have integrated with LDAP, SAML, and custom ERP systems.

**Q: What AI integrations work?**
A: Claude Desktop, Cursor, or any MCP-compatible client. Three transport options (stdio, HTTP, SSE) with OAuth2 support.

**Q: How is this different from [existing solution]?**
A: Most fax services are SaaS-only, closed-source, or don't handle HIPAA properly. This is the first open-source, self-hostable solution with AI integration and enterprise-grade architecture.

---

## Contact

- **GitHub**: github.com/dmontgomery40/vivi
- **Documentation**: vivified.dev/docs
- **Commercial inquiries**: [business email]
- **Developer questions**: [technical email]

*Built with spite, deployed with care.*