# Device Client Deployment

## Guardrails

- The [Cloudflare One device client](https://developers.cloudflare.com/cloudflare-one/team-and-resources/devices/cloudflare-one-client/) is the on-ramp for user devices. Two components control it: **enrollment rules** (who can connect) and **device profiles** (how the client behaves after enrollment).
- The enrollment rule is an Access application of type `warp`, not a device setting. It accepts reusable Access policies. Look in Access for enrollment debugging, not Devices.
- For headless or autonomous devices (services, kiosks, Linux hosts), use service token enrollment. Non-human devices authenticate as `non_identity@[team-domain].cloudflareaccess.com` and have no group membership - device profiles targeting IdP groups will not match them. Target headless devices explicitly with the non-identity email, specific conventions about the devices (OS information, etc.),or let them fall to the default profile.
- Device profiles control connection mode, [split tunnel](https://developers.cloudflare.com/cloudflare-one/team-and-resources/devices/cloudflare-one-client/configure/route-traffic/split-tunnels/) configuration, user permissions (disable, switch lock), auto-reconnect, and captive portal behavior. Profiles are matched by user group or device attributes in precedence order - first match wins, default profile catches the rest.
- Split tunnel mode is the single most impactful client setting. Choose the mode based on the deployment goal:

  | Goal | Mode | Rationale |
  |---|---|---|
  | VPN replacement only (private apps) | **Include** | Route only specified private CIDRs and hostnames through the client. Everything else goes direct. Minimal blast radius. |
  | SWG only (internet security) | **Exclude** | All traffic through the client. Exclude only what breaks (local printers, certificate-pinned apps). |
  | VPN replacement + SWG | **Exclude** | All traffic through the client. Most common enterprise configuration. |
  | Coexistence with another VPN | **Include** | Avoids conflict with the other VPN's tunnel interface and DNS control. |
  | DNS filtering only | DNS-only mode | Only DNS queries go to Gateway. No traffic proxying. |

- Include vs exclude is per-profile, not per-entry. You cannot mix modes in the same profile. Switching modes mid-deployment requires re-evaluating every entry.
- Split tunnel entries must align with tunnel routes bidirectionally. A CIDR in the include list without a matching tunnel route causes a black hole. A tunnel route without a matching device profile entry means traffic never enters the tunnel.
- MDM parameters (`mdm.xml` / managed preferences) override dashboard-configured profile settings for any setting specified in the file. If dashboard changes appear to have no effect on managed devices, check MDM config. Retrieve [MDM deployment](https://developers.cloudflare.com/cloudflare-one/team-and-resources/devices/cloudflare-one-client/deployment/mdm-deployment/) docs for platform-specific file locations and parameters.
- If another VPN client or agent controls DNS on the device, the device client's DNS interception will conflict. In coexistence scenarios, use "traffic only" mode to avoid routing table and DNS conflicts.
- Captive portal detection temporarily disconnects the client when it detects a portal (hotel WiFi, airport).  This is a common source of end-user friction and should be managed carefully.
