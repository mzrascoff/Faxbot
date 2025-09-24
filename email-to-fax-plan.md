# Email-to-Fax — Plan (alpha)

## Goals (Non-HIPAA MVP First)

### Phase 1: MVP for Non-Healthcare Users
- Zero-install, optional feature to send faxes by emailing attachments to a gateway address
- Receive inbound faxes as email attachments to a configured mailbox
- OAuth-only mail access (no raw passwords), basic logging, feature OFF by default
- Self-hosted friendly; no SaaS dependency
- **HIPAA users**: Feature completely disabled until Phase 2 compliance work
- Focus on getting core functionality working with Gmail/Outlook for non-PHI use cases

### Phase 2: HIPAA Compliance Enhancement (Future)

#### Database Plugin Architecture
**Problem**: SQLite insufficient for HIPAA; need enterprise-grade, encrypted storage

**Solution**: Extend existing plugin system for database backends
```python
# api/app/plugins/database/
├── base_database_provider.py      # Abstract interface
├── providers/
│   ├── postgresql_encrypted.py    # PostgreSQL with row-level encryption
│   ├── s3_kms_storage.py          # S3 with KMS encryption
│   └── azure_sql_always_encrypted.py  # Azure SQL with Always Encrypted
└── manager.py                     # Plugin discovery and lifecycle
```

**Database Plugin Interface**:
```python
class DatabaseProvider(ABC):
    @abstractmethod
    def store_email_event(self, event: EmailEvent) -> str: pass

    @abstractmethod
    def store_oauth_token(self, token: EncryptedOAuthToken) -> None: pass

    @abstractmethod
    def get_email_events(self, filters: EventFilters) -> List[EmailEvent]: pass

    @abstractmethod
    def encrypt_at_rest(self, data: bytes, key_id: str) -> bytes: pass

    @abstractmethod
    def audit_access(self, user_id: str, resource: str, action: str) -> None: pass
```

#### HIPAA-Specific Features
1. **PHI Detection & Classification**
   - Content scanning for SSN, DOB, medical record numbers
   - Automatic encryption of detected PHI fields
   - Risk scoring and quarantine for high-risk content

2. **Enhanced Encryption**
   - End-to-end encryption for email attachments
   - Key management with HSM integration
   - Field-level encryption for database storage
   - Encryption in transit with mutual TLS

3. **Advanced Access Controls**
   - Role-based access control (RBAC) with healthcare roles
   - Multi-factor authentication for admin functions
   - Session management with timeout controls
   - Segregation of duties for configuration changes

4. **Audit & Compliance**
   - Comprehensive audit trail with tamper protection
   - HIPAA-compliant log retention (6 years)
   - Automated compliance reporting
   - Breach detection and notification workflows

5. **Data Lifecycle Management**
   - Automated data retention policies
   - Secure deletion with cryptographic shredding
   - Data loss prevention (DLP) integration
   - Backup encryption with key escrow

#### Environment Configuration (Phase 2)
```bash
# HIPAA Mode Activation
HIPAA_MODE=true                           # Enables HIPAA-compliant features
EMAIL_GATEWAY_HIPAA_READY=true            # Must be true to enable in HIPAA mode

# Database Plugin
DATABASE_PLUGIN=postgresql_encrypted       # Plugin identifier
POSTGRES_ENCRYPTION_KEY_ID=kms://aws/hipaa-key
POSTGRES_TDE_ENABLED=true                 # Transparent data encryption

# PHI Detection
PHI_DETECTION_ENABLED=true                # Scan content for PHI
PHI_QUARANTINE_THRESHOLD=0.7              # Risk score threshold
PHI_ENCRYPTION_REQUIRED=true              # Force encrypt detected PHI

# Enhanced Security
MFA_REQUIRED_FOR_EMAIL_CONFIG=true        # Multi-factor auth for config
SESSION_TIMEOUT_MINUTES=15                # Idle session timeout
AUDIT_LOG_TAMPER_PROTECTION=true          # Cryptographic audit log integrity

# Compliance
DATA_RETENTION_YEARS=6                    # HIPAA-required retention
BREACH_NOTIFICATION_EMAIL=security@company.com
COMPLIANCE_REPORTING_ENABLED=true         # Generate compliance reports
```

