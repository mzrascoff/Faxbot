import { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Alert,
  Paper,
  CircularProgress,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Link,
  Stack,
  useTheme,
  useMediaQuery,
  Fade,
  IconButton,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  LinearProgress,
} from '@mui/material';
import {
  Download as DownloadIcon,
  ContentCopy as ContentCopyIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  RestartAlt as RestartIcon,
  ExpandMore as ExpandMoreIcon,
  Help as HelpIcon,
  Send as SendIcon,
  HealthAndSafety as HealthIcon,
  BugReport as DiagnosticIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import AdminAPIClient from '../api/client';
import type { DiagnosticsResult } from '../api/types';
import { useTraits } from '../hooks/useTraits';
import { ResponsiveFormSection } from './common/ResponsiveFormFields';

interface DiagnosticsProps {
  client: AdminAPIClient;
  onNavigate?: (index: number) => void;
  docsBase?: string;
}

function Diagnostics({ client, onNavigate, docsBase }: DiagnosticsProps) {
  const [diagnostics, setDiagnostics] = useState<DiagnosticsResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [helpOpen, setHelpOpen] = useState(false);
  const [helpTitle, setHelpTitle] = useState<string>('');
  const [helpKey, setHelpKey] = useState<string>('');
  const [testSending, setTestSending] = useState(false);
  const [testSendingTxt, setTestSendingTxt] = useState(false);
  const [testSendingImg, setTestSendingImg] = useState(false);
  const [testJobId, setTestJobId] = useState<string | null>(null);
  const [testStatus, setTestStatus] = useState<string | null>(null);
  const [expandedSections, setExpandedSections] = useState<string[]>(['summary']);
  const [anchors, setAnchors] = useState<Record<string, string>>({});

  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isSmallMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { active, registry } = useTraits();
  const thirdParty: Record<string, string> = {
    'sinch-build-access-keys-location': 'https://dashboard.sinch.com/settings/access-keys',
    'sinch-oauth-client-credentials-flow': 'https://developers.sinch.com/docs/fax/api-reference/authentication/oauth/',
    'sinch-regional-base-url': 'https://developers.sinch.com/docs/fax/api-reference/#global-url',
    'sinch-inbound-webhook-url': 'https://developers.sinch.com/docs/fax/api-reference/fax/tag/Notifications/#incoming-fax-event-webhook',
    'sinch-inbound-basic-auth': 'https://developers.sinch.com/docs/fax/api-reference/fax/tag/Notifications/#incoming-fax-event-webhook',
    'sinch-register-webhook-limitations': 'https://developers.sinch.com/docs/fax/api-reference/fax/tag/Services/#create-a-service',
    'sinch-troubleshoot-auth-fail': 'https://developers.sinch.com/docs/fax/api-reference/fax/tag/Error-Messages/#http-error-codes',
    'sinch-troubleshoot-inbound-fail': 'https://developers.sinch.com/docs/fax/api-reference/fax/tag/Services/#create-a-service',
    'enforce-https-phi': 'https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164/subpart-C/section-164.312',
    'require-api-key-production': 'https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html#https',
    'audit-logging-hipaa': 'https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164/subpart-C/section-164.312',
    'phaxio-webhook-hmac': 'https://www.phaxio.com/docs/security/callbacks',
    'phaxio-status-callback-url': 'https://www.phaxio.com/docs/api/v1/send/sendCallback',
  };

  const hrefFor = (topic: string): string | undefined => (anchors[topic] || thirdParty[topic]);

  // Load anchor mapping from docs site for precise deep links
  useEffect(() => {
    const loadAnchors = async () => {
      try {
        const base = docsBase || 'https://dmontgomery40.github.io/Faxbot';
        const topics: string[] = [ 'security', 'diagnostics', 'inbound', 'storage', 'plugins', 'mcp' ];
        const provs = [active?.outbound, active?.inbound].filter(Boolean) as string[];
        for (const p of provs) { if (!topics.includes(p)) topics.push(p); }
        topics.push('all');
        for (const t of Array.from(new Set(topics))) {
          try {
            const res = await fetch(`${base}/anchors/${t}.json`, { cache: 'no-store' });
            if (res.ok) {
              const js = await res.json();
              setAnchors(prev => ({ ...prev, ...js }));
            }
          } catch { /* ignore per-scope failure */ }
        }
      } catch {
        /* ignore */
      }
    };
    loadAnchors();
  }, [docsBase, active?.outbound, active?.inbound]);

  const runDiagnostics = async () => {
    try {
      setError(null);
      setLoading(true);
      const data = await client.runDiagnostics();
      setDiagnostics(data);
      setExpandedSections(['summary', ...Object.keys(data.checks || {})]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to run diagnostics');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const downloadText = (filename: string, text: string) => {
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleSectionToggle = (section: string) => {
    setExpandedSections(prev => 
      prev.includes(section) 
        ? prev.filter(s => s !== section)
        : [...prev, section]
    );
  };

  const renderCheckValue = (value: any) => {
    if (typeof value === 'boolean') {
      return (
        <Chip
          icon={value ? <CheckCircleIcon /> : <ErrorIcon />}
          label={value ? 'Pass' : 'Fail'}
          color={value ? 'success' : 'error'}
          size="small"
          variant="outlined"
          sx={{ borderRadius: 1 }}
        />
      );
    }
    return <Typography variant="body2">{String(value)}</Typography>;
  };

  const anchorFor = (title: string) => {
    const t = title.toLowerCase();
    if (t.includes('phaxio')) return '#settings-phaxio';
    if (t.includes('sinch')) return '#settings-sinch';
    if (t.includes('sip')) return '#settings-sip';
    if (t.includes('storage')) return '#settings-storage';
    if (t.includes('security')) return '#settings-security';
    if (t.includes('inbound')) return '#settings-inbound';
    return '#settings-advanced';
  };

  const helpFor = (title: string, key: string, value: any): string | null => {
    const t = title.toLowerCase();
    if (t.includes('phaxio')) {
      if (key === 'api_key_set' && !value) return 'Set PHAXIO_API_KEY with your Phaxio console key.';
      if (key === 'api_secret_set' && !value) return 'Set PHAXIO_API_SECRET with your Phaxio console secret.';
      if (key === 'callback_url_set' && !value) return 'Set PHAXIO_STATUS_CALLBACK_URL so Phaxio can send status updates.';
      if (key === 'public_url_https' && !value) return 'PUBLIC_API_URL should be HTTPS for PHI; enable TLS.';
    }
    if (t.includes('sinch')) {
      if ((key === 'auth_present' || key === 'project_id_set') && !value) return 'Set SINCH_PROJECT_ID, SINCH_API_KEY, and SINCH_API_SECRET (Sinch Build → Access Keys).';
      if (key === 'api_key_set' && !value) return 'Set SINCH_API_KEY (Key ID) — used to mint OAuth 2.0 access tokens.';
      if (key === 'api_secret_set' && !value) return 'Set SINCH_API_SECRET — used with the key to mint OAuth 2.0 access tokens.';
      if ((key === 'auth' || key === 'auth_valid') && value === false) return 'If auth fails, set SINCH_BASE_URL for your region (e.g., https://us.fax.api.sinch.com/v3) and re-run. Outbound API uses OAuth 2.0 (Bearer).';
    }
    if (t.includes('sip')) {
      if (key === 'ami_password_not_default' && !value) return 'Change ASTERISK_AMI_PASSWORD from default to a secure value.';
      if (key === 'ami_reachable' && !value) return 'Verify AMI host/port, credentials, and network reachability.';
    }
    if (t.includes('storage')) {
      if (key === 'kms_enabled' && !value) return 'Set S3_KMS_KEY_ID to enable server-side encryption (KMS).';
      if (key === 'bucket_set' && !value) return 'Set S3_BUCKET to store inbound artifacts.';
    }
    if (t.includes('security')) {
      if (key === 'enforce_https' && !value) return 'Set ENFORCE_PUBLIC_HTTPS=true for HIPAA deployments.';
      if (key === 'audit_logging' && !value) return 'Enable AUDIT_LOG_ENABLED=true to record security events.';
      if (key === 'rate_limiting' && !value) return 'Set MAX_REQUESTS_PER_MINUTE to mitigate abuse.';
      if (key === 'pdf_token_ttl' && !value) return 'Set a reasonable PDF_TOKEN_TTL_MINUTES for Phaxio token links.';
    }
    if (t.includes('system')) {
      if (key === 'ghostscript' && !value) return 'Install ghostscript in production to support PDF→TIFF.';
      if (key === 'fax_data_writable' && !value) return 'Ensure FAX_DATA_DIR is writable (default /faxdata).';
      if (key === 'database_connected' && !value) return 'Check DATABASE_URL and ensure DB file or Postgres is reachable.';
    }
    if (t.includes('inbound')) {
      if (key === 'enabled' && !value) return 'Enable inbound to receive faxes.';
    }
    return 'See linked docs for configuration details.';
  };

  const getHelpDocs = (title: string, key: string) => {
    const t = title.toLowerCase();
    const docs: { text: string; href?: string }[] = [];
    
    if (t.includes('system')) {
      if (key === 'ghostscript') {
        docs.push({ text: 'Ghostscript is required for PDF to TIFF conversion (SIP/Asterisk backend).' });
        docs.push({ text: 'Ghostscript Documentation', href: 'https://ghostscript.readthedocs.io/' });
        docs.push({ text: 'Install via: apt-get install ghostscript (Linux) or brew install ghostscript (Mac)' });
      }
      else if (key === 'fax_data_dir' || key === 'fax_data_writable') {
        docs.push({ text: 'FAX_DATA_DIR stores temporary files and fax artifacts.' });
        docs.push({ text: 'Default: /faxdata in container, ./faxdata locally' });
        docs.push({ text: 'Must be writable by the application process.' });
        docs.push({ text: 'Deployment Guide', href: `${docsBase || 'https://dmontgomery40.github.io/Faxbot'}/deployment/` });
      }
      else if (key === 'database_connected') {
        docs.push({ text: 'Database stores job records and API keys.' });
        docs.push({ text: 'Default: SQLite at ./faxbot.db' });
        docs.push({ text: 'Production: Use PostgreSQL with DATABASE_URL' });
        docs.push({ text: 'Database Setup', href: `${docsBase || 'https://dmontgomery40.github.io/Faxbot'}/deployment/#database-configuration` });
      }
    }
    
    if (t.includes('phaxio')) {
      docs.push({ text: 'Phaxio Setup Guide', href: `${docsBase || 'https://dmontgomery40.github.io/Faxbot'}/backends/phaxio-setup.html` });
      docs.push({ text: 'Phaxio Console', href: 'https://console.phaxio.com' });
      const add = (topic: string, text: string) => { const href = anchors[topic] || thirdParty[topic]; if (href) docs.push({ text, href }); };
      add('phaxio-webhook-hmac', 'Verify Phaxio inbound HMAC signatures');
      add('phaxio-status-callback-url', 'Set status callback URL (HTTPS required)');
    }
    
    if (t.includes('sip')) {
      docs.push({ text: 'SIP/Asterisk Setup', href: `${docsBase || 'https://dmontgomery40.github.io/Faxbot'}/backends/sip-setup.html` });
      if (key === 'ami_password_not_default') {
        docs.push({ text: 'Change AMI password in both Asterisk manager.conf and ASTERISK_AMI_PASSWORD env var.' });
      }
    }
    
    if (t.includes('security')) {
      docs.push({ text: 'Security Guide', href: `${docsBase || 'https://dmontgomery40.github.io/Faxbot'}/security/` });
      const addSec = (topic: string, text: string) => { const href = anchors[topic] || thirdParty[topic]; if (href) docs.push({ text, href }); };
      addSec('enforce-https-phi', 'Enforce HTTPS for PHI (ENFORCE_PUBLIC_HTTPS)');
      addSec('require-api-key-production', 'Require API keys (REQUIRE_API_KEY)');
      addSec('audit-logging-hipaa', 'Enable audit logging');
    }

    if (t.includes('sinch')) {
      docs.push({ text: 'Faxbot: Sinch Setup', href: `${docsBase || 'https://dmontgomery40.github.io/Faxbot'}/backends/sinch-setup.html` });
      docs.push({ text: 'Sinch Fax API', href: 'https://developers.sinch.com/docs/fax/api-reference/' });
      docs.push({ text: 'OAuth 2.0 for Fax API', href: 'https://developers.sinch.com/docs/fax/api-reference/authentication/oauth/' });
      docs.push({ text: 'Sinch Customer Dashboard (Access Keys – Build)', href: 'https://dashboard.sinch.com/settings/access-keys' });
      const add = (topic: string, text: string) => { const href = anchors[topic] || thirdParty[topic]; if (href) docs.push({ text, href }); };
      add('sinch-build-access-keys-location', 'Where to find Sinch Fax access keys (Build)');
      add('sinch-oauth-client-credentials-flow', 'How Faxbot mints OAuth2 access tokens');
      add('sinch-regional-base-url', 'Regional base URL (SINCH_BASE_URL)');
      add('sinch-inbound-webhook-url', 'Set the inbound webhook URL');
      add('sinch-inbound-basic-auth', 'Enforce Basic auth for inbound webhooks');
      add('sinch-troubleshoot-auth-fail', 'Troubleshooting auth failures in Diagnostics');
      add('sinch-troubleshoot-inbound-fail', 'Troubleshooting inbound failures');
      add('sinch-register-webhook-limitations', 'Limitations of auto “Register with Sinch”');
    }
    
    return docs;
  };

  const renderCheckSection = (title: string, checks: Record<string, any>) => {
    const sectionKey = title.toLowerCase().replace(/\s+/g, '_');
    const isExpanded = expandedSections.includes(sectionKey);

    // Treat provider traits as informational, not pass/fail
    const neutralKeys = new Set(['requires_ami', 'needs_storage', 'inbound_verification', 'backend', 'enabled']);

    const entries = Object.entries(checks || {});
    const failCount = entries.filter(([k, v]) => !neutralKeys.has(k) && v === false).length;
    const totalCount = entries.filter(([k]) => !neutralKeys.has(k)).length;
    const hasIssues = failCount > 0;

    return (
      <Accordion 
        key={sectionKey}
        expanded={isExpanded}
        onChange={() => handleSectionToggle(sectionKey)}
        sx={{ 
          borderRadius: 2,
          mb: 2,
          '&:before': { display: 'none' },
          border: '1px solid',
          borderColor: 'divider',
        }}
      >
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          sx={{
            '& .MuiAccordionSummary-content': {
              alignItems: 'center',
              gap: 2,
            }
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
            {hasIssues ? <ErrorIcon color="error" /> : <CheckCircleIcon color="success" />}
            <Typography variant="h6" fontWeight={600}>
              {title}
            </Typography>
            <Chip
              label={`${Math.max(totalCount - failCount, 0)}/${Math.max(totalCount, 0)} Pass`}
              color={hasIssues ? 'error' : 'success'}
              size="small"
              variant="outlined"
              sx={{ borderRadius: 1, ml: 'auto' }}
            />
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Stack spacing={2}>
            {entries.map(([key, value]) => {
              const help = helpFor(title, key, value);
              const displayKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

              const isNeutral = neutralKeys.has(key);

              return (
                <Paper
                  key={key}
                  elevation={0}
                  sx={{
                    p: 2,
                    border: '1px solid',
                    borderColor: !isNeutral && value === false ? 'error.main' : 'divider',
                    borderRadius: 2,
                    backgroundColor: theme.palette.mode === 'dark' 
                      ? 'rgba(255, 255, 255, 0.02)' 
                      : 'rgba(0, 0, 0, 0.02)',
                  }}
                >
                  <Box sx={{ 
                    display: 'flex', 
                    alignItems: 'flex-start',
                    flexDirection: isMobile ? 'column' : 'row',
                    gap: isMobile ? 1 : 2
                  }}>
                    <Box sx={{ flex: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <Typography variant="subtitle2" fontWeight={600}>
                          {displayKey}
                        </Typography>
                        {isNeutral ? (
                          <Chip
                            icon={<InfoIcon />}
                            label={String(value)}
                            color="info"
                            size="small"
                            variant="outlined"
                            sx={{ borderRadius: 1 }}
                          />
                        ) : (
                          renderCheckValue(value)
                        )}
                      </Box>
                      {help && (
                        <Typography variant="caption" color="text.secondary">
                          {help}
                        </Typography>
                      )}
                    </Box>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      {onNavigate && (
                        <Button
                          size="small"
                          variant="outlined"
                          onClick={() => {
                            const anchor = anchorFor(title);
                            onNavigate('settings/settings');
                            setTimeout(() => {
                              const el = document.querySelector(anchor);
                              el?.scrollIntoView({ behavior: 'smooth' });
                            }, 200);
                          }}
                          sx={{ borderRadius: 1 }}
                        >
                          Go to Settings
                        </Button>
                      )}
                      <Tooltip title="Get help">
                        <IconButton
                          size="small"
                          onClick={() => {
                            setHelpTitle(title);
                            setHelpKey(key);
                            setHelpOpen(true);
                          }}
                        >
                          <HelpIcon />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </Box>
                </Paper>
              );
            })}
          </Stack>
        </AccordionDetails>
      </Accordion>
    );
  };

  const getSuggestions = (diagnostics: DiagnosticsResult) => {
    const suggestions: Array<{ type: 'error' | 'warning' | 'info'; text: string }> = [];
    
    diagnostics.summary.critical_issues.forEach(issue => {
      suggestions.push({ type: 'error', text: issue });
    });
    
    diagnostics.summary.warnings.forEach(warning => {
      suggestions.push({ type: 'warning', text: warning });
    });
    
    const { checks } = diagnostics;
    
    if (active?.outbound === 'phaxio') {
      const phaxio = checks.phaxio || {};
      if (!phaxio.api_key_set) suggestions.push({ type: 'error', text: 'Set PHAXIO_API_KEY in .env' });
      if (!phaxio.api_secret_set) suggestions.push({ type: 'error', text: 'Set PHAXIO_API_SECRET in .env' });
      if (!phaxio.callback_url_set) suggestions.push({ type: 'warning', text: 'Set PHAXIO_STATUS_CALLBACK_URL (or PHAXIO_CALLBACK_URL)' });
      if (phaxio.public_url_https === false) suggestions.push({ type: 'warning', text: 'Use HTTPS for PUBLIC_API_URL' });
    }
    
    if (active?.outbound === 'sip') {
      const sip = checks.sip || {};
      if (sip.ami_password_not_default === false) suggestions.push({ type: 'error', text: 'Change ASTERISK_AMI_PASSWORD from default "changeme"' });
      if (sip.ami_reachable === false) suggestions.push({ type: 'error', text: 'Verify Asterisk AMI host/port/credentials and network reachability' });
    }
    
    const system = checks.system || {};
    if (system.ghostscript === false) suggestions.push({ type: 'warning', text: 'Install Ghostscript (gs) for PDF→TIFF conversion' });
    if (system.fax_data_writable === false) suggestions.push({ type: 'error', text: 'Ensure FAX_DATA_DIR exists and is writable' });
    if (system.database_connected === false) suggestions.push({ type: 'error', text: 'Fix DATABASE_URL connectivity' });
    
    return suggestions;
  };

  const getSuggestionIcon = (type: string) => {
    switch (type) {
      case 'error': return <ErrorIcon color="error" />;
      case 'warning': return <WarningIcon color="warning" />;
      default: return <InfoIcon color="info" />;
    }
  };

  const runSendTestFax = async () => {
    try {
      setError(null);
      setTestSending(true);
      setTestJobId(null);
      setTestStatus(null);
      const blob = new Blob(["Faxbot test"], { type: 'text/plain' });
      const file = new File([blob], 'test.txt', { type: 'text/plain' });
      const result = await client.sendFax('+15555550123', file);
      setTestJobId(result.id);
      setTestStatus(result.status);
      
      let attempts = 0;
      const poll = async () => {
        if (!result.id || attempts++ > 10) return;
        try {
          const job = await client.getJob(result.id);
          setTestStatus(job.status);
          if (['SUCCESS','FAILED','failed','SUCCESSFUL','COMPLETED'].includes(String(job.status))) return;
          try {
            const logs = await client.getLogs({ q: result.id, limit: 5 });
            if (logs.items && logs.items.length > 0) {
              // Could display logs inline in future
            }
          } catch {}
        } catch {}
        setTimeout(poll, 2000);
      };
      poll();
    } catch (e: any) {
      setError(e?.message || 'Test fax failed to start');
    } finally {
      setTestSending(false);
    }
  };

  // Send Test TXT (simple text → backend converts to PDF)
  const runSendTestTxtFax = async () => {
    try {
      setError(null);
      setTestSendingTxt(true);
      setTestJobId(null);
      setTestStatus(null);
      const blob = new Blob(["Faxbot test TXT\nHello from Admin Console"], { type: 'text/plain' });
      const file = new File([blob], 'faxbot_test.txt', { type: 'text/plain' });
      const result = await client.sendFax('+15555550123', file);
      setTestJobId(result.id);
      setTestStatus(result.status);
      let attempts = 0;
      const poll = async () => {
        if (!result.id || attempts++ > 10) return;
        try {
          const job = await client.getJob(result.id);
          setTestStatus(job.status);
          if (['SUCCESS','FAILED','failed','SUCCESSFUL','COMPLETED'].includes(String(job.status))) return;
        } catch {}
        setTimeout(poll, 2000);
      };
      poll();
    } catch (e: any) {
      setError(e?.message || 'Test TXT fax failed to start');
    } finally {
      setTestSendingTxt(false);
    }
  };

  // Minimal single-page PDF generator (text) for "image" test path
  // Generates a valid PDF with Helvetica text — exercises PDF→TIFF when required
  const buildSimplePdf = (text: string): Uint8Array => {
    const enc = (s: string) => new TextEncoder().encode(s);
    const parts: Uint8Array[] = [];
    const push = (s: string) => parts.push(enc(s));
    push('%PDF-1.4\n');
    // 1: Catalog
    const o1 = enc('1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n');
    // 2: Pages
    const o2 = enc('2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n');
    // 5: Font
    const o5 = enc('5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n');
    // 4: Contents
    const streamContent = `BT /F1 24 Tf 72 720 Td (${text.replace(/\\/g,'\\\\').replace(/\(/g,'\\(').replace(/\)/g,'\\)')}) Tj ET`;
    const o4Stream = enc(streamContent);
    const o4 = enc(`4 0 obj\n<< /Length ${o4Stream.length} >>\nstream\n`);
    const o4end = enc('\nendstream\nendobj\n');
    // 3: Page
    const o3 = enc('3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n');
    // Assemble with xref
    let offset = 0;
    const add = (u: Uint8Array) => { parts.push(u); offset += u.length; };
    const offsets: number[] = [];
    add(enc('%PDF-1.4\n')); // already pushed via push, but we will rebuild consistently
    parts.length = 0; offset = 0; // reset to build deterministically
    const addAndRemember = (u: Uint8Array) => { offsets.push(offset); add(u); };
    addAndRemember(o1);
    addAndRemember(o2);
    addAndRemember(o3);
    addAndRemember(o4);
    add(o4Stream);
    add(o4end);
    addAndRemember(o5);
    const xrefStart = offset;
    const xref = `xref\n0 6\n0000000000 65535 f \n${offsets.map(o=>String(o).padStart(10,'0')+ ' 00000 n ').join('\n')}\ntrailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n${xrefStart}\n%%EOF`;
    add(enc(xref));
    // Combine
    const total = parts.reduce((n,u)=>n+u.length,0);
    const out = new Uint8Array(total);
    let p = 0; for (const u of parts) { out.set(u, p); p += u.length; }
    return out;
  };

  // Send Test Image (PDF) — generates a simple PDF with text to exercise raster path
  const runSendTestImageFax = async () => {
    try {
      setError(null);
      setTestSendingImg(true);
      setTestJobId(null);
      setTestStatus(null);
      const bytes = buildSimplePdf('Faxbot Test Image');
      // Create a standalone ArrayBuffer to avoid ArrayBufferLike/SharedArrayBuffer typing issues
      const ab = new ArrayBuffer(bytes.byteLength);
      new Uint8Array(ab).set(bytes);
      const blob = new Blob([ab], { type: 'application/pdf' });
      const file = new File([blob], 'faxbot_test_image.pdf', { type: 'application/pdf' });
      const result = await client.sendFax('+15555550123', file);
      setTestJobId(result.id);
      setTestStatus(result.status);
      let attempts = 0;
      const poll = async () => {
        if (!result.id || attempts++ > 10) return;
        try {
          const job = await client.getJob(result.id);
          setTestStatus(job.status);
          if (['SUCCESS','FAILED','failed','SUCCESSFUL','COMPLETED'].includes(String(job.status))) return;
        } catch {}
        setTimeout(poll, 2000);
      };
      poll();
    } catch (e: any) {
      setError(e?.message || 'Test image fax failed to start');
    } finally {
      setTestSendingImg(false);
    }
  };

  return (
    <>
      <Box>
        <Box 
          display="flex" 
          justifyContent="space-between" 
          alignItems={{ xs: 'flex-start', sm: 'center' }}
          flexDirection={{ xs: 'column', sm: 'row' }}
          gap={2}
          mb={3}
        >
          <Typography variant="h4" component="h1">
            System Diagnostics
          </Typography>
          <Box display="flex" gap={1}>
            <Button
              variant="contained"
              startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <DiagnosticIcon />}
              onClick={runDiagnostics}
              disabled={loading}
              size={isSmallMobile ? 'medium' : 'large'}
              sx={{ 
                borderRadius: 2,
                minHeight: isSmallMobile ? 40 : 42,
              }}
            >
              {loading ? 'Running...' : 'Run Diagnostics'}
            </Button>
            <Button
              variant="outlined"
              startIcon={<RestartIcon />}
              onClick={async () => { try { await client.restart(); } catch { /* ignore */ } }}
              size={isSmallMobile ? 'medium' : 'large'}
              sx={{ 
                borderRadius: 2,
                minHeight: isSmallMobile ? 40 : 42,
              }}
            >
              {isSmallMobile ? 'Restart' : 'Restart API'}
            </Button>
          </Box>
        </Box>

        {error && (
          <Fade in>
            <Alert 
              severity="error" 
              sx={{ mb: 3, borderRadius: 2 }}
              onClose={() => setError(null)}
            >
              {error}
            </Alert>
          </Fade>
        )}

        {!diagnostics && !loading && (
          <Fade in>
            <Paper sx={{ p: 4, textAlign: 'center', borderRadius: 2 }}>
              <HealthIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Run System Diagnostics
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Check your Faxbot configuration, backend connectivity, and system health
              </Typography>
              <Button
                variant="contained"
                startIcon={<DiagnosticIcon />}
                onClick={runDiagnostics}
                sx={{ borderRadius: 2 }}
              >
                Start Diagnostics
              </Button>
            </Paper>
          </Fade>
        )}

        {loading && (
          <Fade in>
            <Paper sx={{ p: 4, borderRadius: 2 }}>
              <Box sx={{ textAlign: 'center' }}>
                <CircularProgress sx={{ mb: 2 }} />
                <Typography variant="body1">
                  Running diagnostics...
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Checking system health, backend connectivity, and configuration
                </Typography>
              </Box>
              <LinearProgress sx={{ mt: 3 }} />
            </Paper>
          </Fade>
        )}

        {diagnostics && (
          <Fade in>
            <Box>
              {/* Built-in Tests */}
              <ResponsiveFormSection
                title="Built-in Tests"
                subtitle="Test your fax configuration with a sample transmission"
                icon={<SendIcon />}
              >
                <Stack spacing={2}>
                  <Box sx={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: 2,
                    flexWrap: 'wrap'
                  }}>
                    <Button 
                      variant="outlined" 
                      onClick={runSendTestTxtFax} 
                      disabled={testSendingTxt}
                      startIcon={testSendingTxt ? <CircularProgress size={16} /> : <SendIcon />}
                      sx={{ borderRadius: 2 }}
                    >
                      {testSendingTxt ? 'Sending…' : 'Send Test TXT'}
                    </Button>
                    <Button 
                      variant="outlined" 
                      onClick={runSendTestImageFax} 
                      disabled={testSendingImg}
                      startIcon={testSendingImg ? <CircularProgress size={16} /> : <SendIcon />}
                      sx={{ borderRadius: 2 }}
                    >
                      {testSendingImg ? 'Sending…' : 'Send Test Image'}
                    </Button>
                    <Button 
                      variant="outlined" 
                      onClick={runSendTestFax} 
                      disabled={testSending}
                      startIcon={testSending ? <CircularProgress size={16} /> : <SendIcon />}
                      sx={{ borderRadius: 2 }}
                    >
                      {testSending ? 'Sending…' : 'Send Test Fax'}
                    </Button>
                    {testJobId && (
                      <Chip
                        icon={<AssessmentIcon />}
                        label={`Job: ${testJobId.slice(0, 8)}... • Status: ${testStatus || 'queued'}`}
                        variant="outlined"
                        sx={{ borderRadius: 1 }}
                      />
                    )}
                  </Box>
                  <Typography variant="caption" color="text.secondary">
                    Uses your current backend settings. For cloud backends without valid credentials this will fail fast with an error.
                  </Typography>
                </Stack>
              </ResponsiveFormSection>

              {/* Summary */}
              <ResponsiveFormSection
                title="Diagnostic Summary"
                subtitle={`Backend: ${diagnostics.backend} • Health: ${diagnostics.summary.healthy ? 'Healthy' : 'Issues Detected'}`}
                icon={<HealthIcon />}
              >
                <Stack spacing={3}>
                  <Box>
                    <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
                      Overall Health
                    </Typography>
                    <Chip
                      icon={diagnostics.summary.healthy ? <CheckCircleIcon /> : <ErrorIcon />}
                      label={diagnostics.summary.healthy ? 'Healthy' : 'Issues Detected'}
                      color={diagnostics.summary.healthy ? 'success' : 'error'}
                      sx={{ borderRadius: 1 }}
                    />
                  </Box>

                  {getSuggestions(diagnostics).length > 0 && (
                    <Box>
                      <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
                        Issues & Suggestions
                      </Typography>
                      <List dense>
                        {getSuggestions(diagnostics).map((suggestion, idx) => (
                          <ListItem key={idx} sx={{ px: 0 }}>
                            <ListItemIcon sx={{ minWidth: 36 }}>
                              {getSuggestionIcon(suggestion.type)}
                            </ListItemIcon>
                            <ListItemText 
                              primary={suggestion.text}
                              primaryTypographyProps={{ 
                                variant: 'body2',
                                color: suggestion.type === 'error' ? 'error' : 'text.primary'
                              }}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}

                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Button
                      variant="outlined"
                      startIcon={<ContentCopyIcon />}
                      onClick={() => copyToClipboard(JSON.stringify(diagnostics, null, 2))}
                      size="small"
                      sx={{ borderRadius: 1 }}
                    >
                      Copy JSON
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<DownloadIcon />}
                      onClick={() => downloadText('diagnostics.json', JSON.stringify(diagnostics, null, 2))}
                      size="small"
                      sx={{ borderRadius: 1 }}
                    >
                      Download
                    </Button>
                  </Box>
                </Stack>
              </ResponsiveFormSection>

              {/* Provider Traits */}
              <ResponsiveFormSection
                title="Provider Traits"
                subtitle="Active provider capabilities and configuration"
                icon={<InfoIcon />}
              >
                <Stack spacing={2}>
                  <Box>
                    <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
                      Active Providers
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      <Chip
                        label={`Outbound: ${active?.outbound || 'None'}`}
                        color="primary"
                        variant="outlined"
                        sx={{ borderRadius: 1 }}
                      />
                      <Chip
                        label={`Inbound: ${active?.inbound || 'None'}`}
                        color="secondary"
                        variant="outlined"
                        sx={{ borderRadius: 1 }}
                      />
                    </Box>
                  </Box>

                  {active?.outbound && registry?.[active.outbound]?.traits && (
                    <Box>
                      <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
                        Outbound Traits
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                        {Object.entries(registry[active.outbound].traits || {}).map(([key, value]) => (
                          <Chip
                            key={key}
                            label={`${key}: ${String(value)}`}
                            size="small"
                            color="info"
                            variant="outlined"
                            sx={{ borderRadius: 1 }}
                          />
                        ))}
                      </Box>
                    </Box>
                  )}

                  {active?.inbound && registry?.[active.inbound]?.traits && active.inbound !== active.outbound && (
                    <Box>
                      <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
                        Inbound Traits
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                        {Object.entries(registry[active.inbound].traits || {}).map(([key, value]) => (
                          <Chip
                            key={key}
                            label={`${key}: ${String(value)}`}
                            size="small"
                            color="info"
                            variant="outlined"
                            sx={{ borderRadius: 1 }}
                          />
                        ))}
                      </Box>
                    </Box>
                  )}
                </Stack>
              </ResponsiveFormSection>

              {/* Check Sections */}
              <Box sx={{ mt: 3 }}>
                <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
                  System Checks
                </Typography>
                {Object.entries(diagnostics.checks).map(([title, checks]) => (
                  renderCheckSection(title.charAt(0).toUpperCase() + title.slice(1), checks as Record<string, any>)
                ))}
              </Box>
            </Box>
          </Fade>
        )}
      </Box>

      {/* Help Dialog */}
      <Dialog 
        open={helpOpen} 
        onClose={() => setHelpOpen(false)}
        maxWidth="sm"
        fullWidth
        fullScreen={isSmallMobile}
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <HelpIcon />
            Help: {helpTitle} - {helpKey.replace(/_/g, ' ')}
          </Box>
        </DialogTitle>
        <DialogContent>
          <Stack spacing={2}>
            {getHelpDocs(helpTitle, helpKey).map((doc, idx) => (
              <Box key={idx}>
                {doc.href ? (
                  <Link href={doc.href} target="_blank" rel="noreferrer">
                    {doc.text}
                  </Link>
                ) : (
                  <Typography variant="body2">{doc.text}</Typography>
                )}
              </Box>
            ))}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setHelpOpen(false)} sx={{ borderRadius: 2 }}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

export default Diagnostics;
