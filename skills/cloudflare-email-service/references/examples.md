# Full-Stack Email Patterns

Real-world implementation patterns that combine sending, receiving, and Cloudflare platform services. Each example is a complete, working pattern you can adapt.

For email content best practices (avoiding spam filters, proper structure, compliance), see [deliverability.md](deliverability.md).

## Table of Contents

- [User Signup Flow](#user-signup-flow)
- [Magic Link Authentication](#magic-link-authentication)
- [Support Inbox with Auto-Reply](#support-inbox-with-auto-reply)
- [AI Email Agent](#ai-email-agent)
- [Invoice Processing Pipeline](#invoice-processing-pipeline)
- [Email Notifications via Queues](#email-notifications-via-queues)
- [Email Metadata Storage with D1](#email-metadata-storage-with-d1)

## User Signup Flow

A classic pattern: user signs up, receives a verification email, clicks to confirm.

```jsonc
// wrangler.jsonc
{
  "name": "signup-service",
  "main": "src/index.ts",
  "compatibility_date": "2025-01-01",
  "send_email": [{ "name": "EMAIL" }],
  "kv_namespaces": [{ "binding": "TOKENS", "id": "your-kv-namespace-id" }]
}
```

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === "/signup" && request.method === "POST") {
      const { email, name } = await request.json();

      // Generate a verification token
      const token = crypto.randomUUID();
      await env.TOKENS.put(token, JSON.stringify({ email, name }), {
        expirationTtl: 3600, // 1 hour
      });

      const verifyUrl = `${url.origin}/verify?token=${token}`;

      await env.EMAIL.send({
        to: email,
        from: { email: "welcome@yourdomain.com", name: "My App" },
        subject: "Verify your email",
        html: `
          <h1>Welcome, ${name}!</h1>
          <p>Click the button below to verify your email address.</p>
          <a href="${verifyUrl}" style="display:inline-block;padding:12px 24px;background:#0070f3;color:#fff;text-decoration:none;border-radius:6px;">
            Verify Email
          </a>
          <p style="color:#666;font-size:14px;">This link expires in 1 hour.</p>
        `,
        text: `Welcome, ${name}! Verify your email: ${verifyUrl}`,
      });

      return Response.json({ message: "Verification email sent" });
    }

    if (url.pathname === "/verify") {
      const token = url.searchParams.get("token");
      if (!token) return new Response("Missing token", { status: 400 });

      const data = await env.TOKENS.get(token, "json");
      if (!data) return new Response("Invalid or expired token", { status: 400 });

      // Token is valid — mark user as verified, delete the token
      await env.TOKENS.delete(token);

      return new Response(`Email verified for ${data.email}!`);
    }

    return new Response("Not found", { status: 404 });
  },
} satisfies ExportedHandler<Env>;
```

## Magic Link Authentication

Passwordless login: send a one-time link that logs the user in when clicked.

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === "/login" && request.method === "POST") {
      const { email } = await request.json();

      // Generate a short-lived, single-use token
      const token = crypto.randomUUID();
      await env.TOKENS.put(`magic:${token}`, email, {
        expirationTtl: 600, // 10 minutes
      });

      const magicUrl = `${url.origin}/auth?token=${token}`;

      await env.EMAIL.send({
        to: email,
        from: { email: "login@yourdomain.com", name: "My App" },
        subject: "Your login link",
        html: `
          <h1>Sign in to My App</h1>
          <p>Click below to sign in. This link expires in 10 minutes and can only be used once.</p>
          <a href="${magicUrl}" style="display:inline-block;padding:12px 24px;background:#0070f3;color:#fff;text-decoration:none;border-radius:6px;">
            Sign In
          </a>
          <p style="color:#666;font-size:14px;">If you didn't request this, you can safely ignore this email.</p>
        `,
        text: `Sign in to My App: ${magicUrl}\n\nThis link expires in 10 minutes. If you didn't request this, ignore this email.`,
      });

      return Response.json({ message: "Login link sent" });
    }

    if (url.pathname === "/auth") {
      const token = url.searchParams.get("token");
      if (!token) return new Response("Missing token", { status: 400 });

      const email = await env.TOKENS.get(`magic:${token}`);
      if (!email) return new Response("Invalid or expired link", { status: 400 });

      // Single-use: delete immediately
      await env.TOKENS.delete(`magic:${token}`);

      // Create session, set cookie, redirect — your auth logic here
      return new Response(`Logged in as ${email}`);
    }

    return new Response("Not found", { status: 404 });
  },
} satisfies ExportedHandler<Env>;
```

## Support Inbox with Auto-Reply

Receive support emails, auto-reply with a ticket number, and forward to the team. This demonstrates the unified send + receive pattern.

```jsonc
// wrangler.jsonc
{
  "name": "support-inbox",
  "main": "src/index.ts",
  "compatibility_date": "2025-01-01",
  "send_email": [{ "name": "EMAIL" }]
}
```

```typescript
import PostalMime from "postal-mime";