#### Migration Path from Phase 1 to Phase 2
1. **Database Migration**: Automated tool to migrate SQLite data to encrypted backend
2. **Configuration Upgrade**: Convert Phase 1 env vars to Phase 2 format
3. **Security Assessment**: Built-in HIPAA readiness checker
4. **Training Mode**: Gradual rollout with compliance monitoring
5. **Certification Support**: Documentation and evidence collection for audits

#### Implementation Priority for Phase 2
1. Database plugin system (enables secure storage)
2. PHI detection engine (protects sensitive content)
3. Enhanced encryption layer (secures data at rest/transit)
4. RBAC and MFA (strengthens access controls)
5. Audit and compliance framework (ensures regulatory compliance)
6. BAA integration and vendor management (enables provider relationships)

## Detailed Processing Workflows

### Outbound Email-to-Fax Flow
1. **Email Monitoring**
   - Background worker polls OAuth-authenticated mailbox every 60 seconds
   - Check for unread messages in INBOX
   - Use Message-ID for deduplication (store in `email_events` table)

2. **Email Processing Pipeline**
   ```
   New Email → Validate Sender → Parse Destination → Process Attachments → Create Fax Job → Send Status Reply
   ```

   **Destination Parsing** (flexible formats):
   - Subject: `Fax to +15551234567: Document title`
   - Subject: `fax:+15551234567`
   - Body: First line starting with `Fax:` or `To:` followed by E.164 number
   - Fallback: Look for any E.164 number in subject/body

   **Attachment Validation**:
   - Accept: PDF (≤10MB), TXT (≤1MB, convert to PDF)
   - Reject: Archives (ZIP, RAR), executables, images (Phase 2: convert)
   - Multiple attachments: Process each as separate fax job

3. **Fax Job Creation**
   - Save attachment to temporary path in faxdata/
   - Call existing `POST /fax` endpoint with file path
   - Store email-to-fax mapping in database
   - Queue cleanup of temporary files

4. **Status Email Replies**
   ```
   Subject: Re: [Original Subject] - Fax Status: [QUEUED|SENT|FAILED]

   Your fax to +15551234567 has been [queued|sent successfully|failed].

   Job ID: abc123
   Pages: 3
   Status: Delivered at 2024-01-15 14:30 UTC

   [If failed: Error details and troubleshooting guidance]
   ```

### Inbound Fax-to-Email Flow
1. **Trigger**: Existing inbound webhook receives fax
2. **Email Generation**:
   - From: `noreply@[your-domain]`
   - To: Configured distribution list (`EMAILFAX_INBOUND_DISTRO`)
   - Subject: `Inbound Fax from +15551234567 - [timestamp]`
   - Body: Metadata (sender, pages, size, received time)
   - Attachment: Original PDF from inbound processing

3. **Security Considerations**:
   - Rate limiting: Max 20 inbound emails per hour
   - Size limits: Skip if PDF >25MB (log warning)
   - Distribution validation: Verify all recipient addresses

## Architecture Overview

### Core Components

