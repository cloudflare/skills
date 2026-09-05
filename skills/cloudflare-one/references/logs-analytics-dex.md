# Logs, Analytics, and DEX

## Guardrails

- [Gateway activity logs](https://developers.cloudflare.com/cloudflare-one/analytics/logs/gateway-logs/) record DNS, HTTP, and Network policy decisions. Filter by rule name, user identity, destination, action, and time range. These are the primary troubleshooting tool for "why was this blocked/allowed."
- [Access audit logs](https://developers.cloudflare.com/cloudflare-one/insights/logs/dashboard-logs/access-authentication-logs/) record authentication decisions per app - who authenticated, which policy matched, and session details. Use for verifying policy behavior and investigating access failures.
- [Shadow IT discovery](https://developers.cloudflare.com/cloudflare-one/insights/analytics/shadow-it-discovery/) uses Gateway HTTP logs to surface unmanaged SaaS applications. Requires TLS inspection for HTTPS visibility.
- [DEX (Digital Experience Monitoring)](https://developers.cloudflare.com/cloudflare-one/insights/dex/) provides fleet-level and per-device connectivity diagnostics. Use [DEX tests](https://developers.cloudflare.com/cloudflare-one/insights/dex/tests/) (HTTP, traceroute) to proactively monitor reachability to critical origins and internal apps. Fleet status shows device client health, connection mode, and connectivity state across the enrolled population.
- [Logpush](https://developers.cloudflare.com/cloudflare-one/analytics/logs/logpush/) exports Gateway, Access, Network, and DEX logs to external SIEM or storage. Configure before go-live if the customer requires centralized log retention or compliance reporting.
- When troubleshooting, work from logs toward config: identify the log entry showing the failure (Gateway block, Access deny, tunnel error, DNS resolution miss), then trace back to the responsible rule, route, or policy.