export default {
  async email(message, env, ctx): Promise<void> {
    const raw = await new Response(message.raw).arrayBuffer();
    const parsed = await PostalMime.parse(raw);

    const ticketId = `TK-${Date.now().toString(36).toUpperCase()}`;

    // Auto-reply with ticket number
    await env.EMAIL.send({
      to: message.from,
      from: { email: "support@yourdomain.com", name: "Support Team" },
      subject: `[${ticketId}] Re: ${parsed.subject}`,
      html: `
        <h2>We received your message</h2>
        <p>Your ticket number is <strong>${ticketId}</strong>.</p>
        <p>A member of our team will respond within 24 hours.</p>
        <hr>
        <p style="color:#666;font-size:14px;">Original message: ${parsed.subject}</p>
      `,
      text: `We received your message. Your ticket number is ${ticketId}. We'll respond within 24 hours.`,
      headers: {
        "In-Reply-To": message.headers.get("Message-ID") || "",
      },
    });

    // Forward to the support team
    await message.forward("team@company.com");
  },

  async fetch(request: Request, env: Env): Promise<Response> {
    return new Response("Support inbox running");
  },
} satisfies ExportedHandler<Env>;
```

## AI Email Agent

Receive emails, classify them with Workers AI, and respond intelligently. This pattern uses the Agents SDK for stateful processing.

```jsonc
// wrangler.jsonc
{
  "name": "ai-email-agent",
  "main": "src/index.ts",
  "compatibility_date": "2025-01-01",
  "compatibility_flags": ["nodejs_compat"],
  "ai": { "binding": "AI" },
  "durable_objects": {
    "bindings": [{ "name": "EMAIL_AGENT", "class_name": "EmailAgent" }]
  },
  "migrations": [{ "tag": "v1", "new_sqlite_classes": ["EmailAgent"] }],
  "send_email": [{ "name": "EMAIL" }]
}
```

```typescript
import { Agent, routeAgentRequest, routeAgentEmail } from "agents";
import { type AgentEmail, createAddressBasedEmailResolver, isAutoReplyEmail } from "agents/email";
import PostalMime from "postal-mime";

export class EmailAgent extends Agent<Env, State> {
  async onEmail(email: AgentEmail) {
    // Skip auto-replies to avoid infinite loops
    if (isAutoReplyEmail(email.headers)) return;

    const parsed = await PostalMime.parse(await email.getRaw());

    // Classify the email using Workers AI
    const classification = await this.env.AI.run("@cf/meta/llama-3.1-8b-instruct", {
      messages: [{
        role: "user",
        content: `Classify this email as one of: question, bug_report, feature_request, thank_you, spam.
Subject: ${parsed.subject}
Body: ${parsed.text?.substring(0, 1000)}

Respond with ONLY the category name.`,
      }],
    });

    const category = classification.response?.trim().toLowerCase() || "unknown";

    if (category === "spam") {
      return; // Drop silently
    }

    // Generate a contextual response
    const response = await this.env.AI.run("@cf/meta/llama-3.1-8b-instruct", {
      messages: [{
        role: "system",
        content: "You are a helpful support agent. Write a brief, professional email reply.",
      }, {
        role: "user",
        content: `Reply to this ${category} email:
Subject: ${parsed.subject}
Body: ${parsed.text?.substring(0, 1000)}`,
      }],
    });

    await this.replyToEmail(email, {
      fromName: "AI Support Agent",
      subject: `Re: ${parsed.subject}`,
      body: response.response || "Thanks for your message! A human team member will follow up shortly.",
    });
  }
}

export default {
  async email(message, env) {
    await routeAgentEmail(message, env, {
      resolver: createAddressBasedEmailResolver("EmailAgent"),
    });
  },
  async fetch(request, env) {
    return routeAgentRequest(request, env) ?? new Response("Not found", { status: 404 });
  },
};
```

## Invoice Processing Pipeline

Receive invoices via email, extract PDF attachments, store in R2, and send a confirmation.

```jsonc
// wrangler.jsonc
{
  "name": "invoice-processor",
  "main": "src/index.ts",
  "compatibility_date": "2025-01-01",
  "send_email": [{ "name": "EMAIL" }],
  "r2_buckets": [{ "binding": "INVOICES", "bucket_name": "invoices" }]
}
```

```typescript
import PostalMime from "postal-mime";

