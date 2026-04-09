# Email Deliverability & Best Practices

For full details, see the [deliverability docs](https://developers.cloudflare.com/email-service/concepts/deliverability/) and [email authentication docs](https://developers.cloudflare.com/email-service/concepts/email-authentication/).

## What Cloudflare Handles

When you onboard a domain, Cloudflare auto-configures:

- **SPF** — TXT records authorizing Cloudflare's sending infrastructure
- **DKIM** — Records for cryptographic signing of outbound emails
- **IP reputation** — Managed sending infrastructure optimized for deliverability
- **Soft bounce retries** — Automatic exponential backoff for temporary failures
- **Suppression lists** — Hard-bounced addresses automatically blocked
- **Feedback loops** — ISP complaint signals processed and acted on

Consider adding a **DMARC** record if you don't have one: `v=DMARC1; p=quarantine; rua=mailto:dmarc-reports@yourdomain.com`

## Bounce Handling

**Hard bounces** — permanent failures (address doesn't exist, domain doesn't exist). Never retried. Address auto-added to suppression list. Sending to suppressed address returns `E_RECIPIENT_SUPPRESSED`.

**Soft bounces** — temporary failures (mailbox full, server down, greylisting). Cloudflare auto-retries with exponential backoff.

## Suppression Lists

Two types protect your sender reputation:

**Global list** (managed by Cloudflare) — hard bounces, repeated soft bounces, compliance blocks. Protects shared IP pool reputation.

**Account list** (your account) — spam complaints from recipients. Cloudflare integrates with Postmasters to auto-suppress. You can manually add/remove addresses in the Dashboard.

See the [suppressions docs](https://developers.cloudflare.com/email-service/concepts/suppressions/) for details.

## Your Responsibilities

### Content
- Include both HTML and plain text versions
- Use a recognizable sender name: `{ email: "noreply@app.com", name: "My App" }`
- Write honest subject lines — avoid ALL CAPS, excessive punctuation
- Include `List-Unsubscribe` headers for recurring emails
- Use full URLs from your domain — avoid URL shorteners

### List Quality
- Validate email addresses before sending
- Implement double opt-in for subscriptions
- Honor unsubscribe requests promptly

### Transactional Only
Email Service is for **transactional email** (triggered by user actions: signups, password resets, order confirmations). Marketing/bulk campaigns are not permitted — use a dedicated marketing platform.

## Metrics to Watch

| Metric | Target | If Out of Range |
|--------|--------|-----------------|
| Delivery rate | > 95% | Check for invalid addresses; verify DNS records |
| Hard bounce rate | < 2% | Clean your email list |
| Complaint rate | < 0.1% | Make unsubscribe easier; stop unwanted emails |
