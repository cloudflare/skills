# Prerequisites for Adding a New Cloudflare Product Skill

This document describes the research and source material needed before writing a skill reference for a new Cloudflare product. Following this process ensures the skill is accurate, consistent with existing references, and comprehensive enough to be useful.

## 1. Gather Primary Sources

Before writing anything, collect these materials for the product:

### Official Documentation

| Source | Where to find it | What it provides |
|--------|-------------------|------------------|
| **LLM reference** | `https://developers.cloudflare.com/<product>/llms-full.txt` | Condensed, structured overview of the full product — usually the single best starting point |
| **Developer docs** | `https://developers.cloudflare.com/<product>/` | Canonical reference for APIs, config, limits, pricing |
| **Getting started guide** | `https://developers.cloudflare.com/<product>/getting-started/` | Setup steps, minimal working examples |
| **Blog announcement** | `https://blog.cloudflare.com/<product>/` | Design rationale, performance claims, positioning vs alternatives |

The LLM reference (`llms-full.txt`) is the highest-signal single source. Start there. Fall back to the full docs for details it doesn't cover.

### Working Examples

| Source | Where to find it | What it provides |
|--------|-------------------|------------------|
| **Official examples** | `https://github.com/cloudflare/agents/tree/main/examples/` (or product-specific repos) | Real, runnable code showing intended usage patterns |
| **Starter templates** | Linked from the getting started guide | Minimal scaffolding for common setups |

**Read the actual source code of every relevant example.** GitHub tree pages only show file listings — you need to fetch each source file individually (via raw URLs or a clone). Examples reveal:
- Real `wrangler.jsonc` configurations (what bindings are actually needed)
- How the product combines with other Cloudflare products (AI, Durable Objects, etc.)
- Idiomatic patterns the docs may not spell out
- Edge cases handled in production-quality code

### Upstream Repository

If the product has an SDK or library (e.g. `@cloudflare/worker-bundler`, `@cloudflare/sandbox`):
- Check the npm package for current API surface
- Read the repo README and any inline type definitions
- Capture the current API shape and doc entry points; avoid pinning version-specific details unless they are required to use the product

## 2. Understand the Product's Position

Before writing, answer these questions:

- **What existing products is this most similar to?** (e.g. Dynamic Workers vs Workers for Platforms vs Sandbox)
- **What's the key differentiator?** (runtime vs pre-deployed, isolates vs containers, etc.)
- **When should someone use this instead of the alternatives?**
- **What bindings/integrations does it need?** (worker_loaders, durable_objects, ai, etc.)

This informs the README's comparison table and the SKILL.md decision tree entry.

## 3. Follow the Standard 5-File Structure

Every product reference in `skills/cloudflare/references/` uses this structure:

```
references/<product-name>/
  README.md         — Overview, architecture, quick start, comparison table
  api.md            — API reference: methods, types, parameters, return values
  configuration.md  — wrangler.jsonc setup, binding combinations, CLI commands
  patterns.md       — Common usage patterns with full code examples
  gotchas.md        — Errors, best practices, retrieval cues, starter links
```

### What goes in each file

**README.md**: The entry point. Someone reading only this file should understand what the product is, when to use it, and how to get a minimal example running. Include:
- One-line description
- Comparison table vs similar products
- Architecture diagram or description
- Quick start (wrangler config + minimal code)
- Links to the other 4 files and related references

**api.md**: Complete API surface. For each method/class/type:
- Signature and parameters
- Code example showing usage
- Notes on behavior (caching, async, error cases)
- For RPC/binding patterns, show both the definition and consumption sides

**configuration.md**: Everything about setup and config. Include:
- The primary binding configuration (wrangler.jsonc and wrangler.toml)
- How it combines with other bindings (show real composite configs from examples)
- Supported languages/runtimes
- CLI commands relevant to this product
- Any bundling or build steps required

**patterns.md**: Real-world usage patterns, each with complete runnable code. Source these from:
- Official examples (adapt, don't just copy)
- Patterns described in the docs/blog
- Common combinations with other products
Aim for 4-7 patterns ranging from basic to advanced.

**gotchas.md**: Everything that trips people up. Include:
- Common errors with cause/solution pairs
- Best practices (do/don't format with code examples)
- Retrieval cues for pricing, limits, and plan availability, with links to the official docs instead of copied tables
- Links to starter templates and official resources

## 4. Update the Skill Index

After creating the reference directory, update `skills/cloudflare/SKILL.md`:

1. **Decision tree**: Add a branch in the appropriate "I need to..." tree. Place it near similar products with a description that distinguishes it.

2. **Product index table**: Add a row in the appropriate section (Compute & Runtime, Storage, AI, etc.).

## 5. Cross-Reference Other Skills

Check if existing skills should link to the new one:
- Products it's commonly used with (e.g. Dynamic Workers + Agents SDK, + Tail Workers)
- Products it's easily confused with (comparison in README helps)
- The main SKILL.md decision trees

## 6. Verify Before Committing

- [ ] All code examples use current API syntax (check against `llms-full.txt` and docs)
- [ ] `wrangler.jsonc` examples match real working configurations from official examples
- [ ] Pricing, limits, and plan availability link to official docs rather than copying values that may drift
- [ ] No broken internal links between the 5 files
- [ ] SKILL.md decision tree entry distinguishes this from similar products
- [ ] SKILL.md product index row added in the correct section
- [ ] README.md includes a retrieval-bias directive near the top of the file
- [ ] File structure matches `README.md`, `api.md`, `configuration.md`, `patterns.md`, `gotchas.md` exactly

## Example: What Was Needed for Dynamic Workers

| Source | URL | Key information extracted |
|--------|-----|--------------------------|
| LLM reference | `developers.cloudflare.com/dynamic-workers/llms-full.txt` | Full API surface, WorkerCode properties, retrieval entry points |
| Docs home | `developers.cloudflare.com/dynamic-workers/` | Architecture overview, use cases, security model |
| Getting started | `developers.cloudflare.com/dynamic-workers/getting-started/` | `worker_loaders` binding, `load()` vs `get()`, supported languages |
| Blog post | `blog.cloudflare.com/dynamic-workers/` | V8 isolate performance claims, helper libraries, design rationale |
| `dynamic-workers` example | `github.com/cloudflare/agents/.../dynamic-workers/` | Minimal `load()` pattern, basic wrangler config |
| `dynamic-workers-playground` example | `github.com/cloudflare/agents/.../dynamic-workers-playground/` | `get()` with content-hashed IDs, `@cloudflare/worker-bundler`, Tail Worker + DO logging pipeline, warmup trick |
| `codemode` example | `github.com/cloudflare/agents/.../codemode/` | `AIChatAgent` + `DynamicWorkerExecutor` integration, SQL-backed tools |
| `codemode-mcp` example | `github.com/cloudflare/agents/.../codemode-mcp/` | `codeMcpServer()` wrapper pattern |
| `codemode-mcp-openapi` example | `github.com/cloudflare/agents/.../codemode-mcp-openapi/` | `openApiMcpServer()` for REST API wrapping |
| `worker-bundler-playground` example | `github.com/cloudflare/agents/.../worker-bundler-playground/` | AI-generated app pattern, `createWorker()` with assets, DO persistence |

Six examples were needed to cover the full range of patterns. The `llms-full.txt` provided the API reference backbone. The blog provided design rationale and helper-library context. The examples provided real wrangler configs and production patterns.
