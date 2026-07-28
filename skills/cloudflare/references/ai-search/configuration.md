# AI Search Configuration

Full option list, current defaults, ranges, and enums: the [configuration docs](https://developers.cloudflare.com/ai-search/configuration/), `instance.info()`, and `npx wrangler ai-search create --help`.

## Worker setup

```jsonc
// wrangler.jsonc
{
  "compatibility_date": "2026-03-27",   // or later
  "ai_search_namespaces": [
    { "binding": "AI_SEARCH", "namespace": "default", "remote": true }
  ]
}
```

```typescript
interface Env { AI_SEARCH: AiSearchNamespace }

const { chunks } = await env.AI_SEARCH.get("my-instance").search({
  messages: [{ role: "user", content: "How do I configure caching?" }],
});
```

**Settings change from the Worker, not just the dashboard.** `update()` takes a partial of the same object `create()` takes, applies only the keys you pass, and returns the instance info that `info()` would return.

```typescript
const instance = env.AI_SEARCH.get("my-instance");

const info = await instance.update({
  index_method: { vector: true, keyword: true },
  retrieval_options: { keyword_match_mode: "and" },
});
```

Omitted keys keep their current value, so read before you write only when you need the old value. What `update()` cannot fix is in [Decide before you create](#decide-before-you-create).

- **`compatibility_date` must be at least `2026-03-27`.** An older one leaves the binding `undefined` at runtime, the most common setup failure.
- `remote: true` proxies `wrangler dev` to the deployed instance. There is no local emulator, so local dev hits real data and real query limits.
- Every account has a `default` namespace. Wrangler creates any other namespace you name on deploy.

Use `ai_search` only when the Worker reads exactly one instance that already exists. It has no `get()`, `list()`, `create()`, `delete()`, or cross-instance search. See [api.md](api.md#bindings).

## Decide before you create

Surface these to the user rather than picking silently.

**Cannot be changed on an existing instance. Create a new one.**

| Decision | Why |
|----------|-----|
| **Embedding model** | Different dimensions, different vector space. Existing vectors are not converted, so there is nothing to migrate in place. |
| **Data source type** | An instance takes built-in storage plus at most one external source. Switching that source type in place is unsupported. |

**Changing an indexing setting reindexes the whole instance.**

`index_method`, `indexing_options`, and `chunk` / `chunk_size` / `chunk_overlap` are applied to an item when it is indexed, so `update()` resyncs the existing corpus to apply them. 

## Creating an instance

**Default to built-in storage.** Only `id` is required. Omit `type` and `source` and the instance provisions its own R2 and Vectorize, and you write to it directly.

```bash
npx wrangler ai-search create my-instance
```

```typescript
// requires the namespace binding; create() returns the instance handle
const instance = await env.AI_SEARCH.create({ id: "my-instance" });
await instance.items.upload("faq.md", content);
```

Add `type` and `source` only to point at content that already lives elsewhere. See [Data sources](#data-sources).

```bash
npx wrangler ai-search create my-instance --type r2 --source my-docs-bucket --hybrid-search
```

IDs are short, lowercase alphanumeric with `-` and `_`. Every ingestion, indexing, retrieval, and model setting is also a `create()` parameter; `create --help` lists current flags and the ambient types give the accepted shape.

## Data sources

An instance combines built-in storage with **one** external source. Pick by where the content already lives.

| Situation | Source | Freshness |
|-----------|--------|-----------|
| New corpus, or you own the write path | **Built-in storage** | Immediate, per file |
| Content already sitting in an R2 bucket | **R2** | Hours-scale sync |
| Content is a website you own | **Website crawl** | Hours-scale sync |

**R2 is the only data source that needs a service API token**, with both `AI Search:Edit` and `AI Search:Run`. Pass its UUID as `token_id` when creating your first R2-backed instance. An expired token shows up as an instance that silently stops indexing.

**Website crawl** requires a domain you own. Two non-obvious options:

```typescript
source_params: {
  include_items: ["**/docs/**"],        // the leading ** matters, see Path filtering
  web_crawler: {
    parse_type: "sitemap",
    parse_options: { use_browser_rendering: true },   // JS-rendered pages, else you index the shell
  },
}
```

Full `source_params`: [Data sources](https://developers.cloudflare.com/ai-search/configuration/data-source/).

## Path filtering

`include_items` and `exclude_items` on `source_params` decide which paths enter the index at all. Distinct from query-time [`filters`](api.md#filters): path filtering controls what exists, `filters` controls what a query may see. Built-in storage needs neither.

**Exclude is evaluated first and wins**, whether or not an include also matches. Then, if any include exists, an item must match at least one. Setting neither indexes everything.

**Patterns are anchored to the whole path, not searched inside it.** The most common reason a filter indexes nothing:

| Pattern | Matches | Skips |
|---|---|---|
| `docs/*` | `docs/file.pdf` | `docs/sub/file.pdf`, `site/docs/file.pdf` |
| `docs/**` | `docs/file.pdf`, `docs/sub/file.pdf` | `site/docs/file.pdf` |
| `**/docs/*` | `docs/file.pdf`, `site/docs/file.pdf` | `docs/sub/file.pdf` |

```typescript
// ❌ misses subfolders and any nested docs/ directory
include_items: ["docs/*"]

// ✅ catches every row above
include_items: ["**/docs/**"]
```

`*` stops at a `/`; `**` crosses them and matches zero segments as well as many. Those are the only two wildcards: no brace expansion, character classes, or negation, so `*.{md,pdf}` is two patterns. Patterns are **case-sensitive** (`/Blog/*` misses `/blog/post.html`) and compared **without normalization** (`/blog/` and `/blog` differ).

**The matched string is shaped differently per source.** R2 patterns run against object paths with a leading slash (`/docs/guide.pdf`). Website patterns run against host-inclusive URLs without the scheme (`example.com/blog/post`), which is why a website pattern almost always needs a leading `**`.

[Path filtering](https://developers.cloudflare.com/ai-search/configuration/indexing/path-filtering/).

## Indexing and syncing

Built-in storage indexes immediately, per file, with no jobs. External sources sync on an hours-scale schedule.

**Every sync of an external source is a job.** The job list is therefore the sync history, and where to look when a source is stale.

```bash
npx wrangler ai-search jobs list <NAME>              # sync history
npx wrangler ai-search jobs logs <NAME> <JOB-ID>     # what one sync did
npx wrangler ai-search jobs create <NAME>            # sync now
```

The same surface is on the binding, so a webhook handler triggers and inspects syncs without shelling out:

```typescript
await instance.jobs.create();                // sync now
await instance.jobs.list();                  // sync history
await instance.jobs.get(jobId).logs();       // what one sync did
await instance.jobs.get(jobId).cancel();     // stop a running sync
```

**To keep an external source fresh, trigger a job on publish** from a Worker webhook or CI/CD, rather than shortening `sync_interval`. The endpoint is rate-limited, so this is a per-change trigger, not a polling loop.

`stats()` is the monitoring surface: counts by state (`queued` / `running` / `completed` / `error` / `outdated`), last activity, embedding errors.

## Search modes

New instances index **vector only**. Enable keyword indexing to get BM25 or hybrid.

```typescript
await env.AI_SEARCH.create({
  id: "docs",
  index_method: { vector: true, keyword: true },       // both = hybrid available
  fusion_method: "rrf",                               // or "max"
  indexing_options: { keyword_tokenizer: "porter" },   // or "trigram"
  retrieval_options: { keyword_match_mode: "and" },    // or "or"
});
```

| Setting | Choose |
|---------|--------|
| `keyword_tokenizer` | `trigram` for code, IDs, error strings, substring matching. `porter` (stemming) for prose |
| `fusion_method` | `rrf` to blend both signals. `max` when one should dominate |

## Models

Model calls route through AI Gateway, so Anthropic, OpenAI, Google, and others are selectable alongside `@cf/*` models. Set `ai_gateway_id` to route through your own gateway.

Four slots: `embedding_model`, `ai_search_model` (generation, `chatCompletions()` only), `rewrite_model`, `reranking_model`. The last three are changeable with `update()`. **If you only use `search()`, `embedding_model` is the only one that matters**, and it is fixed for the life of the instance: see [Decide before you create](#decide-before-you-create).

**Do not pin a model name from memory.** The supported list changes often and a wrong name fails at request time. Read [Supported models](https://developers.cloudflare.com/ai-search/configuration/models/supported-models/).

## Metadata

`filename`, `folder`, and `timestamp` are always available and always filterable.

### Custom metadata

**Declare fields on the instance before uploading items with them.** Undeclared keys are not indexed and cannot be filtered on, and this fails silently: the upload succeeds, the filter just never matches. The field-count cap is small, so declare only fields you will filter by.

```typescript
await env.AI_SEARCH.create({
  id: "docs",
  custom_metadata: [
    { field_name: "category", data_type: "text" },   // text | number | boolean | datetime
    { field_name: "views",    data_type: "number" },
  ],
});

await instance.items.upload("guide.pdf", buf, { metadata: { category: "onboarding" } });
```

Adding a field later does not backfill already-indexed items; reupload or resync them.

## Public endpoint and UI snippets

Enable per instance in the dashboard (**Settings** → **Public Endpoint**) for an unauthenticated `https://<INSTANCE_ID>.search.ai.cloudflare.com/` serving `/search`, `/chat/completions`, and `/mcp`, with rate limiting, CORS, and authorized hosts in the same panel.

**`/mcp` exposes a single `search` tool whose name and description you control.** Reach for it before writing a custom MCP server.

Drop-in web components (search bar, Cmd+K modal, chat bubble, full-page chat) are at [search.ai.cloudflare.com](https://search.ai.cloudflare.com/), with the current versioned script URL in the instance's dashboard panel.

## Multi-environment

Bindings are per-environment. Instance names only need to be unique within a namespace, so **make the environment be the namespace and keep instance names identical across them**. `env.AI_SEARCH.get("docs")` then resolves to whichever copy the deployed environment binds, and application code stays environment-agnostic.

```toml
[[env.production.ai_search_namespaces]]
binding = "AI_SEARCH"
namespace = "production"

[[env.staging.ai_search_namespaces]]
binding = "AI_SEARCH"
namespace = "staging"
```

Give staging its own instance rather than pointing `remote: true` at production.

## See Also

- [api.md](api.md) - querying the instance you just configured
- [gotchas.md](gotchas.md) - migration traps, limits, silent failures
- [AI Search configuration docs](https://developers.cloudflare.com/ai-search/configuration/) - full option list and current defaults
