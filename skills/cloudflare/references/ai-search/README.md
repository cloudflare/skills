# Cloudflare AI Search

Managed retrieval over your own content. Ingestion, chunking, embedding, storage, and ranking are handled for you; you get scored chunks back.

**Formerly AutoRAG.** `env.AI.autorag()` still works but is frozen. See [gotchas.md](./gotchas.md#the-legacy-binding-trap).

[The docs](https://developers.cloudflare.com/ai-search/) are authoritative over these files.

## Quick Start

```jsonc
// wrangler.jsonc
{
  "compatibility_date": "2026-03-27",   // or later
  "ai_search_namespaces": [{ "binding": "AI_SEARCH", "namespace": "default" }]
}
```

```typescript
interface Env { AI_SEARCH: AiSearchNamespace }

export default {
  async fetch(request, env: Env) {
    const { chunks } = await env.AI_SEARCH.get("my-instance").search({
      messages: [{ role: "user", content: "How do I configure caching?" }],
    });
    return Response.json(chunks.map((c) => ({ source: c.item.key, text: c.text })));
  },
};
```

**`compatibility_date` must be `2026-03-27` or later.** An older one is the usual cause of "the binding is undefined." Add `"remote": true` for `wrangler dev`; there is no local emulator.

## In This Reference

Read in this order.

| File | When | Covers |
|---|---|---|
| [configuration.md](./configuration.md#decide-before-you-create) | Before creating an instance | Data sources, path filtering, indexing, models, metadata. The embedding model and data source are fixed for the life of an instance |
| [api.md](./api.md) | While implementing | Bindings, `search()`, filters, boosting, Items API, failure surfaces, REST and CLI |
| [patterns.md](./patterns.md) | Designing the integration | Agent tools, RAG you own, multitenancy, agent memory, retrieval tuning |
| [gotchas.md](./gotchas.md) | Results are empty or wrong | Migration traps, silent failures, limits, error codes |

## Default to `search()`

`search()` returns scored chunks. `chatCompletions()` runs a model over those chunks inside AI Search and returns prose.

Use `chatCompletions()` only when the generated answer *is* the shipped artifact: an embedded FAQ box, a public endpoint. Everywhere else use `search()` and generate yourself. `chatCompletions()` exposes only `model:`, so you get no control over the prompt, no tool calling, no multi-turn state, and no chance to filter or dedupe chunks before generation.

## Building an agent? Use the Agents SDK

**The Agents SDK owns the loop; AI Search is one tool it calls.** An agent built on `chatCompletions()` has no memory, no tools, and no loop.

```typescript
searchDocs = tool({
  description: "Search the product documentation.",
  parameters: z.object({ query: z.string() }),
  execute: async ({ query }) => {
    const { chunks } = await this.env.AI_SEARCH.get("product-docs").search({
      messages: [{ role: "user", content: query }],
    });
    return chunks.map((c) => ({ source: c.item.key, text: c.text }));
  },
});
```

Full example in [patterns.md](./patterns.md#search-as-an-agent-tool). See [agents-sdk](../agents-sdk/).

## Object Model

```
Account → Namespace → Instance → Items
```

The **instance** is the searchable unit. Names collide only within a namespace, so `docs` can exist in both `blog` and `support`. A `default` namespace always exists.

**An instance is an ordinary API object, not provisioned infrastructure.** `create()` is a normal call and the per-account ceiling is high, so one instance per tenant or per agent is viable, and usually better than one shared index filtered by `tenantId`. See [patterns.md](./patterns.md#multitenancy).

## Two Bindings

| Binding | Access | Use when |
|---------|--------|----------|
| `ai_search_namespaces` | Every instance in a namespace | **Default.** Runtime instance choice, `create()` / `list()` / `delete()`, cross-instance search, per-tenant isolation |
| `ai_search` | One instance, fixed at deploy time | The Worker only ever reads one instance that already exists |

The namespace handle is a strict superset; switching to it later means a config change, a code change, and a redeploy. See [api.md](./api.md#bindings).

## Search Modes

| Mode | Finds | To use it |
|------|-------|-----------|
| `vector` | Semantic: "how to ship my app" matches "deployment guide" | On by default |
| `keyword` | Exact terms via BM25: `ERR_CONNECTION_REFUSED` | Enable `index_method.keyword` |
| `hybrid` | Both, fused | Enable both index methods |

New instances index **vector only**. Querying with `retrieval_type: "hybrid"` requires both index methods enabled at index time, which triggers a full reindex and lowers the file ceiling. See [gotchas.md](./gotchas.md#retrieval-can-only-use-an-index-you-built).

## Data Sources

An instance combines built-in storage with at most one external source. Pick by where the content already lives.

| Content lives | Use | Freshness |
|---|---|---|
| Nowhere yet, or you own the write path | **Built-in storage** | Immediate, per file |
| An R2 bucket already | **R2** | Hours-scale sync |
| A website you own | **Crawl** | Hours-scale sync |

Built-in storage indexes each file as it arrives through the [Items API](./api.md#items-api), so write-then-read works. That makes AI Search usable as agent memory: see [patterns.md](./patterns.md#per-agent-knowledge-isolation).

Details in [configuration.md](./configuration.md#data-sources).

## When to Use Something Else

**Skip AI Search when** the corpus is small and structured enough that ordinary querying wins: a few dozen rows in [d1](../d1/), exact-key lookup in [kv](../kv/). Semantic retrieval is the wrong tool for "fetch the record with this ID."

**Use [vectorize](../vectorize/) instead when** you need your own chunking or embeddings, or vectors not derived from documents (image embeddings, user-preference vectors, recommendation features).

| | AI Search | Vectorize |
|---|---|---|
| Chunking and embedding | Managed | Yours |
| Keyword/BM25 and hybrid fusion | Built in | Not available |
| Reranking, query rewriting, caching | Built in, toggleable | Yours to build |
| Ingest | Text, code, PDF, Office, images | Vectors only |

Limits that shape a design are in [gotchas.md](./gotchas.md#limits). Do not pin numbers from memory.

## See Also

- [AI Search docs](https://developers.cloudflare.com/ai-search/) - full option lists and current defaults
- [llms.txt](https://developers.cloudflare.com/ai-search/llms.txt) - index of every doc page, for retrieval
- [agents-sdk](../agents-sdk/) - the right home for agent loops
- [vectorize](../vectorize/) - the unmanaged alternative
- [workers-ai](../workers-ai/) - models for your own generation step
- [ai-gateway](../ai-gateway/) - routing and observability for model calls
