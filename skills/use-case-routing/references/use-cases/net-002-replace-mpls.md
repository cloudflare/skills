---
id: net-002
name: Connect all your offices and clouds over Cloudflare instead of expensive leased lines
category: network-connectivity-wan
description: Connect branch offices, data centers, and clouds over Cloudflare's network as an alternative to MPLS or traditional SD-WAN.
products: [Cloudflare WAN]
default_path: software-wan
aliases:
  - Replace MPLS with cloud WAN
  - MPLS replacement
  - Software-defined WAN
  - SD-WAN
  - Branch office connectivity
keywords:
  - "Cisco SD-WAN integration"
  - "Fortinet SD-WAN integration"
  - "Palo Alto SD-WAN integration"
  - "SonicWall integration"
  - "Juniper integration"
  - "IPsec tunnel branch"
  - "GRE tunnel"
  - "leased line replacement"
  - "site-to-site connectivity"
  - "private network interconnect"
related:
  - net-004
  - net-007
  - net-001
---

# Connect all your offices and clouds over Cloudflare instead of expensive leased lines

## Ask first

**What are you connecting?**
- Branch offices to each other and headquarters → software-wan or tunnel-wan
- On-prem data centers to cloud environments → tunnel-wan or cni-wan
- All of the above → walk all paths that fit your connection method below

**How do you want to connect your sites to Cloudflare?**
- Software connector (cloudflared or Cloudflare Mesh) → software-wan
- Encrypted tunnels from existing routers or firewalls (IPsec/GRE) → tunnel-wan
- Direct physical interconnect (CNI) → cni-wan
- Mix of methods → walk software-wan and tunnel-wan

## Paths

### software-wan (default)

Software-based WAN connectivity:

1. Deploy cloudflared or the WARP Connector at each site
2. Configure private network routes for each site
3. Define which traffic routes through Cloudflare via split tunnel settings
4. Create Magic Firewall rules for inter-site traffic

### tunnel-wan

Tunnel-based WAN over IPsec or GRE:

1. Follow the Magic WAN integration guide for your network device (guides cover Cisco, Fortinet, Palo Alto, SonicWall, Juniper, and others)
2. Establish IPsec or GRE tunnels from your routers and firewalls
3. Configure static routes for site subnets
4. Enable tunnel health checks and failover
5. Create Magic Firewall rules for traffic segmentation

### cni-wan

Direct interconnect via CNI:

1. Provision a physical or virtual interconnect at a peering facility
2. Establish BGP sessions over the interconnect
3. Configure Magic WAN routing for the connected networks

## Hand off

For implementation, retrieve from Cloudflare docs:
https://developers.cloudflare.com/magic-wan/, /magic-firewall/,
/network-interconnect/, /cloudflare-one/.
Browse https://github.com/cloudflare/skills/tree/main/skills for any
matching builder skills.
