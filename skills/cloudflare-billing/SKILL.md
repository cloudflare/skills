---
name: cloudflare-billing
description: Debug Cloudflare billing for a confused customer — outstanding balances, why they're on FREE/PRO/BUSINESS, possible double charges, pending authorizations, which zones/products drive cost. Pulls subscriptions and billing history straight from the Cloudflare REST API and presents a friendly, plain-language summary the customer can act on. Load when a user asks why they were charged, what plan they're on, whether they have outstanding invoices, or asks for help reconciling a Cloudflare bill.
---

# Cloudflare Billing

A structured investigation playbook for making sense of a Cloudflare bill. Calls the Cloudflare REST API directly — no MCP server, no extra dependencies. The agent runs read-only `curl` requests with a scoped token and produces a single, plain-language summary the customer can act on.

Your knowledge of Cloudflare billing endpoints, plan names, and prices may be outdated. **Prefer retrieval over pre-training** — fetch the latest from the sources below before quoting specific numbers.

## Retrieval Sources

| Source | How to retrieve | Use for |
| --- | --- | --- |
| Cloudflare docs | `cloudflare-docs` search tool or `https://developers.cloudflare.com/billing/` | Plan names, pricing, billing FAQ |
| Cloudflare API reference | `https://developers.cloudflare.com/api/` | Subscription / billing-history endpoint contracts |
| Customer's dashboard | `https://dash.cloudflare.com/<account_id>/billing` | What the customer sees |

## Prerequisites

A Cloudflare API token with **`Account → Billing → Read`** (required). `Zone → Zone → Read` is optional and only needed for the per-zone subscription drill-down.

Create one at `https://dash.cloudflare.com/profile/api-tokens`. Have the user export it before you run anything:

```sh
export CLOUDFLARE_API_TOKEN=...
```

If the variable isn't set, tell the user how to create the token and stop — don't guess.

## API endpoints you'll call

All read-only `GET` requests against `https://api.cloudflare.com/client/v4`, with `Authorization: Bearer $CLOUDFLARE_API_TOKEN`.

| Purpose | Endpoint | When |
| --- | --- | --- |
| Account subscriptions | `GET /accounts/{account_id}/subscriptions` | Primary — the full plan picture per account |
| User subscriptions (fallback) | `GET /user/subscriptions` | When the user doesn't know their account ID |
| Billing history | `GET /user/billing/history?per_page=50` | Every charge, refund, proration with status |
| Zone subscription | `GET /zones/{zone_id}/subscription` | Only if drilling into one specific domain |

> **Note:** the billing-history endpoint is marked deprecated by Cloudflare but remains live as of 2026. No public replacement exposes per-product usage breakdowns (see edge cases below).

### Example calls

```sh
# Account subscriptions
curl -s "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/subscriptions" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" | jq '.result'

# User-level fallback (no account_id needed)
curl -s "https://api.cloudflare.com/client/v4/user/subscriptions" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" | jq '.result'

# Billing history
curl -s "https://api.cloudflare.com/client/v4/user/billing/history?per_page=50" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" | jq '.result'

# A specific zone's subscription
curl -s "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/subscription" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" | jq '.result'
```

## What to ask before running anything

At most **two** questions:

1. **Account ID?** (the 32-char hex from the dash URL, e.g. `dash.cloudflare.com/<account_id>/...`). If they don't know it, fall back to `GET /user/subscriptions`.
2. **Is there a specific charge or date that's confusing you?** Narrows the search if their history is long.

Don't keep asking. Often the data answers the question on its own — run the calls and *then* clarify if needed.

## Investigation order

### Step 1 — Subscriptions

Call `GET /accounts/{account_id}/subscriptions` (or `GET /user/subscriptions` as fallback). Group results into:

- **Account-scoped plans** — `rate_plan.scope === "account"`. Pay-as-you-go consumption plans (Workers Paid, R2 Paid, Log Explorer, Teams). Usually `frequency: "monthly"` and a small or $0 base fee plus usage.
- **Zone-scoped plans** — `rate_plan.scope === "zone"`. One per domain, fixed monthly: FREE ($0), PRO ($25), BUSINESS ($250), ENTERPRISE (custom). Identifiable by `zone.name`.

Interpret the `intent` field — it tells the customer *why* they're on a plan:

| intent | Plain-language meaning |
| --- | --- |
| `PAYGO` | You opted into a usage-based product (typical for Workers/R2) |
| `BULK_ZONE` | You upgraded this domain from the dashboard |
| `EMPLOYEE` | Cloudflare employee benefit plan |
| `CONTRACT` | Enterprise contract |

Note the `created_date` so you can say "you upgraded `example.com` to Business on 2024-08-07."

### Step 2 — Billing history

