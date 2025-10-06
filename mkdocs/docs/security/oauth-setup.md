---
title: OAuth / OIDC Setup
---

# OAuth / OIDC Setup

Protect the Admin Console with your identity provider.

## Steps

1) Create an OAuth/OIDC app in your IdP (Auth0/Okta/etc.)
2) Configure Redirect URI to your Admin domain
3) Enter client id/secret in Admin → Settings → Security
4) Test login from a private window

???+ tip "Scopes and claims"
    Map Admin roles from IdP claims if available. Keep Admin access limited to operators.

## Troubleshooting

- Invalid redirect → verify exact URI and HTTPS
- Forbidden → check user group/role mapping

