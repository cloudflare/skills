# DNS-AID — DNS for AI Discovery

Publish ServiceMode SVCB records under `_agents.<domain>` so resolvers/agents can discover entrypoints via DNS, and sign the zone with DNSSEC so the answers are authenticated.

Spec: `draft-mozleywilliams-dnsop-dnsaid` (Internet-Draft) + RFC 9460 (SVCB/HTTPS).

## Records

Point each label at the real host for that entrypoint:

```dns
_index._agents.example.com.  3600 IN SVCB 1 example.com.            ( alpn="h2,h3" port=443 )   ; → /.well-known/api-catalog
_mcp._agents.example.com.    3600 IN SVCB 1 mcp.example.com.        ( alpn="h2"    port=443 )   ; → MCP server
_a2a._agents.example.com.    3600 IN SVCB 1 agents.example.com.     ( alpn="h2"    port=443 )   ; → A2A endpoint
```

Only publish a label if the target host actually exists. If your MCP server lives on `*.workers.dev`, set the SVCB TargetName to that host directly rather than inventing a subdomain.

## Create via Cloudflare API

```bash
ZONE=<zone-id>
api(){ curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE/dns_records" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" --data "$1" | jq -c '{ok:.success, name:.result.name}'; }

api '{"type":"SVCB","name":"_index._agents","data":{"priority":1,"target":"example.com","value":"alpn=\"h2,h3\" port=443"},"ttl":3600}'
api '{"type":"SVCB","name":"_mcp._agents","data":{"priority":1,"target":"mcp.example.com","value":"alpn=\"h2\" port=443"},"ttl":3600}'
```

The draft's `endpoint=` SvcParam isn't an IANA-registered SvcParamKey; Cloudflare may reject it. Standard `alpn`/`port` params satisfy "ServiceMode SVCB with alpn"; convey the path via the api-catalog the `_index` record points to.

## DNSSEC

```bash
# enable signing at Cloudflare (safe: no resolution impact until the DS is at the registrar)
curl -s -X PATCH "https://api.cloudflare.com/client/v4/zones/$ZONE/dnssec" \
  -H "Authorization: Bearer $TOKEN" --data '{"status":"active"}' | jq -c '{status:.result.status}'   # -> "pending"
# fetch the DS record to hand to the registrar
curl -s "https://api.cloudflare.com/client/v4/zones/$ZONE/dnssec" -H "Authorization: Bearer $TOKEN" \
  | jq -r '.result | "DS \(.key_tag) \(.algorithm) \(.digest_type) \(.digest)"'
```

Then **add that DS at the registrar** (Settings → DNSSEC). Status flips `pending → active` once the parent zone has the DS. If the domain is registered at Cloudflare it auto-activates; otherwise this is a manual step only the domain owner can do.

## Verify

```bash
dig _index._agents.example.com TYPE64 +short      # SVCB present (old dig won't pretty-print; raw \# hex is fine)
dig +dnssec example.com SOA | grep RRSIG          # zone signed
delv _mcp._agents.example.com SVCB                # authenticated answer once DS is live
```
