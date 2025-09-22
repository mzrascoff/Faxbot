# OAuth2 / OIDC Setup for Faxbot MCP (SSE)

This guide shows how to configure JWT validation for the SSE transport. It covers what is validated, the environment variables Faxbot needs, and quick links for popular identity providers.

What the MCP SSE servers validate
- Issuer (`iss`): must match `OAUTH_ISSUER`
- Audience (`aud`): must match `OAUTH_AUDIENCE` (e.g., `faxbot-mcp`)
- Signature: verified against the provider’s JWKS (`OAUTH_JWKS_URL`)
- Expiry / not-before: standard JWT time checks

Environment variables
```
OAUTH_ISSUER     # Your OIDC issuer URL (no trailing slash)
OAUTH_AUDIENCE   # The audience/identifier of the API you expose to clients (string)
OAUTH_JWKS_URL   # JWKS endpoint (optional if your issuer uses the default well-known path)
```

General steps (any provider)
1) Create or identify an API/resource in your IdP.
   - Set an identifier value (this becomes the `aud` claim). Example: `faxbot-mcp`.
2) Create a client/app that can obtain access tokens for that API (client credentials or the flow used by your client).
3) Find your issuer URL and JWKS URL (from the OIDC discovery document at `${issuer}/.well-known/openid-configuration`).
4) Export env vars and start the SSE server (Node or Python).
5) Obtain a token from the IdP and connect to `/sse` with `Authorization: Bearer <token>`.

Provider specifics and links

Auth0
- Issuer: `https://YOUR_TENANT.auth0.com`
- Audience: your API Identifier (e.g., `faxbot-mcp`)
- JWKS: `https://YOUR_TENANT.auth0.com/.well-known/jwks.json`
- Docs: create API, JWKS/token validation, client credentials flow

Okta
- Issuer: `https://YOUR_DOMAIN.okta.com/oauth2/default` (or your custom auth server)
- Audience: the custom API audience you configure
- JWKS: `${issuer}/v1/keys`

Microsoft Entra ID (Azure AD)
- Issuer: `https://login.microsoftonline.com/<TENANT_ID>/v2.0`
- Audience: App Registration → “Expose an API” → Application ID URI (or custom ID you set)
- JWKS: `https://login.microsoftonline.com/<TENANT_ID>/discovery/v2.0/keys`

Google Identity
- Issuer: `https://accounts.google.com`
- JWKS: `https://www.googleapis.com/oauth2/v3/certs`

Keycloak (self‑hosted)
- Issuer: `https://YOUR_HOST/realms/YOUR_REALM`
- JWKS: `${issuer}/protocol/openid-connect/certs`

Quick test (Auth0 example)
```
# Request a token (client credentials)
curl https://$AUTH0_DOMAIN/oauth/token \
  -H 'content-type: application/json' \
  -d '{"grant_type":"client_credentials","client_id":"'$AUTH0_CLIENT_ID'","client_secret":"'$AUTH0_CLIENT_SECRET'","audience":"'$AUDIENCE'"}'

# Connect to SSE with Authorization: Bearer <token>
curl -H "Authorization: Bearer $TOKEN" -H "Accept: text/event-stream" http://localhost:3002/sse
```

Notes
- The SSE servers validate tokens; they don’t mint them. Use your IdP or an internal OAuth server to issue access tokens.
- For HIPAA deployments, ensure TLS, MFA, and appropriate access policies at your IdP and proxy.
