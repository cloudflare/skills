# Sending Emails — Workers Binding & Agents SDK

Send emails from Cloudflare Workers using the native binding, or from AI agents using the Agents SDK. If your app is NOT on Workers, use the [REST API](rest-api.md) instead.

## Workers Binding

### Configuration

```jsonc
// wrangler.jsonc
{
  "send_email": [
    { "name": "EMAIL" }
  ]
}
```

For local development, add `"remote": true` so email sends are proxied to the real service:

```jsonc
{ "send_email": [{ "name": "EMAIL", "remote": true }] }
```

Run `npx wrangler types` to auto-generate the `Env` interface with your `EMAIL` binding.

### TypeScript Interfaces

```typescript
interface SendEmail {
  send(message: EmailMessage | EmailMessageBuilder): Promise<EmailSendResult>;
}

interface EmailMessageBuilder {
  to: string | string[];                // Max 50 recipients
  from: string | { email: string; name: string };
  subject: string;
  html?: string;
  text?: string;
  cc?: string | string[];
  bcc?: string | string[];
  replyTo?: string | { email: string; name: string };
  attachments?: Attachment[];
  headers?: { [key: string]: string };
}

interface Attachment {
  content: string | ArrayBuffer;        // Base64 string or binary
  filename: string;
  type: string;                         // MIME type
  disposition: "attachment" | "inline";
  contentId?: string;                   // Required for inline
}

interface EmailSendResult {
  messageId: string;
}
// Errors thrown with .code and .message properties
```

**Note:** Workers binding uses `email` in the from object. REST API uses `address`. See [rest-api.md](rest-api.md).

## send()

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const response = await env.EMAIL.send({
      to: "user@example.com",
      from: { email: "welcome@yourdomain.com", name: "My App" },
      subject: "Welcome!",
      html: "<h1>Welcome!</h1><p>Thanks for signing up.</p>",
      text: "Welcome! Thanks for signing up.",
    });
    return new Response(`Sent: ${response.messageId}`);
  },
} satisfies ExportedHandler<Env>;
```

Multiple recipients (max 50 combined to + cc + bcc):

```typescript
const response = await env.EMAIL.send({
  to: ["user1@example.com", "user2@example.com"],
  cc: ["manager@company.com"],
  bcc: ["archive@company.com"],
  from: { email: "orders@yourdomain.com", name: "Orders" },
  replyTo: "support@yourdomain.com",
  subject: "Order Confirmation #12345",
  html: "<h1>Your order is confirmed</h1>",
  text: "Your order is confirmed",
});
```

## Attachments

```typescript
// File attachment
const response = await env.EMAIL.send({
  to: "customer@example.com",
  from: "invoices@yourdomain.com",
  subject: "Your Invoice",
  html: "<h1>Invoice attached</h1>",
  text: "Invoice attached.",
  attachments: [{
    content: "JVBERi0xLjQKJeLjz9MK...", // Base64-encoded PDF
    filename: "invoice-12345.pdf",
    type: "application/pdf",
    disposition: "attachment",
  }],
});

// Inline image — reference in HTML with cid:<contentId>
const response = await env.EMAIL.send({
  to: "user@example.com",
  from: "marketing@yourdomain.com",
  subject: "New Product",
  html: '<img src="cid:product-hero" alt="Product" />',
  attachments: [{
    content: "iVBORw0KGgoAAAANSUhEUgAA...",
    filename: "product.png",
    type: "image/png",
    disposition: "inline",
    contentId: "product-hero",
  }],
});
```

Total email size (body + attachments) cannot exceed 25 MiB. Base64 adds ~33% overhead.

## Custom Headers

Only whitelisted headers allowed. See the [headers reference](https://developers.cloudflare.com/email-service/reference/headers/).

```typescript
const response = await env.EMAIL.send({
  to: "user@example.com",
  from: "notifications@yourdomain.com",
  subject: "Your weekly digest",
  html: "<h1>Weekly Digest</h1>",
  headers: {
    "In-Reply-To": "<original-message-id@yourdomain.com>",
    "List-Unsubscribe": "<https://yourdomain.com/unsubscribe?id=abc123>",
    "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
    "X-Campaign-ID": "weekly-digest-2026-03",
  },
});
```

## Legacy EmailMessage API

The `EmailMessage` API remains supported. Uses raw MIME via `mimetext`:

```typescript
import { EmailMessage } from "cloudflare:email";
import { createMimeMessage } from "mimetext";

const msg = createMimeMessage();
msg.setSender({ name: "Sender", addr: "sender@yourdomain.com" });
msg.setRecipient("recipient@example.com");
msg.setSubject("Hello");
msg.addMessage({ contentType: "text/html", data: "<h1>Hello</h1>" });

await env.EMAIL.send(new EmailMessage("sender@yourdomain.com", "recipient@example.com", msg.asRaw()));
```

Requires `npm install mimetext` and `"nodejs_compat"` in compatibility flags.

## Agents SDK Email

Agents can receive and reply to emails natively via the Agents SDK.

```jsonc
// wrangler.jsonc
{
  "durable_objects": {
    "bindings": [{ "name": "EmailAgent", "class_name": "EmailAgent" }]
  },
  "migrations": [{ "tag": "v1", "new_sqlite_classes": ["EmailAgent"] }],
  "send_email": [{ "name": "EMAIL", "destination_address": "reply@yourdomain.com" }]
}
```

```typescript
import { Agent } from "agents";
import { type AgentEmail } from "agents/email";
import PostalMime from "postal-mime";

export class EmailAgent extends Agent<Env, State> {
  async onEmail(email: AgentEmail) {
    const parsed = await PostalMime.parse(await email.getRaw());
    await this.replyToEmail(email, {
      fromName: "My Agent",
      subject: `Re: ${parsed.subject}`,
      body: "Thanks for your email! I'll look into this.",
    });
  }
}
```

Route emails to agents with resolvers:

```typescript
import { routeAgentEmail } from "agents";
import { createAddressBasedEmailResolver } from "agents/email";

export default {
  async email(message, env) {
    await routeAgentEmail(message, env, {
      resolver: createAddressBasedEmailResolver("EmailAgent"),
    });
  },
};
```

Resolver types: `createAddressBasedEmailResolver` (recipient → instance name), `createSecureReplyEmailResolver(secret)` (HMAC-signed replies), `createCatchAllEmailResolver("Agent", "default")` (single inbox). Use `isAutoReplyEmail(email.headers)` to skip vacation responders.

## Error Handling

```typescript
try {
  const response = await env.EMAIL.send({ /* ... */ });
} catch (error) {
  // error.code is one of the E_* error codes
  console.error(`Failed: ${error.code} - ${error.message}`);
}
```

See [SKILL.md](../SKILL.md#error-codes) for the full error codes table.

## Restricted Bindings

Restrict which `from` addresses a binding can use:

```jsonc
{
  "send_email": [{
    "name": "RESTRICTED_EMAIL",
    "allowed_sender_addresses": ["noreply@yourdomain.com", "support@yourdomain.com"]
  }]
}
```
