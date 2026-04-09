# CLI, MCP, and Project Setup

This reference covers managing Cloudflare Email Service from the command line using wrangler, using MCP tools from coding agents, and scaffolding new email-enabled projects.

## Table of Contents

- [Wrangler Email Commands](#wrangler-email-commands)
- [Domain Setup](#domain-setup)
- [Scaffolding a New Email Project](#scaffolding-a-new-email-project)
- [Development and Deployment](#development-and-deployment)
- [MCP Tools for Coding Agents](#mcp-tools-for-coding-agents)
- [Sending Emails from a Coding Agent](#sending-emails-from-a-coding-agent)

## Wrangler Email Commands

Wrangler has dedicated commands for managing email routing and email sending. These wrap the Cloudflare Email Routing and Email Sending REST APIs.

### Command Tree

```
wrangler email routing
├── list                                            # List zones with email routing
├── settings       <domain>                         # Get settings for a zone
├── enable         <domain>                         # Enable email routing
├── disable        <domain>                         # Disable email routing
├── dns get        <domain>                         # Show required DNS records
├── dns unlock     <domain>                         # Unlock MX records
├── rules list     <domain>                         # List routing rules
├── rules get      <domain> <rule-id>               # Get a routing rule (use 'catch-all' as rule-id for catch-all)
├── rules create   <domain>                         # Create a routing rule
├── rules update   <domain> <rule-id>               # Update a routing rule
├── rules delete   <domain> <rule-id>               # Delete a routing rule
└── addresses list|get|create|delete                # Destination addresses (account-scoped)

wrangler email sending
├── list                                            # List zones with email sending
├── settings       <domain>                         # Get sending settings (zone + subdomains)
├── enable         <domain>                         # Enable email sending (auto-detects zone vs subdomain)
├── disable        <domain>                         # Disable email sending
├── dns get        <domain>                         # Show sending DNS records
├── send           --from --to --subject --text     # Send an email (builder flags)
└── send-raw       --from --to --mime/--mime-file   # Send a raw MIME email
```

All zone-scoped commands take `<domain>` as a positional argument. Wrangler auto-resolves the zone by walking up domain labels (e.g., `sub.example.com` tries `sub.example.com`, then `example.com`). Use `--zone-id` to skip zone lookup if your token lacks `zone:read`.

Destructive commands (`disable`, `dns unlock`, `rules delete`, `addresses delete`) prompt for confirmation. Use `--force` or `-y` to bypass.

### Email Routing Commands

```bash
# List all zones with email routing status
npx wrangler email routing list

# Get email routing settings for a domain
npx wrangler email routing settings example.com

# Enable email routing on a domain (adds MX, SPF, DKIM records)
npx wrangler email routing enable example.com

# Disable email routing (prompts for confirmation)
npx wrangler email routing disable example.com
npx wrangler email routing disable example.com --force  # Skip confirmation

# View required DNS records
npx wrangler email routing dns get example.com

# Unlock MX records (if locked by email routing)
npx wrangler email routing dns unlock example.com
```

### Routing Rules

```bash
# List all routing rules for a domain
npx wrangler email routing rules list example.com

# Get a specific rule (use 'catch-all' for the catch-all rule)
npx wrangler email routing rules get example.com <rule-id>
npx wrangler email routing rules get example.com catch-all

# Create a forwarding rule
npx wrangler email routing rules create example.com \
  --name "Support forwarding" \
  --match "support@example.com" \
  --forward "team@company.com" \
  --enabled

# Update a rule
npx wrangler email routing rules update example.com <rule-id> \
  --forward "new-team@company.com"

# Delete a rule (prompts for confirmation)
npx wrangler email routing rules delete example.com <rule-id>
```

### Destination Addresses

Destination addresses are account-scoped (not per-domain). These are the verified addresses that emails can be forwarded to.

```bash
# List all verified destination addresses
npx wrangler email routing addresses list

# Get details of a destination address
npx wrangler email routing addresses get <address-id>

# Add a new destination address (sends verification email)
npx wrangler email routing addresses create user@gmail.com

# Delete a destination address
npx wrangler email routing addresses delete <address-id>
```

### Email Sending Commands

```bash
# List zones with email sending enabled
npx wrangler email sending list

# Get sending settings for a domain (includes subdomains)
npx wrangler email sending settings example.com

# Enable email sending on a domain (auto-detects zone vs subdomain)
npx wrangler email sending enable example.com
npx wrangler email sending enable sub.example.com  # Works for subdomains too

# Disable email sending
npx wrangler email sending disable example.com

# View sending DNS records (SPF, DKIM)
npx wrangler email sending dns get example.com
```

### Sending Emails via CLI

The `wrangler email sending send` command lets you send emails directly from the command line — useful for testing, automation, and coding agents.

```bash
# Send an email with builder flags
npx wrangler email sending send \
  --from "noreply@example.com" \
  --to "recipient@example.com" \
  --subject "Test email" \
  --text "Hello from wrangler!"

# Send with HTML content
npx wrangler email sending send \
  --from "noreply@example.com" \
  --to "recipient@example.com" \
  --subject "Test email" \
  --html "<h1>Hello!</h1><p>Sent from wrangler.</p>" \
  --text "Hello! Sent from wrangler."

# Send with attachments and custom headers
npx wrangler email sending send \
  --from "noreply@example.com" \
  --to "recipient@example.com" \
  --subject "Invoice attached" \
  --text "Please find the invoice attached." \
  --attachment ./invoice.pdf \
  --header "X-Campaign-ID:monthly-invoice"

# Send a raw MIME email from a file
npx wrangler email sending send-raw \
  --from "noreply@example.com" \
  --to "recipient@example.com" \
  --mime-file ./email.eml

# Send a raw MIME email inline
npx wrangler email sending send-raw \
  --from "noreply@example.com" \
  --to "recipient@example.com" \
  --mime "From: sender@example.com\r\nTo: recipient@example.com\r\n..."
```

## Domain Setup

Before sending any emails, you need to onboard a domain to Email Service. This configures SPF, DKIM, and DMARC records automatically.

### Via Wrangler CLI

```bash
# Enable email sending on your domain
npx wrangler email sending enable yourdomain.com

# Verify DNS records were configured
npx wrangler email sending dns get yourdomain.com

# Enable email routing (for receiving emails)
npx wrangler email routing enable yourdomain.com

# Verify routing DNS records
npx wrangler email routing dns get yourdomain.com
```

### Via Dashboard

1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Navigate to **Compute & AI** > **Email Service** > **Email Sending**
3. Select **Onboard Domain**
4. Choose a domain from your Cloudflare account
5. Select **Continue** > **Add records and onboard**

This automatically adds:
- **TXT records** for SPF (authorizes Cloudflare to send on your behalf)
- **CNAME records** for DKIM (cryptographic signing for your emails)

DNS changes usually propagate within 5-15 minutes for domains using Cloudflare DNS.

## Scaffolding a New Email Project

### Email Sending Worker

```bash
# Create a new Worker project
npm create cloudflare@latest -- my-email-worker
# Select "Hello World" Worker when prompted

cd my-email-worker
```

Add the email binding to `wrangler.jsonc`:

```jsonc
{
  "$schema": "./node_modules/wrangler/config-schema.json",
  "name": "my-email-worker",
  "main": "src/index.ts",
  "compatibility_date": "2025-01-01",
  "send_email": [
    {
      "name": "EMAIL"
    }
  ]
}
```

Write the Worker in `src/index.ts`:

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    await env.EMAIL.send({
      to: "test@example.com",
      from: { email: "hello@yourdomain.com", name: "My App" },
      subject: "Hello from my Worker!",
      html: "<h1>It works!</h1>",
      text: "It works!",
    });
    return new Response("Email sent!");
  },
} satisfies ExportedHandler<Env>;
```

### Email Routing Worker (Inbound)

```bash
npm create cloudflare@latest -- my-email-processor
cd my-email-processor
npm install postal-mime
```

Write the email handler in `src/index.ts`:

```typescript
import PostalMime from "postal-mime";

export default {
  async email(message, env, ctx): Promise<void> {
    const raw = await new Response(message.raw).arrayBuffer();
    const parsed = await PostalMime.parse(raw);

    console.log(`From: ${message.from}, Subject: ${parsed.subject}`);
    await message.forward("your-inbox@gmail.com");
  },
} satisfies ExportedHandler<Env>;
```

Deploy, then configure a routing rule to point an address to this Worker:

```bash
npx wrangler deploy
npx wrangler email routing rules create yourdomain.com \
  --name "Support to Worker" \
  --match "support@yourdomain.com" \
  --forward "worker:my-email-processor"
```

### Combined Send + Receive Worker

```jsonc
// wrangler.jsonc
{
  "name": "email-service",
  "main": "src/index.ts",
  "compatibility_date": "2025-01-01",
  "compatibility_flags": ["nodejs_compat"],
  "send_email": [
    { "name": "EMAIL" }
  ]
}
```

```typescript
import PostalMime from "postal-mime";

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    await env.EMAIL.send({
      to: "user@example.com",
      from: { email: "noreply@yourdomain.com", name: "My App" },
      subject: "Notification",
      text: "Something happened!",
    });
    return new Response("Sent");
  },

  async email(message, env, ctx): Promise<void> {
    const raw = await new Response(message.raw).arrayBuffer();
    const parsed = await PostalMime.parse(raw);

    await env.EMAIL.send({
      to: message.from,
      from: { email: "support@yourdomain.com", name: "Support" },
      subject: `Re: ${parsed.subject}`,
      text: "Thanks! We got your message.",
    });
  },
} satisfies ExportedHandler<Env>;
```

## Development and Deployment

### Local Development

Add `"remote": true` to the `send_email` binding in `wrangler.jsonc` so your Worker runs locally but email sends go through the real Email Service:

```jsonc
{ "send_email": [{ "name": "EMAIL", "remote": true }] }
```

```bash
# Start dev server — Worker runs locally, email binding proxies to Cloudflare
npx wrangler dev

# Start on a specific port
npx wrangler dev --port 8787
```

Emails are actually sent during `wrangler dev` with remote bindings. Use verified test addresses during development. Remove `"remote": true` before deploying to production.

### Deployment

```bash
# Deploy your Worker
npx wrangler deploy

# Preview what will be deployed
npx wrangler deploy --dry-run

# View real-time logs from your deployed Worker
npx wrangler tail
```

### Secrets Management

```bash
# Set a secret (prompts for value — never visible in logs)
npx wrangler secret put EMAIL_SECRET

# List secrets
npx wrangler secret list
```

Access secrets in your Worker as `env.EMAIL_SECRET`.

## MCP Tools for Coding Agents

Coding agents (Claude Code, Cursor, Copilot, etc.) can interact with Cloudflare Email Service through MCP servers:

| MCP Server | URL | What It Does |
|------------|-----|--------------|
| `cloudflare-api` | `https://mcp.cloudflare.com/mcp` | Manage Cloudflare resources (Workers, domains, DNS) |
| `cloudflare-docs` | `https://docs.mcp.cloudflare.com/mcp` | Search Cloudflare documentation |
| `cloudflare-bindings` | `https://bindings.mcp.cloudflare.com/mcp` | Interact with Worker bindings |
| `cloudflare-builds` | `https://builds.mcp.cloudflare.com/mcp` | Build and deploy Workers |
| `cloudflare-observability` | `https://observability.mcp.cloudflare.com/mcp` | View logs and analytics |

Use the `cloudflare-docs` MCP server to look up the latest Email Service documentation — more reliable than pre-trained knowledge.

## Sending Emails from a Coding Agent

If a coding agent needs to send an email (testing, notifications, etc.), there are two approaches:

### Via Wrangler CLI (Simplest)

The most direct way — no API keys or HTTP calls needed. Wrangler uses the authenticated session from `wrangler login`.

```bash
# Send a test email directly from the terminal
npx wrangler email sending send \
  --from "agent@yourdomain.com" \
  --to "developer@company.com" \
  --subject "Deployment Complete" \
  --text "Your Worker was deployed successfully."
```

### Via REST API

For agents that need to send programmatically without wrangler:

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

The agent needs `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` as environment variables. These should be pre-configured — the agent should never ask the user to paste tokens directly into the chat.