#### 1. Database Schema (MVP Extensions)
Extend existing SQLite schema with new tables:
```sql
-- Email processing events (dedupe and tracking)
CREATE TABLE email_events (
    id TEXT PRIMARY KEY,
    message_id TEXT UNIQUE NOT NULL,  -- Email Message-ID header
    from_address TEXT NOT NULL,
    to_address TEXT NOT NULL,
    subject TEXT,
    processing_status TEXT DEFAULT 'received',  -- received, processing, completed, failed
    fax_job_id TEXT,  -- FK to fax_jobs.id when created
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    processed_at DATETIME
);

-- Email provider OAuth tokens (encrypted storage)
CREATE TABLE email_oauth_tokens (
    id TEXT PRIMARY KEY,
    provider TEXT NOT NULL,  -- 'gmail', 'outlook', 'generic'
    encrypted_access_token TEXT NOT NULL,
    encrypted_refresh_token TEXT,
    expires_at DATETIME,
    scopes TEXT,  -- comma-separated OAuth scopes
    email_address TEXT NOT NULL,  -- authenticated email
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Email configuration settings
CREATE TABLE email_config (
    key TEXT PRIMARY KEY,
    value TEXT,
    encrypted BOOLEAN DEFAULT 0,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. Email Provider Plugin Architecture
Building on existing plugin system in `api/app/plugins/`:
- **Base Email Provider Interface**: `api/app/plugins/base/email_provider.py`
- **Gmail Plugin**: `api/app/plugins/providers/gmail.py`
- **Outlook Plugin**: `api/app/plugins/providers/outlook.py`
- **Generic IMAP Plugin**: `api/app/plugins/providers/generic_imap.py`

Each provider implements:
- `authenticate()` - OAuth flow initiation
- `poll_messages()` - Check for new emails
- `send_email()` - Send status replies and inbound notifications
- `validate_config()` - Check OAuth tokens and settings

#### 3. Background Worker Process
Async task loop within existing FastAPI app:
- **IMAP Polling**: 60-second intervals (configurable)
- **Message Processing**: Parse subject/body for fax numbers
- **Attachment Handling**: Validate PDF/TXT, convert TXT→PDF, size limits
- **Fax Job Creation**: Call existing `/fax` endpoint with file path
- **Status Notifications**: Email replies to sender

#### 4. Traits Integration
Extend `config/provider_traits.json` with email-specific traits:
```json
"email_gateway": {
  "id": "email_gateway",
  "kind": "communication",
  "traits": {
    "supports_oauth": true,
    "supports_imap_idle": false,
    "attachment_size_limit_mb": 10,
    "supported_formats": ["pdf", "txt"],
    "requires_hipaa_mode": false,  // MVP: false, Phase 2: conditional
    "supports_inbound_email": true,
    "rate_limit_per_hour": 100
  }
}
```

## Environment Configuration

### Core Email Gateway Settings
```bash
# Feature Control
EMAIL_GATEWAY_ENABLED=false           # Feature flag - disabled by default
EMAIL_GATEWAY_POLL_INTERVAL=60        # Seconds between email checks
EMAIL_GATEWAY_MAX_EMAILS_PER_POLL=10  # Batch size limit

# OAuth Provider Configuration
EMAIL_OAUTH_PROVIDER=gmail             # gmail|outlook|generic
# Gmail OAuth (get from Google Cloud Console)
GMAIL_CLIENT_ID=your-gmail-client-id.googleusercontent.com
GMAIL_CLIENT_SECRET=your-gmail-client-secret
# Outlook OAuth (get from Azure App Registration)
OUTLOOK_CLIENT_ID=your-azure-app-id
OUTLOOK_CLIENT_SECRET=your-azure-app-secret

# Email Processing Rules
EMAIL_ALLOWED_SENDERS=                 # Comma-separated, wildcards OK (*@domain.com)
EMAIL_DEFAULT_COUNTRY_CODE=+1          # Applied to numbers without country code
EMAIL_MAX_ATTACHMENT_SIZE_MB=10        # Per-attachment limit
EMAIL_ATTACHMENT_TYPES=pdf,txt         # Allowed attachment types

# Response Configuration
EMAIL_STATUS_REPLIES_ENABLED=true      # Send status emails to sender
EMAIL_FROM_ADDRESS=noreply@company.com # From address for status emails
EMAIL_FROM_NAME=Fax Gateway            # Display name for outgoing emails

# Inbound Fax Distribution
EMAIL_INBOUND_ENABLED=true             # Forward received faxes to email
EMAIL_INBOUND_DISTRO=admin@company.com,fax@company.com  # Recipients

# Security & Rate Limiting
EMAIL_RATE_LIMIT_PER_HOUR=100          # Max emails processed per hour
EMAIL_RATE_LIMIT_PER_SENDER_HOUR=20    # Max emails per sender per hour
EMAIL_QUARANTINE_SUSPICIOUS=true       # Hold emails that fail validation

