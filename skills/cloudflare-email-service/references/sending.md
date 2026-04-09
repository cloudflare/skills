# Sending Emails — Workers Binding & Agents SDK

This reference covers sending emails from Cloudflare Workers using the native binding, and from AI agents using the Agents SDK. Both approaches share the same underlying Email Service — the difference is how you access it.

If your application is NOT running on Cloudflare Workers, use the [REST API](rest-api.md) instead.

## Table of Contents

- [Workers Binding API](#workers-binding-api)
- [send() Method](#send-method)
- [sendBatch() Method](#sendbatch-method)
- [Attachments](#attachments)
- [Custom Headers](#custom-headers)
- [React Email Integration](#react-email-integration)
- [Agents SDK Email](#agents-sdk-email)
- [Error Handling](#error-handling)
- [Restricted Bindings](#restricted-bindings)

## Workers Binding API

The `send_email` binding gives your Worker direct access to Email Service. No API keys, no secrets — authentication is handled by the binding itself. This is the simplest and most secure way to send email from Cloudflare.

### Configuration

```jsonc
// wrangler.jsonc
{
  "send_email": [
    {
      "name": "EMAIL"
    }
  ]
}
```

For local development, add `"remote": true` to the binding so your Worker runs locally but sends real emails via the deployed Email Service:

```jsonc
// wrangler.jsonc — local development with remote binding
{
  "send_email": [
    {
      "name": "EMAIL",
      "remote": true
    }
  ]
}
```

Then run `npx wrangler dev` as normal. Your Worker code executes locally, but email sends are proxied to Cloudflare. Remove `"remote": true` before deploying to production (deployed Workers connect to Email Service automatically).

### Env Interface

Run `npx wrangler types` to auto-generate the `Env` interface from your `wrangler.jsonc`. This picks up the `send_email` binding and any other bindings you've configured:

```bash
npx wrangler types
```

This generates a `.d.ts` file (typically `worker-configuration.d.ts`) with a typed `Env` including your `EMAIL` binding. Use this instead of manually defining the interface — it stays in sync with your config automatically.

### TypeScript Interfaces

These are the actual types from `@cloudflare/workers-types`. Run `npx wrangler types` to generate them for your project.

```typescript
// The binding interface — generated as `SendEmail` by `wrangler types`
interface SendEmail {
  // Overload 1: raw EmailMessage (legacy MIME API — see Legacy section below)
  send(message: EmailMessage): Promise<EmailSendResult>;

  // Overload 2: EmailMessageBuilder (recommended)
  send(builder: EmailMessageBuilder): Promise<EmailSendResult>;
}

// Structured email builder (recommended)
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
  headers?: { [key: string]: string };  // See headers reference
}

interface Attachment {
  content: string | ArrayBuffer;        // Base64 string or binary content
  filename: string;
  type: string;                         // MIME type
  disposition: "attachment" | "inline";
  contentId?: string;                   // Required for inline attachments
}

interface EmailSendResult {
  messageId: string;                    // Unique email ID
}

// Errors are thrown as standard Error objects with a `code` property
// try { await env.EMAIL.send(...) } catch (e) { console.log(e.code, e.message) }
```

Key points:
- The binding type is `SendEmail` (not `EmailBinding`). `wrangler types` generates `env.EMAIL` as `SendEmail`.
- `send()` returns `EmailSendResult` with just `messageId` — there is no `success` boolean on the result. Failures throw errors with `.code` and `.message` properties.
- `from` accepts either a plain string (`"user@domain.com"`) or an object with `email` and `name`.
- **Workers binding uses `email` key** in the from object (not `address` — that's the REST API).
- `EmailAttachment.content` accepts `string` (base64) or `ArrayBuffer` — you can pass raw binary data directly, not just base64 strings.

## send() Method

Send a single email. This is the most common operation.

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const response = await env.EMAIL.send({
      to: "user@example.com",
      from: { email: "welcome@yourdomain.com", name: "My App" },
      subject: "Welcome to our service!",
      html: "<h1>Welcome!</h1><p>Thanks for signing up.</p>",
      text: "Welcome! Thanks for signing up.",
    });

    return new Response(`Sent: ${response.messageId}`);
  },
} satisfies ExportedHandler<Env>;
```

### Multiple Recipients

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

The combined total of `to` + `cc` + `bcc` cannot exceed 50 recipients. For larger sends, use `sendBatch()` to send individualized emails.

## sendBatch() Method

Send multiple distinct emails in a single request. Each email is independently validated — if one fails, the others still send.

```typescript
const subscribers = [
  { email: "alice@example.com", name: "Alice", plan: "Pro" },
  { email: "bob@example.com", name: "Bob", plan: "Business" },
];

const emails = subscribers.map(sub => ({
  to: sub.email,
  from: { email: "updates@yourdomain.com", name: "Your App" },
  subject: `Your ${sub.plan} plan update`,
  html: `<h1>Hi ${sub.name}!</h1><p>Here's your ${sub.plan} plan update.</p>`,
  text: `Hi ${sub.name}! Here's your ${sub.plan} plan update.`,
}));

const batchResponse = await env.EMAIL.sendBatch(emails);

// Always check individual results — partial failures are possible
let sent = 0, failed = 0;
batchResponse.results.forEach((result, i) => {
  if (result.success) {
    sent++;
  } else {
    failed++;
    console.error(`Email ${i} failed: ${result.error.code} - ${result.error.message}`);
  }
});
```

Batch sends are for individualized emails to different recipients. If you need to send the same email to 50+ people, loop over `send()` or chunk into batches.

## Attachments

### File Attachment

```typescript
const response = await env.EMAIL.send({
  to: "customer@example.com",
  from: "invoices@yourdomain.com",
  subject: "Your Invoice",
  html: "<h1>Invoice attached</h1><p>Please find your invoice attached.</p>",
  text: "Invoice attached. Please find your invoice attached.",
  attachments: [
    {
      content: "JVBERi0xLjQKJeLjz9MK...", // Base64-encoded PDF
      filename: "invoice-12345.pdf",
      type: "application/pdf",
      disposition: "attachment",
    },
  ],
});
```

### Inline Image

Reference inline images in HTML using `cid:<contentId>`:

```typescript
const response = await env.EMAIL.send({
  to: "user@example.com",
  from: "marketing@yourdomain.com",
  subject: "New Product Launch",
  html: `
    <h1>New Product</h1>
    <img src="cid:product-hero" alt="New Product" />
    <p>Check it out!</p>
  `,
  text: "New Product - Check it out!",
  attachments: [
    {
      content: "iVBORw0KGgoAAAANSUhEUgAA...", // Base64-encoded image
      filename: "product.png",
      type: "image/png",
      disposition: "inline",
      contentId: "product-hero",
    },
  ],
});
```

**Size limit:** Total email content (body + attachments) cannot exceed 25 MB. Base64 encoding adds ~33% overhead, so a 15 MB file becomes ~20 MB encoded.

## Custom Headers

Set custom headers for email threading, list management, or tracking. Only whitelisted headers are allowed — platform-controlled headers like `From` and `To` must be set via the API fields.

```typescript
const response = await env.EMAIL.send({
  to: "user@example.com",
  from: "notifications@yourdomain.com",
  subject: "Your weekly digest",
  html: "<h1>Weekly Digest</h1><p>Here's what happened this week.</p>",
  text: "Weekly Digest - Here's what happened this week.",
  headers: {
    // Threading — group related emails in the recipient's inbox
    "In-Reply-To": "<original-message-id@yourdomain.com>",
    "References": "<original-message-id@yourdomain.com>",

    // List management — required for recurring emails (helps with deliverability)
    "List-Unsubscribe": "<https://yourdomain.com/unsubscribe?id=abc123>",
    "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",

    // Custom tracking
    "X-Campaign-ID": "weekly-digest-2026-03",
  },
});
```

Limits: max 20 custom headers, each header name max 100 bytes, each value max 2,048 bytes, total headers max 16 KB.

## React Email Integration

[React Email](https://react.email/) lets you build HTML emails with React components. Render the template to HTML, then pass it to `send()`.

```bash
npm install @react-email/render @react-email/components
```

```tsx
// templates/welcome.tsx
import { Html, Head, Body, Container, Heading, Text, Button } from "@react-email/components";

export function WelcomeEmail({ name, confirmUrl }: { name: string; confirmUrl: string }) {
  return (
    <Html>
      <Head />
      <Body style={{ fontFamily: "sans-serif" }}>
        <Container>
          <Heading>Welcome, {name}!</Heading>
          <Text>Thanks for signing up. Confirm your email to get started.</Text>
          <Button href={confirmUrl}>Confirm Email</Button>
        </Container>
      </Body>
    </Html>
  );
}
```

```tsx
// src/index.tsx
import { render } from "@react-email/render";
import { WelcomeEmail } from "../templates/welcome";

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const html = await render(
      <WelcomeEmail name="Alice" confirmUrl="https://yourdomain.com/confirm/abc123" />
    );
    const text = await render(
      <WelcomeEmail name="Alice" confirmUrl="https://yourdomain.com/confirm/abc123" />,
      { plainText: true }
    );

    await env.EMAIL.send({
      to: "alice@example.com",
      from: { email: "welcome@yourdomain.com", name: "My App" },
      subject: "Welcome to My App!",
      html,
      text,
    });

    return new Response("Welcome email sent");
  },
} satisfies ExportedHandler<Env>;
```

## Agents SDK Email

The Cloudflare Agents SDK provides built-in email handling for AI agents. Agents can receive emails, process them, and reply — all within a stateful Durable Object.

### Wrangler Configuration

```jsonc
{
  "durable_objects": {
    "bindings": [{ "name": "EmailAgent", "class_name": "EmailAgent" }]
  },
  "migrations": [{ "tag": "v1", "new_sqlite_classes": ["EmailAgent"] }],
  "send_email": [
    {
      "name": "EMAIL",
      "destination_address": "reply@yourdomain.com"
    }
  ]
}
```

The `destination_address` restricts the binding so replies can only go to a specific address. The Agents SDK uses this binding internally when you call `this.replyToEmail()` — you don't call `env.EMAIL.send()` directly from agent code.

### Basic Email Agent

```typescript
import { Agent } from "agents";
import { type AgentEmail } from "agents/email";
import PostalMime from "postal-mime";

export class EmailAgent extends Agent<Env, State> {
  async onEmail(email: AgentEmail) {
    const parsed = await PostalMime.parse(await email.getRaw());

    console.log("From:", email.from);
    console.log("Subject:", parsed.subject);
    console.log("Body:", parsed.text);

    await this.replyToEmail(email, {
      fromName: "My Agent",
      subject: `Re: ${parsed.subject}`,
      body: "Thanks for your email! I'll look into this.",
    });
  }
}
```

### Email Routing to Agents

Route incoming emails to agent instances using resolvers. The resolver determines which agent class and instance handles each email.

```typescript
import { routeAgentRequest, routeAgentEmail } from "agents";
import { createAddressBasedEmailResolver } from "agents/email";

export default {
  async email(message, env) {
    await routeAgentEmail(message, env, {
      // Routes based on recipient: support@example.com -> EmailAgent instance "support"
      resolver: createAddressBasedEmailResolver("EmailAgent"),
    });
  },

  async fetch(request, env) {
    return routeAgentRequest(request, env) ?? new Response("Not found", { status: 404 });
  },
};
```

### Resolver Types

| Resolver | Routing Logic | Use Case |
|----------|--------------|----------|
| `createAddressBasedEmailResolver("Agent")` | Recipient local part becomes instance name | Multi-tenant: each address gets its own agent |
| `createSecureReplyEmailResolver(secret)` | Verifies HMAC-SHA256 signed reply headers | Secure reply chains that can't be spoofed |
| `createCatchAllEmailResolver("Agent", "default")` | All emails go to one instance | Single shared agent inbox |

### Combining Resolvers

A common pattern is to try secure reply first (for ongoing conversations), then fall back to address-based routing (for new emails):

```typescript
import {
  createSecureReplyEmailResolver,
  createAddressBasedEmailResolver,
} from "agents/email";

async email(message, env) {
  const secureReply = createSecureReplyEmailResolver(env.EMAIL_SECRET);
  const addressBased = createAddressBasedEmailResolver("EmailAgent");

  await routeAgentEmail(message, env, {
    resolver: async (email, env) => {
      const result = await secureReply(email, env);
      if (result) return result;
      return addressBased(email, env);
    },
  });
}
```

### Secure Reply Signing

When replying from an agent, sign the outbound email so replies route back to the correct agent instance:

```typescript
await this.replyToEmail(email, {
  fromName: "My Agent",
  body: "Here's what I found...",
  secret: this.env.EMAIL_SECRET, // Signs headers for secure reply routing
});
```

### Skip Auto-Replies

Avoid infinite loops by detecting vacation responders and out-of-office messages:

```typescript
import { isAutoReplyEmail } from "agents/email";

async onEmail(email: AgentEmail) {
  if (isAutoReplyEmail(email.headers)) {
    return; // Don't respond to auto-replies
  }
  // Process email...
}
```

## Legacy EmailMessage API

The existing `EmailMessage` API remains supported for backward compatibility. This uses raw MIME messages via `mimetext` or similar libraries. The `EmailMessageBuilder` approach above is recommended for new code.

```typescript
import { EmailMessage } from "cloudflare:email";
import { createMimeMessage } from "mimetext";

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const msg = createMimeMessage();
    msg.setSender({ name: "Sender", addr: "sender@yourdomain.com" });
    msg.setRecipient("recipient@example.com");
    msg.setSubject("Legacy Email");
    msg.addMessage({
      contentType: "text/html",
      data: "<h1>Hello from legacy API</h1>",
    });

    const message = new EmailMessage(
      "sender@yourdomain.com",
      "recipient@example.com",
      msg.asRaw(),
    );

    await env.EMAIL.send(message);
    return new Response("Legacy email sent");
  },
};
```

Requires `mimetext` (`npm install mimetext`) and `"nodejs_compat"` in compatibility flags.

## Error Handling

### Single Send

`send()` throws errors with `.code` and `.message` properties on failure:

```typescript
try {
  const response = await env.EMAIL.send({
    to: "user@example.com",
    from: "noreply@yourdomain.com",
    subject: "Test",
    text: "Hello!",
  });
  console.log("Sent:", response.messageId);
} catch (error) {
  // error.code is one of the E_* error codes
  console.error(`Failed: ${error.code} - ${error.message}`);

  if (error.code === "E_RATE_LIMIT_EXCEEDED") {
    // Retry with backoff
  } else if (error.code === "E_SENDER_NOT_VERIFIED") {
    // Domain not onboarded — fix configuration, don't retry
  }
}
```

### Batch Send

`sendBatch()` returns results for each email. The batch itself succeeds even if individual emails fail — you must check each result:

```typescript
const batchResponse = await env.EMAIL.sendBatch(emails);

const failures = batchResponse.results
  .map((r, i) => ({ ...r, index: i }))
  .filter(r => !r.success);

if (failures.length > 0) {
  console.error(`${failures.length} emails failed:`);
  failures.forEach(f => console.error(`  [${f.index}] ${f.error.code}: ${f.error.message}`));
}
```

A binding-level error (like `E_BATCH_TOO_LARGE`) throws instead of returning results. Use try/catch around `sendBatch()` to handle both cases.

## Restricted Bindings

For security, you can restrict which `from` addresses a binding is allowed to use. This prevents a compromised Worker from sending as arbitrary addresses on your domain.

```jsonc
{
  "send_email": [
    {
      "name": "RESTRICTED_EMAIL",
      "allowed_sender_addresses": [
        "noreply@yourdomain.com",
        "support@yourdomain.com"
      ]
    }
  ]
}
```

If you send from an address not in the list, the send fails with a validation error. Use this in production — especially if multiple Workers share a domain — to limit blast radius.
