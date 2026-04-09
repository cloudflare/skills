# CLI, MCP, and Project Setup

Manage Cloudflare Email Service from the command line and coding agents.

For full CLI reference, run `npx wrangler email --help`. For Dashboard setup, see the [getting started docs](https://developers.cloudflare.com/email-service/get-started/).

## Wrangler Email Commands

```
wrangler email routing
├── enable/disable   <domain>          # Toggle email routing
├── dns get          <domain>          # Show required DNS records
├── rules list/create/update/delete    # Manage routing rules
└── addresses list/create/delete       # Destination addresses (account-scoped)

wrangler email sending
├── enable/disable   <domain>          # Toggle email sending
├── dns get          <domain>          # Show sending DNS records (SPF, DKIM)
├── send             --from --to ...   # Send an email (builder flags)
└── send-raw         --from --to ...   # Send a raw MIME email
```

## Domain Setup

### Via Dashboard

1. Navigate to **Compute & AI** > **Email Service** > **Email Sending** (or **Email Routing**)
2. Select **Onboard Domain** > choose domain > **Add records and onboard**

This auto-adds SPF (TXT) and DKIM (CNAME/TXT) records. DNS usually propagates within 5-15 minutes.

### Via CLI

```bash
npx wrangler email sending enable yourdomain.com
npx wrangler email sending dns get yourdomain.com   # Verify records
```

## Local Development

Add `"remote": true` to send real emails during `wrangler dev`:

```jsonc
{ "send_email": [{ "name": "EMAIL", "remote": true }] }
```

```bash
npx wrangler dev
```

Emails are actually sent — use test addresses you control. Remove `"remote": true` before deploying.

## MCP Tools for Coding Agents

| MCP Server | URL | Use for |
|------------|-----|---------|
| `cloudflare-docs` | `https://docs.mcp.cloudflare.com/mcp` | Search Email Service docs |
| `cloudflare-api` | `https://mcp.cloudflare.com/mcp` | Manage Workers, domains, DNS |
| `cloudflare-bindings` | `https://bindings.mcp.cloudflare.com/mcp` | Interact with Worker bindings |

## Sending from CLI / Agents

```bash
npx wrangler email sending send \
  --from "agent@yourdomain.com" \
  --to "developer@company.com" \
  --subject "Deployment Complete" \
  --text "Your Worker was deployed successfully."
```

Or via REST API:

```bash
curl "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/email/sending/send" \
  --header "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
  --header "Content-Type: application/json" \
  --data '{
    "to": "developer@company.com",
    "from": {"address": "agent@yourdomain.com", "name": "Build Agent"},
    "subject": "Deployment Complete",
    "text": "Your Worker was deployed successfully."
  }'
```
