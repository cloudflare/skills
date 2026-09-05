# Code Review — Workers

How to review Workers code for type correctness, API usage, config validity, and best practices. This is self-contained — do not assume access to other skills.

## Evidence Selection

Types, config schemas, and APIs change with compatibility dates, flags, and dependency versions. For an existing project, use its pinned dependencies, generated types, configuration, lockfile, and tests as the primary contract. Do not automatically substitute the latest published package for the version the project deploys.

Retrieve current official documentation or published types only when the local contract cannot answer the question, the task explicitly targets current behavior or an upgrade, or a material claim is sensitive to platform changes. State which version or compatibility setting the evidence applies to.

### Workers types

Use generated types from `wrangler types` when the project maintains them, or inspect its installed `@cloudflare/workers-types` declarations. Search for the specific type, class, or interface under review instead of guessing names. If neither is available and the exact signature matters, consult the official documentation or the package version appropriate to the task.

### Wrangler config schema

Use the schema bundled with the project's pinned Wrangler version when validating its existing configuration. Consult current official documentation when authoring against the latest Wrangler or planning an upgrade. Do not guess field names or structures when they can be checked locally.

### Cloudflare docs

Use official Cloudflare Workers documentation for platform behavior not established by local types, schemas, or tests. Retrieve the smallest relevant page rather than the full documentation set.

---

## Type Validation

### Env interface

- Every binding must have a specific type. Flag `any`, `unknown`, `object`, or `Record<string, unknown>` on bindings.
- Binding types that accept generic parameters (Durable Object namespaces, Queues, Service bindings for RPC) must include them. Read the type definition to confirm which types are generic.
- Binding names must match the wrangler config exactly.
- Prefer generated types from `wrangler types` over hand-written interfaces.

### Handler and class signatures

Verify against current type definitions — do not assume signatures are stable.

- Correct import path (most Workers platform classes import from `"cloudflare:workers"`)
- Generic type parameter on base classes (e.g., `DurableObject<Env>`)
- Binding access pattern: `env.X` in module export handlers, `this.env.X` in classes extending platform base classes
- `ExecutionContext` as the third param in module export handlers (needed for `ctx.waitUntil()`)
- `fetch()` handlers must return `Promise<Response>`

### Binding access — the most common error

- **Module export handlers** (`fetch`, `scheduled`, `queue`, `email`): bindings via `env.X` parameter
- **Platform base classes** (`WorkerEntrypoint`, `DurableObject`, `Workflow`, `Agent`): bindings via `this.env.X`

Flag `env.X` inside a class extending a platform base class. Flag `this.env.X` inside a module export handler.

### Type integrity rules

| Rule | Detail |
|------|--------|
| No `any` | Never on binding types, handler params, or API responses |
| No double-casting | `as unknown as T` hides real incompatibilities — fix the underlying design |
| Justify suppressions | `@ts-ignore`/`@ts-expect-error` must include a comment explaining why |
| Prefer `satisfies` | Use `satisfies ExportedHandler<Env>` over `as` — validates without widening |
| Validate, do not assert | Schema or type guard for untyped data (JSON, parsed bodies), not `as` |

### Stale class patterns

Old patterns survive in codebases long after APIs change.

- **`extends` vs `implements`**: platform classes use `extends`, not `implements`. The `implements` pattern is legacy and loses `this.ctx`, `this.env`.
- **Import paths**: verify module specifiers match what types actually export. Common mistake: wrong path for `"cloudflare:workers"` vs `"cloudflare:workflows"`.
- **Renamed properties**: e.g., `this.state` to `this.ctx` in Durable Objects. Search types to confirm.
- **Constructor signatures**: base class constructors change. Verify expected parameters.

---

## Config Validation

### Required fields

For executable examples, verify: `name`, `compatibility_date`, `main`. Check the schema for current required fields.

### Config format

- **JSONC** (`wrangler.jsonc`) — preferred for new projects
- **JSON** (`wrangler.json`) — valid but no comments
- **TOML** (`wrangler.toml`) — legacy; acceptable in existing content, flag in new projects

### Binding-code consistency

1. Every `env.X` reference in code has a corresponding binding declaration in config
2. Every binding in config is referenced in code (warn on unused)
3. Names match exactly (case-sensitive)
4. For Durable Objects: `class_name` matches the exported class name

### Common config mistakes

| Check | What to look for |
|-------|-----------------|
| Stale `compatibility_date` | Should be recent; use `$today` placeholder in docs |
| Missing DO migrations | Every new DO class needs a migration entry |
| Binding name mismatch | Config `binding`/`name` must match `env.X` in code |
| Secrets in config | Never in `vars` — use `wrangler secret put` |
| Wrong binding key | Verify top-level key name against the schema |
| Missing entrypoint | `main` required for executable Workers |

---

## Anti-Patterns to Flag

See the full anti-patterns table in `SKILL.md`. The type-specific ones to watch for during review:

- **`any` on `Env` or handler params** — defeats type safety for all downstream binding access
- **`as unknown as T`** — hides real type incompatibilities; fix the underlying design
- **`@ts-ignore`/`@ts-expect-error` without explanation** — masks errors silently; require a justifying comment
- **`implements` instead of `extends` on platform base classes** — legacy pattern; loses `this.ctx`, `this.env`
- **`env.X` inside class body** — should be `this.env.X` in platform base classes
- **`this.env.X` in module export handler** — should be `env.X` parameter
- **Non-serializable values across boundaries** — `Response`, `Error` in step/queue compiles but fails at runtime

---

## Serialization Boundaries

Data crossing these boundaries must be structured-clone serializable:

- **Queue messages**: body passed to `.send()` or `.sendBatch()`
- **Workflow step return values**: persisted to durable storage
- **DO storage**: values in `storage.put()` or SQL
- **`postMessage()`**: WebSocket messages

Non-serializable types to flag: `Response`, `Request`, `Error`, functions, class instances with methods, `Map`/`Set`, `Symbol`.

Valid: plain objects, arrays, strings, numbers, booleans, null, `ArrayBuffer`, `Date`.

---

## Review Scope

Read enough context beyond the diff to understand bindings and deployment assumptions. Match the depth of review and validation to what the code claims to be:

- **Illustrative** examples need correct API names and realistic signatures.
- **Demonstrative** snippets should have valid syntax, APIs, and binding access in their stated context.
- **Executable** projects should compile and include coherent imports, configuration, and bindings.

Prioritize relevant risks rather than mechanically applying every check: handler and binding types, config-code consistency, streaming and promise lifetime, mutable global state, serialization boundaries, secrets and cryptography, and error handling. Use the project's available typecheck, tests, lint, and Wrangler validation where they add confidence. Assess severity from runtime impact and support each reported finding with evidence.

### Output format

```
**[SEVERITY]** Brief description
`file.ts:42` — explanation with evidence
Suggested fix: `code`
```

Severity: **CRITICAL** (security, data loss, crash) | **HIGH** (type error, wrong API, broken config) | **MEDIUM** (missing validation, edge case) | **LOW** (style, minor improvement)
