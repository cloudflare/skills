---
id: net-001
name: Consolidate your network and security into one cloud platform
category: network-connectivity-wan
description: Migrate from legacy perimeter security to unified SASE with one control plane for workforce, branch, and SaaS access.
products: [Cloudflare One]
default_path: workforce-first
aliases:
  - Evolve to SASE
  - SASE rollout
  - SSE deployment
  - Unified network and security platform
keywords:
  - "replace VPN"
  - "SSE alternative"
  - "cloud security platform alternative"
  - "secure access service edge"
  - "SSE"
  - "ZTNA rollout"
  - "branch security"
  - "consolidate point solutions"
related:
  - zt-001
  - zt-003
  - net-002
  - zt-016
---

# Consolidate your network and security into one cloud platform

## Ask first

**Where are you in your SASE journey?**
- Just starting / evaluating cloud-delivered security and networking → workforce-first
- Migrating from existing point solutions → migration-path
- Extending an existing partial SASE setup → workforce-first or branch-first depending on priority
- Not sure → workforce-first

**What is your highest priority?**
- Secure remote/hybrid workforce → workforce-first
- Connect and protect branch offices → branch-first
- Secure SaaS and Internet access → workforce-first
- All of the above → walk workforce-first, then branch-first

## Paths

### workforce-first (default)

Roll out SASE starting with the workforce:

1. Connect identity providers to Cloudflare Access
2. Deploy ZTNA to replace VPN for application access
3. Deploy Gateway as the Secure Web Gateway for Internet traffic
4. Create DLP profiles for data protection
5. Connect critical SaaS apps via CASB

### branch-first

Roll out SASE starting with branch offices:

1. Connect branch offices via Magic WAN (IPsec, GRE, or connector)
2. Deploy Magic Firewall as firewall-as-a-service for branch traffic
3. Deploy Gateway for branch Internet breakout
4. Layer on Access ZTNA for application-level access control

### migration-path

Migrate from existing point solutions:

1. Connect identity providers to Cloudflare Access
2. Create Cloudflare Tunnels to replace existing VPN concentrators
3. Recreate existing SWG and proxy policies in Gateway
4. Connect SaaS apps previously monitored by another CASB
5. Recreate DLP detection profiles in Cloudflare DLP

## Hand off

For implementation, retrieve from Cloudflare docs:
https://developers.cloudflare.com/cloudflare-one/, /magic-wan/, /magic-firewall/.
Browse https://github.com/cloudflare/skills/tree/main/skills for any
matching builder skills.
