---
id: gov-003
name: Meet US federal compliance requirements (FedRAMP, TIC 3.0)
category: compliance-data-governance
description: Deploy Cloudflare services in FedRAMP processing locations and extend TIC 3.0 security capabilities globally.
products: [Cloudflare for Government, Network Services (FedRAMP), Gateway, Logs]
default_path: fedramp-setup
aliases:
  - Achieve FedRAMP authorization
  - Implement TIC 3.0 compliance
  - Federal government compliance
keywords:
  - "FedRAMP Moderate"
  - "FedRAMP High"
  - "TIC 3.0"
  - "CISA compliance"
  - "federal authorization"
  - "government cloud"
  - "audit logging for compliance"
related:
  - ind-006
  - ind-009
  - net-001
---

# Meet US federal compliance requirements (FedRAMP, TIC 3.0)

## Ask first

**Which compliance program applies?**
- FedRAMP authorization (Moderate or High) → fedramp-setup
- TIC 3.0 implementation → tic-3-setup
- Both → walk both paths

## Paths

### fedramp-setup (default)

For FedRAMP deployment:

1. Engage the Cloudflare for Government team
2. Confirm FedRAMP Moderate authorization (High in process)
3. Deploy services in FedRAMP processing locations
4. Configure security controls per FedRAMP requirements
5. Enable comprehensive audit logging via Logs

### tic-3-setup

For TIC 3.0 implementation:

1. Review Cloudflare's TIC 3.0 capability mapping
2. Extend the TIC boundary from centralized data centers to Cloudflare's global network
3. Configure Gateway traffic inspection per TIC 3.0 use cases
4. Configure Logs telemetry for CISA compliance

## Hand off

For implementation, retrieve from Cloudflare docs:
https://developers.cloudflare.com/cloudflare-one/, /logs/.
Browse https://github.com/cloudflare/skills/tree/main/skills for any
matching builder skills.
