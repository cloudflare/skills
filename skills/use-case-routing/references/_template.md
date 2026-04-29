# Filename convention: <id>-<slug>.md
# - <id> matches the `id:` frontmatter field (e.g. sec-001)
# - <slug> is the kebab-cased name with conjunctions ("and", "&") and
#   articles ("a", "the") dropped, capped at ~5-6 words
# - Examples: sec-001-prevent-ddos-attacks.md, ops-016-reduce-ai-costs.md

---
# REQUIRED FIELDS

# Unique identifier. Format: <category-prefix>-<3-digit-number>
# Prefixes: aisec, arch, compliance, dev, ind, net, obs, ops, perf, sec, start, zt
id: cat-001

# Human-readable name. Verb-forward, goal-oriented.
# Avoid product names unless the user would search by them.
name: One-line goal statement

# Category slug. Must match the controlled vocabulary in SKILL.md.
category: <category-slug>

# 1-2 sentence summary in plain language. Use words a non-Cloudflare-customer
# would use. Strip jargon. Test: would someone Googling this problem use
# these words?
description: >
  Concise description of what the user is trying to achieve.

# Cloudflare products involved in this use case. Use canonical product names.
products: [Product A, Product B]

# ID of the path to recommend when the conversation is non-interactive
# (or the user gives no info). Must match a path heading in the body.
default_path: <path-id>

# OPTIONAL FIELDS

# Alternate names for the same goal. These should pass the test
# "could replace the name in a sentence." Use for renames, not search hints.
aliases:
  - Alternate name one
  - Alternate name two

# Search hints, common phrasings, error messages, support-ticket subject lines,
# competitor product names. Use for fuzzy matching when users don't know the
# canonical name.
keywords:
  - "common phrasing one"
  - "error code or symptom"
  - "competitor product name"

# IDs of related use cases the agent might want to follow up with.
# Validation: every ID must exist in the corpus.
related:
  - other-id
---

# Use case: <name>

## Ask first

A short list of questions to narrow the recommendation. Each question
lists options. Each option ends with `→ path-id` to map to a path in
the next section.

**What is your specific goal?**
- Option A description → path-a
- Option B description → path-b
- Option C description → path-c

**Optional follow-up question** (only if the first answer needs narrowing)
- Sub-option → path-a-variant

If the user describes a special condition that applies regardless of the
above answers (e.g. an active incident), instruct the agent to also walk
that path.

## Paths

### path-a (default)

Prose description of what the agent should recommend. Be specific about
which products and configurations. Use numbered lists when sequence
matters; use prose when it doesn't.

For [variant condition]: note the variant inline rather than creating
a separate path.

### path-b

Prose description for this path.

### path-c

Prose description for this path.

## Hand off

For implementation, retrieve current details from Cloudflare docs:
https://developers.cloudflare.com/ — search for the products in the
recommended path. Builder skills may also be available — browse
https://github.com/cloudflare/skills/tree/main/skills and load any
that match the products. Do not name specific skills here; the
catalog evolves.
