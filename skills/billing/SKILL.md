---
name: billing
description: Debug Cloudflare (and optionally Stripe) billing for a confused customer — outstanding balances, why they're on FREE/PRO/BUSINESS, possible double charges, pending authorizations, which zones/products drive cost. Pulls subscriptions + billing history via the `mcp-billing-server` MCP and presents a friendly, plain-language summary the customer can act on. Load when a user asks why they were charged, what plan they're on, whether they have outstanding invoices, or asks for help reconciling a Cloudflare or Stripe bill.
---

# Billing (Cloudflare + Stripe)

Backed by the open-source [`mcp-billing-server`](https://github.com/dalexeenko/mcp-billing-server) MCP server — read-only by construction. The server exposes Cloudflare subscription/billing-history tools and (optionally) Stripe read tools. This skill walks the agent through a structured investigation and produces a single, plain-language summary the customer can act on.

Tool schemas for this MCP server are bundled in [`tools.json`](./tools.json) — code-mode hosts can consume them directly to generate TypeScript types without first connecting to the server.

## Prerequisites

The `mcp-billing-server` MCP must be connected. Two tokens, both read-only:

- **Cloudflare API token** with `Account → Billing → Read` (required). `Zone → Zone → Read` is optional and only needed for `cloudflare_get_zone_subscription`.
- **Stripe restricted key** (`rk_...`) with read on Customers, Invoices, Subscriptions, Charges, Balance (optional — only if the customer also asks about Stripe).

If the server isn't connected or a token is missing, tell the user how to set it up (see the [project README](https://github.com/dalexeenko/mcp-billing-server)) and stop — don't guess.

## Tools you'll call

**Cloudflare**

| Tool | When |
| --- | --- |
| `cloudflare_list_account_subscriptions` | Primary — the full plan picture per account |
| `cloudflare_get_user_subscriptions` | Fallback when the user doesn't know their account ID |
| `cloudflare_list_billing_history` | Every charge, refund, proration with status |
| `cloudflare_get_zone_subscription` | Only if drilling into one specific domain |

**Stripe** (only if asked)

| Tool | When |
| --- | --- |
| `stripe_list_customers` / `stripe_get_customer` | Find / fetch a customer |
| `stripe_list_invoices` / `stripe_get_invoice` | Invoice-level questions |
| `stripe_list_subscriptions` | Recurring revenue / active subs |
| `stripe_list_charges` | Itemized payments |
| `stripe_get_balance` | Current available + pending balance |

## What to ask before running anything

At most **two** questions:

1. **Account ID?** (the 32-char hex from the dash URL, e.g. `dash.cloudflare.com/<account_id>/...`). If they don't know it, fall back to `cloudflare_get_user_subscriptions`.
2. **Is there a specific charge or date that's confusing you?** Narrows the search if their history is long.

Don't keep asking. Often the data answers the question on its own — run the tools and *then* clarify if needed.

## Investigation order

### Step 1 — Subscriptions

Call `cloudflare_list_account_subscriptions` (or `cloudflare_get_user_subscriptions` as fallback). Group results into:

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

Call `cloudflare_list_billing_history` with `per_page: 50`. Walk each item:

| Signal | Plain-language meaning |
| --- | --- |
| `status: CLOSED` AND `amount_to_pay: 0` | Settled, nothing owed |
| `status: OPEN` OR `amount_to_pay > 0` | **Outstanding balance — surface prominently** |
| `status: PENDING` | Bank authorization in flight, not a real charge yet |
| `type: refund` or negative `amount` | Money returned |
| Two items with same `amount` within ~5 min on same `source` | **Flag as possible double charge** — ask user to verify against their bank/card statement |
| `source: stripe` | Charged via Stripe (typical) |

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

## ⚠️ Things to check

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
- **Tool returns auth error** → token missing or wrong scope. Tell the user to create a token with **Account → Billing → Read** at `dash.cloudflare.com/profile/api-tokens`.
- **Multiple accounts** → `cloudflare_get_user_subscriptions` shows subs across all accounts the token can see. If the user has multiple, ask which one they're asking about before pulling history (history is user-scoped, not account-scoped).
- **Deprecation notice** — the underlying billing history endpoint is marked deprecated by Cloudflare but remains live as of 2026. If the call starts failing, note it and recommend dash.cloudflare.com/billing.
- **Per-product usage breakdown** (Workers CPU ms, R2 storage, KV ops, etc.) is **not** exposed by this MCP server — the dashboard's "Billable usage" tab uses an internal Cloudflare endpoint that isn't in the public SDK. If the customer asks "what's driving my usage costs this month," direct them to `https://dash.cloudflare.com/<account_id>/billing/billable-usage` and offer to interpret the page if they paste the totals back.

## Installing the MCP server

Add to `claude_desktop_config.json` (or any MCP-aware client):

```json
{
  "mcpServers": {
    "billing": {
      "command": "npx",
      "args": ["-y", "mcp-billing-server"],
      "env": {
        "CLOUDFLARE_API_TOKEN": "...",
        "STRIPE_API_KEY": "rk_live_..."
      }
    }
  }
}
```

Source, setup walkthrough, safety model: <https://github.com/dalexeenko/mcp-billing-server>.
