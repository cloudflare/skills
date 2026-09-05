# Access and SaaS Federation

## Assessment

Ask only the prompts relevant to the task.

- App shape: web app, API, SSH/RDP/VNC, database, SaaS app, public hostname, private IP, or private hostname. Retrieve [Access application type](https://developers.cloudflare.com/cloudflare-one/access-controls/applications/choose-application-type/) docs before choosing.
- Access model: clientless browser access, private networking with device client, peer to peer connectivity, service connections with service tokens or mutual TLS, or SaaS SSO federation.
- Policy needs: user groups, device posture, session duration, mTLS, service tokens, and app launcher visibility. Retrieve [Access policy](https://developers.cloudflare.com/cloudflare-one/access-controls/policies/) docs before configuring selectors or evaluation order.
- SaaS details: SAML vs OIDC support, ACS/redirect URLs, Entity IDs/client IDs, required attributes, and tenant-control requirements.

## Guardrails

- Access Groups are Cloudflare objects; IdP/SCIM groups are identity claims. Gateway group selectors use synced IdP groups, not Access Groups.
- Group names and SAML/OIDC attributes are case-sensitive. Verify exact claim names and values before creating group-based rules.
- SCIM changes and group membership can be stale until sync and re-authentication complete. Troubleshoot with the user's last authenticated identity, not just the IdP state.
- Access policies are default-deny. A private app with routes but no Allow policy still blocks access.
- Access policy selectors can use IP lists, not Gateway domain or URL lists.
- SaaS federation handles authentication into the SaaS app. SaaS authorization and tenant restrictions usually require SaaS-side roles and/or Gateway tenant controls.
- Browser Rendering for SSH/VNC/RDP is an Access capability. Browser Isolation renders general web content remotely. Do not conflate them.

## Validation

- Access: test authorized, unauthorized, posture-failing, service-token, and multi-IdP flows when applicable; inspect logs and policy precedence.
