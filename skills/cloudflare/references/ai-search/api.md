# AI Search API Reference

## In This File

| You need to | Section |
|---|---|
| See create, upload, and search end to end | [Complete example](#complete-example) |
| Choose between the two bindings | [Bindings](#bindings) |
| Know what a query returns | [`search()`](#search) |
| Generate an answer instead of chunks | [`chatCompletions()`](#chatcompletions) |
| Scope results to a folder, tenant, or date | [Filters](#filters) |
| Rank fresh or high-priority content higher | [Boosting](#boosting) |
| Handle errors | [Failure surfaces](#failure-surfaces) |
| Add, list, or delete documents | [Items API](#items-api) |
| Create instances at runtime | [Instances API](#instances-api) |
| Call from outside a Worker | [Beyond the binding](#beyond-the-binding) |
| Migrate off `env.AI.autorag()` | [Old patterns](#old-patterns) |

Exact signatures and current defaults live in the ambient `AiSearchInstance` / `AiSearchNamespace` types, `npx wrangler ai-search --help`, and [the API docs](https://developers.cloudflare.com/ai-search/api/). Migration and filter traps are in [gotchas.md](gotchas.md).

## Complete Example

Create, upload, and search through the namespace binding.

```typescript
// wrangler.jsonc: { "compatibility_date": "2026-03-27",
//   "ai_search_namespaces": [{ "binding": "AI_SEARCH", "namespace": "default" }] }

interface Env { AI_SEARCH: AiSearchNamespace }

const INSTANCE = "product-docs";

export default {
  async fetch(request: Request, env: Env) {
    const url = new URL(request.url);

    // Synchronous and lazy: no network call, no validation.
    const docs = env.AI_SEARCH.get(INSTANCE);

    // One-time setup. Omitting type/source gives built-in storage.
    // create() throws if the instance already exists.
    if (url.pathname === "/setup") {
      await env.AI_SEARCH.create({ id: INSTANCE }).catch(() => {});
      return new Response("ready");
    }

    // Write. uploadAndPoll waits for indexing, so the next search sees it.
    // Check the returned status: the wait is bounded, not guaranteed.
    if (request.method === "POST") {
      const key = url.searchParams.get("key")!;
      const item = await docs.items.uploadAndPoll(key, await request.text());
      return Response.json({ key, status: item.status });
    }

    // Read.
    const { chunks } = await docs.search({
      messages: [{ role: "user", content: url.searchParams.get("q")! }],
    });

    // Zero results is a normal outcome, not an error.
    if (chunks.length === 0) return Response.json({ results: [] });

    return Response.json({
      results: chunks.map((c) => ({ source: c.item.key, text: c.text, score: c.score })),
    });
  },
} satisfies ExportedHandler<Env>;
```

`create()` is on the namespace handle only, so the per-tenant patterns in [patterns.md](patterns.md#multitenancy) need `ai_search_namespaces`.

## Bindings

| Binding | Handle type | Gives you |
|---------|-------------|-----------|
| `ai_search` | `AiSearchInstance` | One instance, fixed at deploy time |
| `ai_search_namespaces` | `AiSearchNamespace` | Every instance in a namespace, chosen at runtime |

```typescript
interface Env {
  DOCS: AiSearchInstance;        // ai_search
  TENANTS: AiSearchNamespace;    // ai_search_namespaces
}

const instance = env.TENANTS.get("tenant-abc");
```

Both handles expose `search()`, `chatCompletions()`, `info()`, `stats()`, `update()`, and `items.*`. The namespace handle adds `get()`, `list()`, `create()`, `delete()`, and cross-instance `search()`.

Binding declaration, `remote: true`, and the `compatibility_date` minimum are in [configuration.md](configuration.md#worker-setup). **If a binding is `undefined` at runtime, check the compatibility date first.**

## `search()`

```typescript
const { search_query, chunks } = await instance.search({
  messages: [{ role: "user", content: "How do I configure caching?" }],
  ai_search_options: { retrieval: { max_num_results: 8 } },
});
```

`messages` takes OpenAI-style `{ role, content }`. A bare `query: string` also works; pass one or the other, not both.

**Building an agent? Give it `search()` as a tool** rather than retrieving on every turn. See [patterns.md](patterns.md#search-as-an-agent-tool).

### Response

```typescript
{
  search_query,        // the query actually searched, after any rewriting
  chunks: [{
    id, text, score,
    item: { key, timestamp, metadata },   // key = file path or source URL
    scoring_details: { ... },             // per-signal scores and ranks
    instance_id,                          // cross-instance search only
  }],
  errors,              // cross-instance partial failures
}
```

`scoring_details` decomposes the score into vector, keyword, fusion, and reranking components. Log it before tuning anything.

### Options that carry a decision

Everything under `ai_search_options` has a working default. These are worth setting deliberately:

| Option | Set it when |
|--------|-------------|
| `retrieval.max_num_results` | Feeding a model: cap the context you hand it |
| `retrieval.match_threshold` | You would rather return nothing than something wrong (raise), or a model filters downstream (lower) |
| `retrieval.filters` | Multitenancy, folder scoping, freshness. See [Filters](#filters) |
| `retrieval.retrieval_type` | Exact strings matter. Only reads an index built at index time. See [gotchas.md](gotchas.md#retrieval-can-only-use-an-index-you-built) |
| `retrieval.context_expansion` | Chunks come back truncated mid-thought |
| `retrieval.boost_by` | Fresh or high-priority content should outrank the rest. See [Boosting](#boosting) |
| `query_rewrite.enabled` | Input is raw human text. Leave off for agent-generated queries |
| `reranking.enabled` | Right documents, wrong order. Adds a model call |
| `cache.enabled` | Benchmarking, or reading right after a reindex. Caching is **on** by default |

Full list and current defaults: [Workers binding search](https://developers.cloudflare.com/ai-search/api/search/workers-binding/).

### Cross-instance search

Namespace handle only. `instance_ids` is required; results are merged and re-ranked.

```typescript
const { chunks, errors } = await env.TENANTS.search({
  messages: [{ role: "user", content: "refund policy" }],
  ai_search_options: { instance_ids: ["product-docs", "changelog"] },
});
if (errors?.length) console.warn("partial results", errors);
```

Each chunk carries `instance_id` for attribution. Failures land in `errors` rather than throwing; see [Failure surfaces](#failure-surfaces).

## `chatCompletions()`

Retrieves and generates in one call, returning prose. Retrieval is unconditional and the prompt is not yours. Use it only when the generated answer *is* the shipped artifact; otherwise use [`search()`](#search).

```typescript
const response = await instance.chatCompletions({
  messages: [{ role: "user", content: "What is Cloudflare?" }],
  ai_search_options: { retrieval: { max_num_results: 5 } },
});
// response.choices[0].message.content, plus response.chunks in search() shape
```

OpenAI-shaped, extended with the retrieved `chunks`. `model` overrides the instance's generation model.

**Streaming emits chunks first.** With `stream: true` the stream sends a single `event: chunks` frame, then `chat.completion.chunk` deltas, then `data: [DONE]`. That ordering lets a UI render sources before the answer.

## Filters

Metadata keys with conditions, applied **before** retrieval. Both query methods take them.

```typescript
ai_search_options: {
  retrieval: {
    filters: {
      folder: "docs/getting-started/",       // bare value = implicit $eq
      timestamp: { $gte: 1735689600 },
      category: { $in: ["guides", "tutorials"] },
    },
  },
}
```

Operators: `$eq` `$ne` `$in` `$nin` `$lt` `$lte` `$gt` `$gte`. **Multiple keys are ANDed implicitly.** There is no `and` / `or` key; use `$in` for what used to be an OR over one field.

**"Starts with" needs a range query.** Bare equality matches only direct children:

```typescript
// ❌ direct children of docs/ only, misses docs/guides/intro.md
filters: { folder: "docs/" }

// ✅ whole subtree ('0' sorts after '/' in ASCII)
filters: { folder: { $gte: "docs/", $lt: "docs0" } }
```

Filterable fields are `filename`, `folder`, `timestamp`, plus custom fields declared on the instance *before* upload. See [configuration.md](configuration.md#custom-metadata).

Reference: [Filtering](https://developers.cloudflare.com/ai-search/configuration/retrieval/filtering/).

## Boosting

Filters remove candidates before retrieval; `boost_by` reorders what retrieval already found. **It cannot promote a chunk the search step missed.** Widen retrieval first, then boost.

```typescript
ai_search_options: {
  retrieval: {
    boost_by: [{ field: "timestamp", direction: "desc" }],   // newest first
  },
}
```

| `direction` | Ranks higher |
|---|---|
| `desc` | Higher values: most recent, highest priority |
| `asc` | Lower values: oldest, lowest priority |
| `exists` | Documents that have the field |
| `not_exists` | Documents missing the field. How you suppress drafts |

Three traps:

- **`asc` is the default for numeric and datetime fields**, so `{ field: "timestamp" }` with no direction boosts the *oldest* documents.
- **A per-request `boost_by` replaces the instance-level value outright.** It does not merge. `boost_by: []` turns boosting off for one call.
- **It does not appear in `scoring_details`**, so compare orderings with and without it rather than reading its contribution off a response.

Text and boolean fields accept only `exists` / `not_exists`. Boosting runs after retrieval and before reranking, so an enabled reranker can dampen it. Instance-wide defaults go under `retrieval_options` ([configuration.md](configuration.md#retrieval-options)). Reference: [Relevance boosting](https://developers.cloudflare.com/ai-search/configuration/retrieval/boosting/).

## Failure surfaces

The binding throws. Narrow on `err.name`, keyed to the upstream HTTP status:

| Status | `err.name` | Do |
|---|---|---|
| 404 | `AiSearchNotFoundError` | Fix the instance or namespace name. Do not retry |
| 5xx | `AiSearchInternalError` | Retry |
| other | `AiSearchError` | Read `message`. Do not retry blind |

**Use `err.name`, not `instanceof`.** These are type declarations, not exported runtime classes, so there is no constructor to compare against. `message` carries the AI Search error string (`ai_search_not_found`, `namespace_not_found`), and numeric codes are in [API error codes](https://developers.cloudflare.com/ai-search/troubleshooting/api-error-codes/). The legacy `AutoRAGNotFoundError` family is not thrown here.

Four failures that do **not** throw:

- **`get()` never fails.** A typo'd instance name surfaces on the first `search()`, `info()`, or `items.*` call.
- **Cross-instance search degrades.** A failed instance yields partial results plus an `errors[]` entry, message only, no numeric code.
- **Indexing failures never reach the search path.** A skipped or errored document is absent from results. `stats()` gives counts, `items.list({ status })` names the documents, and the codes are in [indexing error codes](https://developers.cloudflare.com/ai-search/troubleshooting/indexing-error-codes/).
- **Zero results is a success.** Branch on `chunks.length === 0` before prompting a model.

## Items API

Documents in an instance's built-in storage. Indexes immediately, no sync jobs.

```typescript
await instance.items.upload("faq.md", content);   // string | ArrayBuffer | ReadableStream
// metadata fields must be declared on the instance first: configuration.md#custom-metadata
await instance.items.upload("guide.pdf", buf, { metadata: { category: "onboarding" } });
const item = await instance.items.uploadAndPoll("handbook.txt", content);   // blocks until indexed
await instance.items.list({ status, search, source });
await instance.items.get(itemId).info();   // also .download(), and items.delete(itemId)
```

**Status is a state machine**: `queued` → `running` → `completed` | `error` | `skipped`, plus `outdated` when the source changed since indexing. Only `completed` items are searchable.

```typescript
// ❌ serializes the whole ingest, one round trip per file
for (const f of files) await instance.items.uploadAndPoll(f.key, f.body);

// ✅ upload, then poll once
await Promise.all(files.map((f) => instance.items.upload(f.key, f.body)));
await instance.stats();
```

## Instances API

Namespace handle only.

```typescript
const instance = env.TENANTS.get("my-instance");      // sync, lazy, unvalidated
await env.TENANTS.list({ search });
await env.TENANTS.create({ id: "knowledge-base" });   // omit type/source = built-in storage
await env.TENANTS.delete("old-docs");                 // permanent, drops all indexed data
```

`create()` requires only `id`, returns a usable handle, and **throws if the instance already exists** with no typed error to narrow on. Every ingestion, indexing, retrieval, and model setting is also a `create()` parameter, all settable later with `update()`. See [configuration.md](configuration.md).

On both handles: `info()` (full config and status), `stats()` (indexing progress, error counts), `update()`.

## Beyond the binding

Inside your own Worker, use the binding: faster, and it authenticates itself.

**REST** lives at `/accounts/{account_id}/ai-search/instances/{id}/...`, with `/ai-search/namespaces/{namespace}/...` for non-default namespaces, and takes the same body shape as the binding. **Wrangler** covers instances, namespaces, and jobs; every command takes `--json`.

```bash
npx wrangler ai-search --help
npx wrangler ai-search jobs create <NAME>     # sync an external source now
```

Both need an API token with **both** `AI Search:Edit` **and** `AI Search:Run`. Edit alone cannot query; Run alone cannot manage instances.

**Public endpoint and MCP.** Enabled per instance ([configuration.md](configuration.md#public-endpoint-and-ui-snippets)). `/mcp` exposes a single `search` tool whose name and description you control: reach for it before writing a custom MCP server.

## Old patterns

`env.AI.autorag(name).search()` and `.aiSearch()` still work indefinitely but receive no new features: no namespaces, Items API, keyword or hybrid search, boosting, cross-instance search, or `scoring_details`. REST endpoints under `/autorag/rags/{name}/` are deprecated alongside them.

Field-by-field migration mapping: [gotchas.md](gotchas.md#the-legacy-binding-trap).

## See Also

- [configuration.md](configuration.md) - creating and configuring the instance you are querying
- [patterns.md](patterns.md) - agent tools, RAG, multitenancy, tuning
- [gotchas.md](gotchas.md) - what to check when results are empty
- [AI Search API docs](https://developers.cloudflare.com/ai-search/api/) - current signatures and defaults