Call `GET /user/billing/history?per_page=50`. Walk each item:

| Signal | Plain-language meaning |
| --- | --- |
| `status: CLOSED` AND `amount_to_pay: 0` | Settled, nothing owed |
| `status: OPEN` OR `amount_to_pay > 0` | **Outstanding balance — surface prominently** |
| `status: PENDING` | Bank authorization in flight, not a real charge yet |
| `type: refund` or negative `amount` | Money returned |
| Two items with same `amount` within ~5 min on same `source` | **Flag as possible double charge** — ask user to verify against their bank/card statement |
| `source: stripe` | Charged via Stripe (Cloudflare's payment processor) |

`receipt_id` (e.g. `IN-65007205`) is the user-visible invoice number — always quote it when referring to a specific item, never the opaque `id` UUID.

### Step 3 — Reconcile

- Sum monthly **base fees** from zone subs (e.g. PRO $25 + BUSINESS $250 = $275 base/month).
- Sum **recent monthly totals** from history (group `occurred_at` by month, sum `amount`).
- If history > base by > ~10%, the difference is **usage on PAYGO plans** (Workers, R2). Point at the relevant `rate_plan.public_name`.
- If history < base in a recent month, mention possible **proration, credit, or partial-period billing** (often happens after plan changes or refunds).
- If the most recent invoice is `amount_to_pay > 0`, that's almost certainly what they're asking about. Lead with it.

## How to present the answer

Use this structure — markdown is fine. Translate IDs to human names everywhere (zone IDs → domains, sub IDs → plan public names, item IDs → receipt numbers).

```
## What you're paying for

**Zone plans** (per domain, fixed monthly)
- example.com — Pro Plan, $25/mo — upgraded 2024-08-07
- other.com — Free Plan, $0/mo

**Account plans** (pay-as-you-go consumption)
- Workers Paid — $5/mo base + usage
- R2 Paid — usage only
- Log Explorer — $0 base + usage

**Total base:** $30/mo before usage.

## Recent activity (last 3 months)

| Date | Description | Amount | Status | Receipt |
| --- | --- | ---: | --- | --- |
| 2026-05-12 | Monthly invoice | $0.00 | CLOSED | IN-65007205 |
| 2026-04-12 | Monthly invoice | $0.00 | CLOSED | IN-62205358 |
| 2026-03-12 | Monthly invoice | $1.55 | CLOSED | IN-59612378 |
| 2026-02-28 | Mid-cycle invoice | **$11.56** | **OPEN** | IN-58696934 |

## Things to check

- **Outstanding $11.56** on receipt IN-58696934 from 2026-02-28 — pay at dash.cloudflare.com/billing.
- No pending authorizations.
- No duplicate charges detected.

## What to do

1. Pay the $11.56 outstanding invoice (IN-58696934) at dash.cloudflare.com/billing.
2. If you don't recognize the $1.55 from March, it's usage on Workers/R2 — check the dashboard's usage page for that month.
3. If anything still looks wrong, contact Cloudflare support with **receipt IN-58696934** and the specific amount.
```

**If the "Things to check" section is empty, say so explicitly** — "No outstanding balances, no pending authorizations, no duplicates detected" reassures more than silence.

## Tone

Friendly, plain, zero jargon. The reader is confused — meet them there.

- Say "your `example.com` domain is on the $25/mo Pro plan" — **not** "zone `a506…494` has rate_plan `pro`".
- Say "you upgraded this on August 7, 2024" — **not** "created_date 2024-08-07T02:55:22Z".
- Say "this charge is still pending at your bank" — **not** "status: PENDING".
- Currency: always include the symbol ($) and 2 decimal places.

## Common edge cases

- **No charges at all** → likely a free-tier-only account. Say so plainly: "You're on free plans only and have no billing history to debug."
- **API returns an auth error** (HTTP 401/403, or `success: false` with code `10000`) → token missing or wrong scope. Tell the user to create a token with **Account → Billing → Read** at `dash.cloudflare.com/profile/api-tokens`.
- **Multiple accounts** → `GET /user/subscriptions` shows subs across all accounts the token can see. If the user has multiple, ask which one they're asking about before pulling history (history is user-scoped, not account-scoped).
- **Deprecation notice** — `GET /user/billing/history` is marked deprecated by Cloudflare but remains live as of 2026. If the call starts returning errors, note it and recommend `dash.cloudflare.com/billing`.
- **Per-product usage breakdown** (Workers CPU ms, R2 storage, KV ops, etc.) is **not** exposed by the public API — the dashboard's "Billable usage" tab uses an internal endpoint. If the customer asks "what's driving my usage costs this month," direct them to `https://dash.cloudflare.com/<account_id>/billing/billable-usage` and offer to interpret the page if they paste the totals back.
