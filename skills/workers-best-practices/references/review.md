# Workers Type and Runtime Checks

Consult the sections relevant to the affected bindings, handlers, configuration, or serialization boundaries. Use the project's installed types and compatibility settings as the target.

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

## Serialization Boundaries

Data crossing these boundaries must be structured-clone serializable:

- **Queue messages**: body passed to `.send()` or `.sendBatch()`
- **Workflow step return values**: persisted to durable storage
- **DO storage**: values in `storage.put()` or SQL
- **`postMessage()`**: WebSocket messages

Non-serializable types to flag: `Response`, `Request`, `Error`, functions, class instances with methods, `Map`/`Set`, `Symbol`.

Valid: plain objects, arrays, strings, numbers, booleans, null, `ArrayBuffer`, `Date`.