export default {
  async email(message, env, ctx): Promise<void> {
    const raw = await new Response(message.raw).arrayBuffer();
    const parsed = await PostalMime.parse(raw);

    const pdfAttachments = parsed.attachments.filter(
      a => a.mimeType === "application/pdf"
    );

    if (pdfAttachments.length === 0) {
      await env.EMAIL.send({
        to: message.from,
      from: { email: "invoices@yourdomain.com", name: "Invoice Processing" },
      subject: `Re: ${parsed.subject}`,
      text: "No PDF attachment found. Please resend with the invoice attached as a PDF.",
      });
      return;
    }

    // Store each PDF in R2
    const storedFiles = [];
    for (const pdf of pdfAttachments) {
      const key = `${new Date().toISOString().slice(0, 10)}/${message.from}/${pdf.filename}`;
      await env.INVOICES.put(key, pdf.content, {
        httpMetadata: { contentType: "application/pdf" },
        customMetadata: {
          from: message.from,
          subject: parsed.subject || "",
          receivedAt: new Date().toISOString(),
        },
      });
      storedFiles.push(pdf.filename);
    }

    // Confirm receipt
    await env.EMAIL.send({
      to: message.from,
      from: { email: "invoices@yourdomain.com", name: "Invoice Processing" },
      subject: `Re: ${parsed.subject}`,
      html: `
        <h2>Invoice received</h2>
        <p>We've received and stored the following files:</p>
        <ul>${storedFiles.map(f => `<li>${f}</li>`).join("")}</ul>
        <p>These will be processed within 1 business day.</p>
      `,
      text: `Invoice received. Files stored: ${storedFiles.join(", ")}. Processing within 1 business day.`,
    });
  },
} satisfies ExportedHandler<Env>;
```

## Email Notifications via Queues

For applications where email sending shouldn't block the main request (e.g., API responses), push email tasks to a Queue and send asynchronously.

```jsonc
// wrangler.jsonc
{
  "name": "notification-service",
  "main": "src/index.ts",
  "compatibility_date": "2025-01-01",
  "send_email": [{ "name": "EMAIL" }],
  "queues": {
    "producers": [{ "binding": "EMAIL_QUEUE", "queue": "email-notifications" }],
    "consumers": [{ "queue": "email-notifications" }]
  }
}
```

```typescript
interface EmailTask {
  to: string;
  subject: string;
  html: string;
  text: string;
}

export default {
  // API handler — queues the email and returns immediately
  async fetch(request: Request, env: Env): Promise<Response> {
    if (request.method === "POST" && new URL(request.url).pathname === "/notify") {
      const { userId, event } = await request.json();

      // Queue the email — returns instantly, doesn't block the response
      await env.EMAIL_QUEUE.send({
        to: `${userId}@example.com`,
        subject: `Event: ${event}`,
        html: `<p>Event <strong>${event}</strong> occurred.</p>`,
        text: `Event ${event} occurred.`,
      } satisfies EmailTask);

      return Response.json({ queued: true });
    }
    return new Response("Not found", { status: 404 });
  },

  // Queue consumer — sends emails in the background
  async queue(batch: MessageBatch<EmailTask>, env: Env): Promise<void> {
    for (const message of batch.messages) {
      try {
        await env.EMAIL.send({
          to: message.body.to,
          from: { email: "notifications@yourdomain.com", name: "Notifications" },
          subject: message.body.subject,
          html: message.body.html,
          text: message.body.text,
        });
        message.ack();
      } catch (error) {
        console.error(`Failed to send to ${message.body.to}:`, error);
        message.retry(); // Will be retried by the queue
      }
    }
  },
} satisfies ExportedHandler<Env>;
```

This pattern is valuable because:
- API responses are fast (no waiting for email delivery)
- Failed emails are automatically retried by the queue
- You can batch process emails efficiently
- Email sending doesn't affect your application's latency

## Email Metadata Storage with D1

Track all sent emails in a D1 database for reporting, debugging, and audit trails.

```jsonc
// wrangler.jsonc
{
  "name": "email-tracker",
  "main": "src/index.ts",
  "compatibility_date": "2025-01-01",
  "send_email": [{ "name": "EMAIL" }],
  "d1_databases": [{ "binding": "DB", "database_name": "email-tracker", "database_id": "your-db-id" }]
}
```

```sql
-- Run with: npx wrangler d1 execute email-tracker --command "..."
CREATE TABLE IF NOT EXISTS sent_emails (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  message_id TEXT NOT NULL,
  recipient TEXT NOT NULL,
  subject TEXT NOT NULL,
  status TEXT DEFAULT 'sent',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

```typescript
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const { to, subject, html, text } = await request.json();

    try {
      const response = await env.EMAIL.send({
        to,
        from: "noreply@yourdomain.com",
        subject,
        html,
        text,
      });

      // Record the sent email
      await env.DB.prepare(
        "INSERT INTO sent_emails (message_id, recipient, subject, status) VALUES (?, ?, ?, ?)"
      ).bind(response.messageId, to, subject, "sent").run();

      return Response.json({ messageId: response.messageId });
    } catch (error) {
      // Record the failure
      await env.DB.prepare(
        "INSERT INTO sent_emails (message_id, recipient, subject, status) VALUES (?, ?, ?, ?)"
      ).bind("failed", to, subject, `error: ${error.code}`).run();

      return Response.json({ error: error.message }, { status: 500 });
    }
  },
} satisfies ExportedHandler<Env>;
```