# Database Storage (MVP uses existing SQLite)
EMAIL_TOKEN_ENCRYPTION_KEY=            # 32-byte base64 key for OAuth token encryption

# HIPAA Mode Override (Phase 2)
HIPAA_MODE=false                       # When true, email gateway is disabled
EMAIL_GATEWAY_HIPAA_READY=false        # Phase 2: enables HIPAA-compliant features
```

### Integration with Existing Config
Extend `api/app/config.py` Settings class:
```python
class Settings(BaseModel):
    # ... existing settings ...

    # Email Gateway
    email_gateway_enabled: bool = Field(
        default_factory=lambda: os.getenv("EMAIL_GATEWAY_ENABLED", "false").lower() in {"1", "true", "yes"}
    )
    email_oauth_provider: str = Field(default_factory=lambda: os.getenv("EMAIL_OAUTH_PROVIDER", "gmail"))
    gmail_client_id: str = Field(default_factory=lambda: os.getenv("GMAIL_CLIENT_ID", ""))
    gmail_client_secret: str = Field(default_factory=lambda: os.getenv("GMAIL_CLIENT_SECRET", ""))
    outlook_client_id: str = Field(default_factory=lambda: os.getenv("OUTLOOK_CLIENT_ID", ""))
    outlook_client_secret: str = Field(default_factory=lambda: os.getenv("OUTLOOK_CLIENT_SECRET", ""))
    # ... additional email settings ...

    # HIPAA Integration
    hipaa_mode: bool = Field(default_factory=lambda: os.getenv("HIPAA_MODE", "false").lower() in {"1", "true", "yes"})
```

## API Endpoint Specifications

### Admin Endpoints (Protected by API Key + Scopes)

#### `GET /admin/email-gateway/status`
**Purpose**: Get current email gateway status and health
```json
{
  "enabled": true,
  "provider": "gmail",
  "oauth_status": {
    "authenticated": true,
    "email": "gateway@company.com",
    "expires_at": "2024-01-15T10:30:00Z",
    "scopes": ["https://www.googleapis.com/auth/gmail.readonly"]
  },
  "last_poll": "2024-01-15T09:45:00Z",
  "poll_interval_seconds": 60,
  "stats": {
    "emails_processed_today": 15,
    "fax_jobs_created_today": 12,
    "last_error": null
  },
  "config": {
    "allowed_senders": ["*@company.com"],
    "default_country": "+1",
    "inbound_distro": ["admin@company.com"]
  }
}
```

#### `POST /admin/email-gateway/oauth/initiate`
**Purpose**: Start OAuth flow for email provider
```json
// Request
{
  "provider": "gmail",  // or "outlook"
  "redirect_uri": "http://localhost:8080/admin/email-gateway/oauth/callback"
}

// Response
{
  "auth_url": "https://accounts.google.com/oauth2/auth?client_id=...",
  "state": "random-state-token"
}
```

#### `POST /admin/email-gateway/oauth/callback`
**Purpose**: Complete OAuth flow with authorization code
```json
// Request
{
  "code": "authorization-code-from-provider",
  "state": "random-state-token"
}

// Response
{
  "success": true,
  "email": "gateway@company.com",
  "scopes": ["gmail.readonly", "gmail.send"]
}
```

#### `POST /admin/email-gateway/config`
**Purpose**: Update email gateway configuration
```json
// Request
{
  "enabled": true,
  "provider": "gmail",
  "allowed_senders": "user@company.com, *@trusted.com",
  "default_country": "+1",
  "inbound_distro": "admin@company.com, fax-team@company.com",
  "poll_interval_seconds": 60
}

// Response
{
  "success": true,
  "config_updated": true,
  "restart_required": false
}
```

#### `POST /admin/email-gateway/test`
**Purpose**: Test email gateway connection and configuration
```json
// Request
{
  "test_type": "connection"  // or "send_test_email"
}

