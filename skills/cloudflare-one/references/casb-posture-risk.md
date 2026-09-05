# CASB, Device Posture, and Risk

## Assessment

Ask only the prompts relevant to the task.

- CASB: SaaS vendors, admin access level, scan policy, org size, remediation owner, and whether inline protection is also required. Retrieve [CASB findings](https://developers.cloudflare.com/cloudflare-one/cloud-and-saas-findings/manage-findings/) docs before recommending remediation.
- Device posture: required checks, third-party EDR/MDM integrations, enrollment rules, device profiles, and split tunnel alignment.
- Risk scoring: relevant behavior signals, false-positive sources such as VPNs or service accounts, and whether risk is for investigation or enforcement. Retrieve [user risk score](https://developers.cloudflare.com/cloudflare-one/team-and-resources/users/risk-score/) docs before using risk in policies.

## Guardrails

- API CASB is out-of-band and periodic. It does not provide real-time inline enforcement although some integrations support "remediation"; use Gateway granular application controls for inline CASB capability for supported applications. Retrieve [Granular application controls](https://developers.cloudflare.com/cloudflare-one/traffic-policies/http-policies/granular-controls/) when creating security policies for specific actions in specific SaaS applications.
- CASB findings are tied to specific assets and instances. Drill into affected assets before recommending remediation.
- Use current Dashboard remediation guidance for CASB fixes. Most remediations happen in the SaaS admin console, not Cloudflare.
- Large SaaS integrations can take 24-48 hours for initial scans. Reauthorizing can restart scan state; check credential health before reconnecting.
- User risk scores are behavior-based and asynchronous. CASB findings do not automatically imply high user risk.

## Validation

- CASB/risk: confirm integration health, credential expiry, asset discovery, scan timing, finding instances, and risk-score signal latency before declaring remediation complete.
