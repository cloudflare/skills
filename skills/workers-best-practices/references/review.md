# Code Review — Workers

How to review Workers code for type correctness, API usage, config validity, and best practices. This is self-contained — do not assume access to other skills.

## Retrieval

Your knowledge of Cloudflare Workers APIs and limits may be outdated. Always retrieve [current documentation](http://developers.cloudflare.com/) when an affected API signature, configuration field, runtime behavior, or limit is uncertain or the task requests current guidance. Types, config schemas, and APIs change with compatibility dates and new bindings.

### Workers types

`npx wrangler types` generates a typed `Env` interface from the local wrangler config. Use this when a binding/configuration change requires regenerating types.

### Wrangler config schema

The authoritative schema is bundled with wrangler as `config-schema.json` (JSON Schema draft-07).

```bash
# Read from local node_modules
cat node_modules/wrangler/config-schema.json
```

Do not guess field names or structures — look them up.

### Cloudflare docs

For uncertain APIs, runtime semantics, compatibility requirements, or limits, use the Cloudflare docs search tool or retrieve the relevant page under `https://developers.cloudflare.com/workers/`. The best practices page lives at `/workers/best-practices/workers-best-practices/`.

---

## Type Validation

### Env interface

- Every binding must have a specific type. Flag `any`, `unknown`, `object`, or `Record<string, unknown>` on bindings.
- Binding types that accept generic parameters (Durable Object namespaces, Queues, Service bindings for RPC) must include them. Read the type definition to confirm which types are generic.
- Binding names must match the wrangler config exactly.
- Prefer generated types from `wrangler types` over hand-written interfaces.

### Handler and class signatures

Verify affected signatures against the project's target type definitions; consult current docs if runtime support or compatibility remains uncertain.

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

For executable examples, verify: `name`, `compatibility_date`, `main`. Check the target Wrangler schema when required fields are in question.

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
| Compatibility date and flags | Verify support for the affected feature under the configured settings; use `$today` for new-project examples |
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

## Review Process

1. **Establish scope and target** — start with the requested diff, files, or behavior and the relevant project versions/configuration. Read surrounding handlers, classes, binding declarations, and callers when needed to establish impact; expand to full files when that context is necessary.
2. **Categorize code** — determines what to check:
   - **Illustrative** (concept demo, comments for most logic): verify correct API names and realistic signatures
   - **Demonstrative** (functional snippet, would work in context): verify syntax, correct APIs, correct binding access
   - **Executable** (standalone, runs without modification): verify compiles, runs, includes imports and config
3. **Investigate affected behavior** — apply relevant type, config, binding-access, streaming, promise-lifetime, state, serialization, and security checks. Retrieve missing evidence using the sources above; a full review can cover all applicable categories, while a focused review stays within its requested scope.
4. **Validate proportionally** — use existing project commands that can resolve the identified concern. Type-check changes to types or binding contracts; inspect or lint affected async paths for floating promises; run relevant runtime tests for behavior changes. Preserve required repository checks, but do not install a new linter or run an unrelated full suite as a review prerequisite. Comments or prose-only changes generally need static inspection. Report checks that could not run and their consequences.
5. **Report supported findings** — connect each issue to the affected execution path and concrete impact, citing file lines, tool output, or documentation. Separate upgrade suggestions from defects in the configured target. For requested fixes, correct failures caused by the change and rerun affected checks before reporting completion.

### Output format

```
**[SEVERITY]** Brief description
`file.ts:42` — explanation with evidence
Suggested fix: `code`
```

Severity: **CRITICAL** (security, data loss, crash) | **HIGH** (type error, wrong API, broken config) | **MEDIUM** (missing validation, edge case) | **LOW** (style, minor improvement)
