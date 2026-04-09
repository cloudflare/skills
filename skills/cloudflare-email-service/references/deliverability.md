# Email Deliverability & Best Practices

This reference covers what Cloudflare Email Service handles for you automatically, what you're responsible for, and how to write emails that land in inboxes.

## Table of Contents

- [What Cloudflare Handles For You](#what-cloudflare-handles-for-you)
- [What You're Responsible For](#what-youre-responsible-for)
- [Bounce Handling](#bounce-handling)
- [Writing Good Transactional Emails](#writing-good-transactional-emails)
- [Metrics to Watch](#metrics-to-watch)
- [Compliance Basics](#compliance-basics)
- [Testing Before Production](#testing-before-production)

## What Cloudflare Handles For You

When you onboard a domain to Email Service, Cloudflare automatically configures the three pillars of email authentication. You don't need to manually create DNS records or manage signing keys.

**SPF (Sender Policy Framework)** — TXT records are added to your zone authorizing Cloudflare's sending infrastructure. Receiving servers check this to verify the email came from an authorized sender.

**DKIM (DomainKeys Identified Mail)** — CNAME records are added that point to Cloudflare's DKIM signing keys. Every outbound email gets a cryptographic signature proving it hasn't been tampered with in transit.

**DMARC** — If you don't already have a DMARC record, consider adding one. Cloudflare handles SPF and DKIM, but DMARC is a policy you set that tells receiving servers what to do when authentication fails. A reasonable starting point:

```
v=DMARC1; p=quarantine; rua=mailto:dmarc-reports@yourdomain.com
```

Cloudflare also manages:
- **IP reputation** — Shared sending infrastructure optimized for deliverability
- **Soft bounce retries** — Automatic exponential backoff for temporary failures
- **Suppression lists** — Hard-bounced addresses are automatically blocked from future sends
- **Feedback loops** — ISP complaint signals are processed and acted on

Because all of this is handled at the platform level, you start with a strong deliverability foundation without any manual configuration.

## What You're Responsible For

Authentication gets your emails past the door. Everything below determines whether they land in the inbox or the spam folder.

### Content Quality

| Do | Don't |
|----|-------|
| Include both HTML and plain text versions | Send HTML-only emails (hurts accessibility and spam scores) |
| Use a recognizable sender name: `{ email: "noreply@app.com", name: "My App" }` | Send from a bare address with no display name |
| Write descriptive, honest subject lines | Use clickbait, ALL CAPS, or excessive punctuation!!! |
| Keep a reasonable text-to-image ratio | Use a single large image as the entire email body |
| Include `List-Unsubscribe` headers for recurring emails | Omit unsubscribe for emails that repeat |
| Use full URLs from your domain | Use URL shorteners (bit.ly, etc.) — spam filters distrust them |

### List Quality

- Validate email addresses before sending (catch typos, disposable domains)
- Implement double opt-in for subscriptions
- Remove hard-bounced addresses immediately (Cloudflare auto-suppresses these, but clean your own lists too)
- Honor unsubscribe requests promptly

### Transactional Only

### Transactional vs Marketing Email

Email Service is for **transactional email only**. Understanding the difference matters because they have different legal requirements, deliverability characteristics, and sending infrastructure.

**Transactional email** is triggered by a specific user action. The recipient expects it because they did something that caused it. Examples:

- Welcome email after signing up
- Password reset link after clicking "Forgot password"
- Order confirmation after a purchase
- Magic link after requesting passwordless login
- Two-factor authentication code
- Shipping notification when an order ships
- Account alert (suspicious login, billing issue)
- Invoice or receipt after payment

**Marketing / broadcast email** is sent at the sender's initiative, not triggered by a specific user action. Examples:

- Weekly newsletter
- Product announcement to all users
- Promotional discount campaign
- Re-engagement email to inactive users
- Event invitation blast

**Why it matters for Email Service:** Transactional and marketing emails have fundamentally different sending patterns. Transactional emails are low-volume, high-priority, and time-sensitive (a password reset that arrives 10 minutes late is useless). Marketing emails are high-volume, lower-priority, and tolerant of delays. Mixing them on the same infrastructure risks marketing complaints dragging down transactional deliverability. Email Service is optimized for the transactional pattern — fast delivery, high inbox placement, strict reputation management.

Marketing emails, newsletters, and bulk campaigns are not permitted on Email Service. Use a dedicated marketing email platform for those.

## Bounce Handling

### Hard Bounces

Permanent failures — the address doesn't exist, the domain doesn't exist, or the recipient server permanently blocks you. Hard bounces are **never retried**. The address is automatically added to the suppression list, preventing future sends.

Sending to a suppressed address returns `E_RECIPIENT_SUPPRESSED` instead of attempting delivery.

### Soft Bounces

Temporary failures — mailbox full, server temporarily down, greylisting. Cloudflare automatically retries with exponential backoff over an extended period. You don't need to implement retry logic for these.

## Suppression Lists

There are **two types** of suppression lists:

### Global Suppression List (Managed by Cloudflare)

Cloudflare maintains a global list of problematic addresses. Email Service will not send to addresses on this list to preserve the reputation of the shared IP pool. Addresses are added for:
- **Hard bounces** — permanently invalid addresses
- **Repeated soft bounces** — addresses that consistently fail delivery
- **Manual additions** — addresses Cloudflare specifically blocks
- **Compliance blocks** — legal or regulatory requirements

### Account Suppression List (Your Account)

Cloudflare also manages suppressions specific to your account:
- **Spam complaints** — recipients who mark your emails as spam. Cloudflare integrates with Postmasters to receive complaints and automatically suppresses these addresses.
- **Manual additions** — you can add or remove addresses via the Dashboard.

Removal of auto-suppressed addresses (from spam complaints) is limited to prevent abuse.

### Best Practices for Suppression

- Review suppression lists monthly in the Dashboard
- Remove temporary suppressions that have expired
- Identify patterns in suppressed addresses
- Update email validation rules based on common issues
- **Do not** try to work around suppressions — they protect your sender reputation

## Writing Good Transactional Emails

Transactional emails have higher open rates than any other email type because recipients expect them. Respect that expectation.

**Welcome / verification emails:** Confirm what they did ("You signed up for..."), set expectations, one clear call-to-action.

**Password resets:** State what happened, include the reset link with a visible button, add a "didn't request this?" fallback, show the expiration time.

**Order confirmations:** Order number prominently displayed, item summary, estimated delivery, tracking link.

**Notifications / alerts:** Clear actionable subject line ("Your deploy succeeded" not "Notification"), relevant details without overwhelming, link to the relevant page.

For building HTML email templates, use [React Email](https://react.email/) — it handles cross-client compatibility. See [sending.md](sending.md#react-email-integration) for integration with Email Service.

## Metrics to Watch

Monitor these in the Cloudflare Dashboard. Gmail specifically requires senders to maintain a complaint rate below 0.1% — exceeding 0.3% can result in permanent spam classification.

| Metric | Target | If Out of Range |
|--------|--------|-----------------|
| Delivery rate | > 95% | Check for invalid addresses; verify DNS records are intact |
| Hard bounce rate | < 2% | Clean your email list; investigate the source of bad addresses |
| Complaint rate | < 0.1% | Make unsubscribe easier; stop sending email people don't want |

## Compliance Basics

For transactional email (which is what Email Service is designed for), you're largely in compliance if you:

1. **Only send emails users expect** — triggered by their actions, not by your marketing calendar
2. **Don't disguise marketing as transactional** — adding promotional content to a receipt email violates CAN-SPAM
3. **Include accurate sender information** — real company name, valid reply address
4. **Provide a way to contact you** — physical address in footer for CAN-SPAM, data contact info for GDPR

**CAN-SPAM (US):** Transactional emails are largely exempt, but must not contain false header information. If you add any promotional content, the full requirements apply (unsubscribe link, physical address, honor opt-outs within 10 days).

**GDPR (EU):** Transactional emails sent as part of a service relationship fall under "contractual necessity." You still need to honor data deletion requests and be transparent about data use.

**CASL (Canada):** Implied consent exists for existing business relationships. Transactional emails are exempt.

## Testing Before Production

1. **Test across email clients** — Gmail, Outlook, Yahoo, Apple Mail all render differently
3. **Check your DNS** — run `npx wrangler email sending dns get yourdomain.com` to verify SPF and DKIM records
4. **Check spam score** — send a test to [mail-tester.com](https://www.mail-tester.com/) and aim for 9/10+
5. **Send small batches first** — monitor delivery metrics in the Dashboard before scaling up
