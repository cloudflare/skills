---
name: use-case-routing
description: Help users solve problems in web security, application performance, edge compute, AI infrastructure, network connectivity, Zero Trust access, and compliance by recommending the right Cloudflare products. Load when a user describes what they want to achieve — whether they have never used Cloudflare, are evaluating it for the first time, or already use some products and need help choosing the rest of the stack. Covers qualifying questions, conditional product paths, and multi-product recommendations. Do NOT load for implementation, configuration, or coding tasks — use the cloudflare, agents-sdk, durable-objects, wrangler, or other builder skills for those. Biases towards retrieval from Cloudflare docs over pre-trained knowledge.
references:
  - index
  - schema
  - use-cases
---

# Use Case Routing

Your knowledge of Cloudflare products, names, and capabilities may be outdated. **Prefer retrieval over pre-training** for any product recommendation. Product names change, pricing tiers shift, and new products launch — do not trust baked-in knowledge of what a product does or which plan includes it.

## Scope — Discovery Only

This skill is **only for product discovery and routing**. It helps answer "which Cloudflare products should I use?" — not "how do I build with them."

This skill works for people evaluating Cloudflare for the first time, users exploring new capabilities, and existing customers expanding into new use cases.

- Use this skill when a user describes a goal, scenario, or pain point and needs help figuring out which Cloudflare products to use — whether they are new to Cloudflare or already use some products and need the right additions.
- **Never** use this skill as a substitute for implementation guidance. The steps in each use case YAML are abstract routing signals (e.g., `create-agent-project`, `define-tools`), not actionable build instructions.
- **Never** rely on this skill to inform how to configure, code, or deploy a product. Always hand off to a dedicated builder skill for that.

### When to use this skill vs. the `cloudflare` skill

| Scenario | Use this skill | Use `cloudflare` skill |
|----------|---------------|----------------------|
| User describes a business goal without naming products ("I want to protect my APIs from abuse") | Yes | No |
| User mentions a product but needs help choosing the rest of the stack ("I use Workers but need the right setup for real-time collaboration") | Yes | No |
| User needs qualifying questions to narrow down options | Yes | No |
| User already knows the product and wants to build ("How do I set up WAF rules?") | No | Yes |
| User names a product category from the decision trees ("I need to store data") | No | Yes |
| User is evaluating Cloudflare for the first time and needs a product recommendation | Yes | No |
| User needs implementation details, code, or config for a known product | No | Yes (or a dedicated skill) |

The `cloudflare` skill has simpler decision trees ("I need to run code" -> `workers/`) that work when the user already thinks in product categories. This skill is richer — it has qualifying questions, conditional paths, and multi-product recommendations — and is meant for the earlier discovery stage when the user only has a problem statement.

## Retrieval Sources

After routing to a product, verify current product details against the docs before presenting recommendations.

| Source | How to retrieve | Use for |
|--------|----------------|---------|
| Cloudflare docs | `https://developers.cloudflare.com/` | Product capabilities, pricing, limits, current feature set |
| Product changelogs | `https://developers.cloudflare.com/changelog/` | Recent changes, new products, deprecations |

When a use case YAML and the docs disagree on product names or capabilities, **trust the docs**.

## Start Here

1. Scan `references/index.json` by `name`, `description`, `aliases`, `category`, and `products`.
2. Choose the closest matching use case.
3. Fetch the matching YAML from `references/use-cases/<id>.yaml`.
4. For interactive conversations, walk the `qualifying_questions` and accumulate the option `sets`.
5. Match the best `paths` entry by its `condition`.
6. If the conversation is non-interactive or ambiguous, use `default_path`.

## After Routing — Hand Off to Builder Skills

After selecting a path, **do not stop at the routing output**. The steps in each path are discovery signals, not implementation plans. You must hand off to the appropriate skill for the actual build.

1. Identify the primary product(s) in the selected path's `steps`.
2. Check whether a dedicated skill exists for that product:

| Product in path | Load skill |
|----------------|------------|
| Workers, Pages, KV, D1, R2, WAF, DDoS, or most Cloudflare products | `cloudflare` |
| Agents SDK, AI agents | `agents-sdk` |
| Durable Objects | `durable-objects` |
| Wrangler CLI | `wrangler` |
| Workers (best practices) | `workers-best-practices` |

3. Load the matching skill and use it for implementation details, code examples, configuration, and deployment.
4. If no dedicated skill exists, fall back to `cloudflare` and its references, or retrieve directly from `https://developers.cloudflare.com/`.

## Files

| File | Purpose |
|------|---------|
| `references/index.json` | Summary index for discovery and matching |
| `references/schema.yaml` | Schema for the structured use case format |
| `references/use-cases/*.yaml` | Individual use case routing trees |

## How to Apply the Output

- Use the selected path to explain which Cloudflare products fit the user's goal.
- Present the ordered `steps` as the recommended product path — not as build instructions.
- Treat product and action names as routing guidance, then load the relevant builder skill or verify detailed configuration against current Cloudflare docs.
- If two use cases seem plausible, present the top matches and explain the difference.

## Categories

The dataset currently covers:

- Network & Application Security
- AI Security
- Zero Trust & Secure Access
- Network Connectivity & WAN
- Application Performance & Delivery
- Developer Platform - Build
- Developer Platform - Operate
- Compliance & Data Governance
- Observability & Analytics
- Multi-Vendor & Architecture
- Industry Verticals
- Getting Started