// Response
{
  "success": true,
  "test_type": "connection",
  "results": {
    "oauth_valid": true,
    "imap_connection": true,
    "smtp_connection": true,
    "last_message_count": 5
  }
}
```

#### `GET /admin/email-gateway/events`
**Purpose**: Get recent email processing events for debugging
```json
// Query params: ?limit=50&status=failed
{
  "events": [
    {
      "id": "evt_123",
      "message_id": "<CAB123@gmail.com>",
      "from_address": "user@company.com",
      "subject": "Fax to +15551234567",
      "processing_status": "completed",
      "fax_job_id": "fax_456",
      "created_at": "2024-01-15T09:30:00Z",
      "processed_at": "2024-01-15T09:30:15Z"
    }
  ],
  "total": 25,
  "has_more": true
}
```

### Error Responses
Following existing Faxbot error patterns:
- **400**: Invalid configuration, malformed request
- **401**: Invalid API key or insufficient scopes
- **403**: Email gateway disabled or HIPAA mode restriction
- **409**: OAuth flow already in progress
- **422**: Provider not supported or OAuth setup incomplete
- **429**: Rate limit exceeded
- **500**: Internal server error (OAuth provider down, etc.)

## Admin Console Integration

### New UI Component: `EmailGateway.tsx`
Location: `api/admin_ui/src/components/EmailGateway.tsx`

Following existing UI patterns from `Settings.tsx` and `Diagnostics.tsx`:

#### Screen Layout
```tsx
// Tools tab -> Email Gateway (traits-gated)
<ResponsiveCard title="Email-to-Fax Gateway"
                subtitle="Send faxes by email, receive faxes in your inbox">

  // Feature Status Section
  <ResponsiveSettingSection title="Gateway Status">
    <StatusChip status={emailEnabled ? 'enabled' : 'disabled'} />
    <Typography variant="body2">
      {emailEnabled ? 'Processing emails every 60 seconds' : 'Feature disabled'}
    </Typography>
    <Button onClick={toggleFeature} variant={emailEnabled ? 'outlined' : 'contained'}>
      {emailEnabled ? 'Disable' : 'Enable'}
    </Button>
  </ResponsiveSettingSection>

  // OAuth Provider Section
  <ResponsiveSettingSection title="Email Provider"
                           subtitle="Configure OAuth authentication">
    <ResponsiveSelect
      label="Provider"
      value={provider}
      options={[{value: 'gmail', label: 'Gmail/Workspace'},
                {value: 'outlook', label: 'Outlook/Microsoft 365'}]}
    />

    <Card sx={{mt: 2, p: 2, bgcolor: provider === 'gmail' ? 'success.light' : 'warning.light'}}>
      <Typography variant="h6">OAuth Status</Typography>
      <Typography variant="body2">
        {oauthStatus.authenticated ?
          `✓ Connected as ${oauthStatus.email}` :
          `✗ Not connected`}
      </Typography>
      {!oauthStatus.authenticated && (
        <Button variant="contained" onClick={initiateOAuth} sx={{mt: 1}}>
          Connect to {provider === 'gmail' ? 'Gmail' : 'Outlook'}
        </Button>
      )}
    </Card>
  </ResponsiveSettingSection>

  // Configuration Section
  <ResponsiveSettingSection title="Email Processing"
                           subtitle="Configure sender restrictions and parsing">
    <ResponsiveTextField
      label="Allowed Senders"
      value={allowedSenders}
      placeholder="user@company.com, *@trusted-domain.com"
      helperText="Comma-separated. Use * for wildcards. Leave blank to allow all."
    />

    <ResponsiveTextField
      label="Default Country Code"
      value={defaultCountry}
      placeholder="+1"
      helperText="Applied to numbers without country code"
    />

    <ResponsiveTextField
      label="Inbound Distribution"
      value={inboundDistro}
      placeholder="admin@company.com, fax-team@company.com"
      helperText="Email addresses to receive inbound faxes"
    />
  </ResponsiveSettingSection>

  // Help and Documentation
  <ResponsiveSettingSection title="Help & Testing">
    <Alert severity="info" sx={{mb: 2}}>
      <Typography variant="body2">
        Send test email to connected address with subject: "Fax to +15551234567"
      </Typography>
    </Alert>

    <Stack direction="row" spacing={2}>
      <Button variant="outlined" onClick={() => window.open(`${docsBase}/tools/email-gateway`)}>
        📝 Setup Guide
      </Button>
      <Button variant="outlined" onClick={() => window.open(`${docsBase}/tools/email-gateway/oauth`)}>
        🔐 OAuth Setup
      </Button>
      <Button variant="outlined" onClick={runConnectionTest}>
        🧪 Test Connection
      </Button>
    </Stack>
  </ResponsiveSettingSection>

  // HIPAA Warning (conditional)
  {hipaaMode && (
    <Alert severity="warning" sx={{mt: 2}}>
      <Typography variant="body2">
        <strong>HIPAA Notice:</strong> Email-to-fax is disabled in HIPAA mode.
        This feature will be available in Phase 2 with enhanced security controls.
      </Typography>
    </Alert>
  )}
