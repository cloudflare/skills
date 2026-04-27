---
name: use-case-routing
description: Route user goals and scenarios to the right Cloudflare products and implementation paths using structured use case decision trees. Load when a user describes what they want to achieve and you need qualifying questions, recommended products, and next-step plans.
---

# Use Case Routing

Use this skill when a user describes a problem, goal, or scenario and you need to map it to the most relevant Cloudflare products and implementation path.

This skill works for both existing Cloudflare customers and people evaluating Cloudflare for the first time.

## Start Here

1. Scan `references/index.json` by `name`, `description`, `aliases`, `category`, and `products`.
2. Choose the closest matching use case.
3. Fetch the matching YAML from `references/use-cases/<id>.yaml`.
4. For interactive conversations, walk the `qualifying_questions` and accumulate the option `sets`.
5. Match the best `paths` entry by its `condition`.
6. If the conversation is non-interactive or ambiguous, use `default_path`.

## Files

| File | Purpose |
|------|---------|
| `references/index.json` | Summary index for discovery and matching |
| `references/schema.yaml` | Schema for the structured use case format |
| `references/use-cases/*.yaml` | Individual use case routing trees |

## How To Apply The Output

- Use the selected path to explain which Cloudflare products fit the user's goal.
- Present the ordered `steps` as the recommended implementation path.
- Treat product and action names as routing guidance, then verify detailed configuration against current Cloudflare docs.
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
