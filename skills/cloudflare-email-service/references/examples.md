# Full-Stack Email Patterns

Working patterns combining sending, receiving, and Cloudflare platform services. For more examples, see the [Email Service examples docs](https://developers.cloudflare.com/email-service/examples/).

## User Signup Flow

```jsonc
// wrangler.jsonc
{
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
      const token = crypto.randomUUID();
      await env.TOKENS.put(token, JSON.stringify({ email, name }), { expirationTtl: 3600 });

      await env.EMAIL.send({
        to: email,
        from: { email: "welcome@yourdomain.com", name: "My App" },
        subject: "Verify your email",
        html: `<h1>Welcome, ${name}!</h1><a href="${url.origin}/verify?token=${token}">Verify Email</a>`,
        text: `Welcome, ${name}! Verify: ${url.origin}/verify?token=${token}`,
      });
      return Response.json({ message: "Verification email sent" });
    }

    if (url.pathname === "/verify") {
      const token = url.searchParams.get("token");
      const data = await env.TOKENS.get(token, "json");
      if (!data) return new Response("Invalid or expired token", { status: 400 });
      await env.TOKENS.delete(token);
      return new Response(`Email verified for ${data.email}!`);
    }

    return new Response("Not found", { status: 404 });
  },
} satisfies ExportedHandler<Env>;
```

## Support Inbox with Auto-Reply

Combined send + receive pattern:

```jsonc
// wrangler.jsonc
{ "send_email": [{ "name": "EMAIL" }] }
```

```typescript
export default {
  async email(message, env, ctx): Promise<void> {
    const ticketId = `TK-${Date.now().toString(36).toUpperCase()}`;

    await env.EMAIL.send({
      to: message.from,
      from: { email: "support@yourdomain.com", name: "Support Team" },
      subject: `[${ticketId}] Re: ${message.headers.get("subject") || ""}`,
      html: `<p>Your ticket number is <strong>${ticketId}</strong>. We'll respond within 24 hours.</p>`,
      text: `Your ticket number is ${ticketId}. We'll respond within 24 hours.`,
      headers: { "In-Reply-To": message.headers.get("Message-ID") || "" },
    });

    await message.forward("team@company.com");
  },
} satisfies ExportedHandler<Env>;
```

## Email Notifications via Queues

Non-blocking email sends — queue emails and process asynchronously:

```jsonc
// wrangler.jsonc
{
  "send_email": [{ "name": "EMAIL" }],
  "queues": {
    "producers": [{ "binding": "EMAIL_QUEUE", "queue": "email-notifications" }],
    "consumers": [{ "queue": "email-notifications" }]
  }
}
```

```typescript
interface EmailTask { to: string; subject: string; html: string; text: string; }

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const { userId, event } = await request.json();
    await env.EMAIL_QUEUE.send({
      to: `${userId}@example.com`,
      subject: `Event: ${event}`,
      html: `<p>Event <strong>${event}</strong> occurred.</p>`,
      text: `Event ${event} occurred.`,
    } satisfies EmailTask);
    return Response.json({ queued: true });
  },

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
        message.retry();
      }
    }
  },
} satisfies ExportedHandler<Env>;
```
