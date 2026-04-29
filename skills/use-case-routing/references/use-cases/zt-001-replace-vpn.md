---
id: zt-001
name: Replace your VPN with identity-based application access
category: zero-trust-secure-access
description: Identity-first, quantum-safe access to internal applications and infrastructure without a traditional VPN.
products: [Access, Cloudflare Tunnel, Gateway, WARP]
default_path: web-app-ztna
aliases:
  - VPN replacement
  - Zero Trust Network Access
  - ZTNA
  - Identity-based access
keywords:
  - "remove VPN"
  - "replace corporate VPN"
  - "internal app access"
  - "private network access"
  - "secure remote access"
  - "clientless SSH"
  - "browser-based RDP"
  - "Okta integration"
  - "Azure AD integration"
  - "Entra ID integration"
  - "Google Workspace SSO"
  - "SAML SSO for internal apps"
  - "OIDC for internal apps"
  - "SSO for internal apps"
  - "identity provider integration"
related:
  - zt-002
  - zt-013
  - zt-014
  - net-001
---

# Replace your VPN with identity-based application access

## Ask first

**What types of internal resources do users need to access?**
- Web applications (HTTP/HTTPS) → web-app-ztna
- SSH/RDP to servers → ssh-rdp-ztna
- Private network resources (non-web) → private-network-ztna
- All of the above → walk all three paths in order

**How large is the user base?** (informational; affects scaling guidance)
- Small team (< 50 users)
- Medium organization (50–500 users)
- Large enterprise (500+ users)

**Is there an existing identity provider?** (informational; affects step 1)
- Yes (Okta, Azure AD, Google Workspace, etc.) → use the existing IdP
- No or unsure → set up an IdP first

## Paths

### web-app-ztna (default)

For web application access:

1. Connect the identity provider to Cloudflare Access
2. Create a Cloudflare Tunnel to the internal web applications
3. Map a public hostname to the internal app via the tunnel
4. Create an Access application with identity-based policies
5. Define who can access (groups, emails, IdP-mapped attributes)

### ssh-rdp-ztna

For SSH and RDP access:

1. Connect the identity provider to Access
2. Create a Cloudflare Tunnel to the SSH/RDP servers
3. Create an Access application for SSH/RDP
4. Enable browser-based SSH or RDP for clientless access
5. Configure session recording and audit logging

### private-network-ztna

For private network resources (non-web):

1. Connect the identity provider
2. Create a Cloudflare Tunnel with private network routing
3. Add private network CIDR ranges to the tunnel
4. Deploy the WARP client to user devices
5. Create Gateway network policies for traffic filtering

## Hand off

For implementation, retrieve from Cloudflare docs:
https://developers.cloudflare.com/cloudflare-one/ (Access, Tunnel, Gateway, WARP).
Browse https://github.com/cloudflare/skills/tree/main/skills for any
matching builder skills.