</ResponsiveCard>
```

#### Integration Points
- **App.tsx**: Add new tab "Email Gateway" to Tools section
- **Traits gating**: Show tab only if `providerHasTrait('outbound', 'supports_email_gateway')`
- **API calls**: Use existing `AdminAPIClient` pattern
- **Help links**: Build from `docsBase` prop
- **Responsive**: Uses existing `ResponsiveFormFields` and `ResponsiveSettingItem` components

## Acceptance Criteria (alpha)
- Process an email with a single PDF attachment into a queued fax job.
- Reject unsupported types and oversize attachments with a status reply.
- Inbound fax triggers an email with the PDF attached to distro.
- No plaintext passwords; tokens file stored locally; logs redact addresses.

## Implementation Checklist (Phase 1 MVP)

### Backend Infrastructure

#### Database Schema & Models
- [ ] **Create migration script**: `api/app/migrations/add_email_gateway_tables.py`
  - [ ] `email_events` table with Message-ID deduplication
  - [ ] `email_oauth_tokens` table with encrypted token storage
  - [ ] `email_config` table for persistent settings
- [ ] **Extend SQLAlchemy models**: `api/app/db.py`
  - [ ] `EmailEvent` class with relationship to `FaxJob`
  - [ ] `EmailOAuthToken` class with encryption helpers
  - [ ] `EmailConfig` class for settings persistence

#### Configuration System
- [ ] **Extend Settings class**: `api/app/config.py` (lines 41-150)
  - [ ] Add all email gateway environment variables
  - [ ] Add HIPAA mode integration
  - [ ] Add provider-specific OAuth settings
- [ ] **Update provider traits**: `config/provider_traits.json`
  - [ ] Add `email_gateway` provider with traits
  - [ ] Define scopes and capabilities

#### Email Provider Plugins
- [ ] **Create plugin base class**: `api/app/plugins/base/email_provider.py`
  ```python
  class EmailProvider(ABC):
      @abstractmethod
      def authenticate(self, oauth_config: dict) -> AuthResult: pass
      @abstractmethod
      def poll_messages(self, since: datetime) -> List[EmailMessage]: pass
      @abstractmethod
      def send_email(self, to: str, subject: str, body: str, attachments: List) -> bool: pass
  ```
- [ ] **Gmail provider**: `api/app/plugins/providers/gmail.py`
  - [ ] OAuth 2.0 flow with Google APIs
  - [ ] IMAP polling with Gmail API or IMAP
  - [ ] SMTP sending via Gmail API
- [ ] **Outlook provider**: `api/app/plugins/providers/outlook.py`
  - [ ] OAuth 2.0 flow with Microsoft Graph
  - [ ] Exchange Online API integration
  - [ ] SMTP sending via Microsoft Graph
- [ ] **Plugin manager**: `api/app/plugins/email_manager.py`
  - [ ] Dynamic provider loading
  - [ ] Configuration validation
  - [ ] Health checking

#### Core Email Processing
- [ ] **Email processing service**: `api/app/services/email_processor.py`
  - [ ] Background task loop (60-second intervals)
  - [ ] Message deduplication by Message-ID
  - [ ] Fax number parsing with multiple formats
  - [ ] Attachment validation and conversion
  - [ ] Integration with existing `/fax` endpoint
- [ ] **OAuth token management**: `api/app/services/oauth_manager.py`
  - [ ] Token encryption/decryption with `cryptography` library
  - [ ] Automatic refresh handling
  - [ ] Provider-agnostic token storage
- [ ] **Email utilities**: `api/app/utils/email_utils.py`
  - [ ] E.164 phone number parsing and validation
  - [ ] Email address validation and sender filtering
  - [ ] Attachment type detection and size validation
  - [ ] TXT to PDF conversion using existing conversion pipeline

#### API Endpoints
- [ ] **Admin controller**: `api/app/routers/email_gateway.py` (new file)
  - [ ] `GET /admin/email-gateway/status` - Gateway status and health
  - [ ] `POST /admin/email-gateway/oauth/initiate` - Start OAuth flow
  - [ ] `POST /admin/email-gateway/oauth/callback` - Complete OAuth
  - [ ] `POST /admin/email-gateway/config` - Update configuration
  - [ ] `POST /admin/email-gateway/test` - Test connections
  - [ ] `GET /admin/email-gateway/events` - Processing history
- [ ] **Integration with main.py**: Add router to FastAPI app
  - [ ] Mount email gateway router with `/admin` prefix
  - [ ] Add HIPAA mode middleware protection
  - [ ] Integrate with existing rate limiting system

#### Security & Middleware
- [ ] **Extend traits middleware**: `api/app/middleware/traits.py`
  - [ ] Add `email_gateway` trait checking
  - [ ] Scope validation for email admin endpoints
- [ ] **HIPAA mode enforcement**: `api/app/main.py` (around line 186)
  - [ ] Add email gateway path blocking when HIPAA mode enabled
  - [ ] Return appropriate error messages

### Frontend (Admin Console)

#### UI Components
- [ ] **Main component**: `api/admin_ui/src/components/EmailGateway.tsx`
  - [ ] Follow existing component patterns from `Settings.tsx`
  - [ ] Use `ResponsiveFormFields` and `ResponsiveSettingItem`
  - [ ] Implement OAuth flow UI with popup/redirect handling
  - [ ] Configuration forms with validation
  - [ ] Status dashboard with real-time updates
- [ ] **Integration with App shell**: `api/admin_ui/src/App.tsx`
  - [ ] Add "Email Gateway" tab to Tools section
  - [ ] Add traits-based gating for tab visibility
  - [ ] Wire up routing and navigation
- [ ] **API client integration**: `api/admin_ui/src/api/client.ts`
  - [ ] Add email gateway API methods
  - [ ] Error handling for OAuth flows
  - [ ] File upload handling for test emails
- [ ] **Type definitions**: `api/admin_ui/src/api/types.ts`
  - [ ] `EmailGatewayStatus` interface
  - [ ] `EmailOAuthConfig` interface
  - [ ] `EmailEvent` interface

#### Responsive Design
- [ ] **Mobile optimization**: Ensure all email gateway UI works on mobile
- [ ] **Dark/light theme support**: Test email gateway components in both themes
- [ ] **Accessibility**: Add proper ARIA labels and keyboard navigation

### Integration & Testing

#### Database Integration
- [ ] **Migration testing**: Verify schema changes work with existing data
- [ ] **Performance testing**: Ensure email polling doesn't impact API performance
- [ ] **Backup compatibility**: Verify email tables are included in backup scripts

#### Provider Integration Testing
- [ ] **Gmail OAuth flow**: End-to-end testing with real Google OAuth
- [ ] **Outlook OAuth flow**: End-to-end testing with Microsoft Azure
- [ ] **Email processing**: Test with various email formats and attachments
- [ ] **Error handling**: Test OAuth token expiration and renewal

#### Security Testing
- [ ] **Token encryption**: Verify OAuth tokens are encrypted at rest
- [ ] **Rate limiting**: Test email processing rate limits
- [ ] **Input validation**: Test malicious email attachments and content
- [ ] **HIPAA mode**: Verify feature is completely disabled in HIPAA mode

### Documentation & Help
- [ ] **User documentation**: Create email gateway setup guide
- [ ] **OAuth setup guides**: Provider-specific instructions for Gmail/Outlook
- [ ] **Troubleshooting guide**: Common issues and solutions
- [ ] **API documentation**: Update OpenAPI spec with new endpoints

### Deployment & Operations
- [ ] **Environment variables**: Document all new config options
- [ ] **Docker integration**: Ensure email gateway works in containerized environment
- [ ] **Health checks**: Add email gateway status to system health endpoint
- [ ] **Monitoring**: Add metrics and alerts for email processing failures

### Acceptance Testing
- [ ] **End-to-end flow**: Send email with PDF attachment, verify fax created
- [ ] **Status notifications**: Verify sender receives success/failure emails
- [ ] **Inbound distribution**: Verify received faxes are emailed to distribution list
- [ ] **Error handling**: Test all error scenarios return appropriate messages
- [ ] **Rate limiting**: Verify rate limits prevent abuse
- [ ] **OAuth renewal**: Test automatic token refresh
- [ ] **Multi-provider**: Test switching between Gmail and Outlook
- [ ] **HIPAA compliance**: Verify feature completely disabled in HIPAA mode

## Security Controls & Risk Mitigation

### Authentication & Authorization
1. **OAuth 2.0 Only**: No password-based email access
   - Gmail: Use Google Cloud Console OAuth 2.0 credentials
   - Outlook: Use Azure App Registration with appropriate scopes
   - Token storage: AES-256 encrypted in database with key rotation
   - Refresh token handling: Automatic renewal with fallback to re-auth

2. **API Access Control**
   - Email gateway endpoints require API key with `email:admin` scope
   - Rate limiting: 100 requests/hour per API key for email endpoints
   - Audit logging: All configuration changes and OAuth events

3. **Email Processing Security**
   - Sender validation: Configurable allowlist with wildcard support
   - Attachment scanning: File type, size, and basic malware detection
   - Content filtering: No executable attachments, no embedded links
   - Quarantine system: Hold suspicious emails for manual review

### Data Protection (MVP)
1. **Minimal Data Storage**
   - Email metadata only (Message-ID, sender, timestamp)
   - No email body content stored permanently
   - OAuth tokens encrypted at rest with application-level encryption
   - Automatic cleanup of temporary files after processing

2. **Logging & Monitoring**
   - No email content in logs (only metadata and processing status)
   - Failed processing attempts logged with sanitized error messages
   - Rate limiting events logged for security monitoring
   - OAuth token refresh/failure events tracked

### Error Handling & Resilience
1. **Email Processing Failures**
   - Malformed attachments: Send error reply with guidance
   - Missing fax number: Send parsing help and examples
   - Attachment too large: Send size limit notification
   - Provider rate limits: Exponential backoff with circuit breaker

2. **OAuth Token Management**
   - Expired tokens: Automatic refresh attempt, then re-auth request
   - Invalid scopes: Clear error message with required permissions
   - Provider downtime: Queue emails for retry (up to 24 hours)

3. **System Integration**
   - Fax backend failures: Store email for retry, notify sender
   - Database connection issues: Graceful degradation, skip processing
   - Storage full: Alert admin, pause email processing

### HIPAA Mode Restrictions (MVP)
```python
# In api/app/main.py middleware
if settings.hipaa_mode and request.url.path.startswith("/admin/email-gateway"):
    raise HTTPException(
        status_code=403,
        detail="Email gateway disabled in HIPAA mode. Feature available in Phase 2 with enhanced security."
    )
```

### Rate Limiting Implementation
```python
# Email-specific rate limiting
EMAIL_RATE_LIMITS = {
    "emails_per_hour": 100,
    "emails_per_sender_hour": 20,
    "oauth_attempts_per_hour": 10,
    "config_changes_per_hour": 20
}

# Integration with existing rate limiter in main.py
def _enforce_email_rate_limit(info: Optional[dict], limit_type: str):
    limit = EMAIL_RATE_LIMITS.get(limit_type, 60)
    _enforce_rate_limit(info, f"email:{limit_type}", limit)
```
