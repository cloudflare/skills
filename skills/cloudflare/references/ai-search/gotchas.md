# AI Search Gotchas

## The legacy binding trap

Most AI Search code in circulation, including model pretraining, predates the current API. `env.AI.autorag(...)`, `aiSearch()`, a `data[]` response, or `{ type, key, value }` filters are all the legacy AutoRAG surface. It works indefinitely but receives no new features: no namespaces, Items API, hybrid search, boosting, cross-instance search, or `scoring_details`.

| Legacy | Current |
|--------|---------|
| `"ai": { "binding": "AI" }` | `ai_search` or `ai_search_namespaces` binding |
| `env.AI.autorag("name")` | `env.MY_SEARCH` or `env.AI_SEARCH.get("name")` |
| `aiSearch()` | `chatCompletions()`, but prefer `search()` |
| `query: "..."` | `messages: [{ role, content }]` (`query` still accepted) |
| `data[]` | `chunks[]` |
| `data[].file_id` | `chunks[].id` |
| `data[].filename` | `chunks[].item.key` |
| `data[].content[].text` | `chunks[].text` |
| `data[].attributes.modified_date` | `chunks[].item.timestamp` |
| top-level `filters` | `ai_search_options.retrieval.filters` |
| `eq` / `gte` / `and` / `or` | `$eq` / `$gte`, implicit AND, no compound keys |
| `ranking_options.score_threshold` | `retrieval.match_threshold` per request, `score_threshold` on the instance |
| `hybrid_search_enabled` | `index_method: { vector, keyword }` (the old flag is deprecated) |
| `env.AI.autorag("_").listInstances()` | `env.AI_SEARCH.list()` |
| `/autorag/rags/{name}/ai-search` | `/ai-search/instances/{id}/search` |
| `AutoRAGNotFoundError` etc. | `AiSearchNotFoundError` / `AiSearchInternalError` / `AiSearchError`, narrowed on `err.name` |

## Common Errors

Symptoms that arrive with no error code. If you have a code, look it up rather than inferring it from the name: [API error codes](https://developers.cloudflare.com/ai-search/troubleshooting/api-error-codes/) for request-time and public endpoint failures, [indexing error codes](https://developers.cloudflare.com/ai-search/troubleshooting/indexing-error-codes/) for anything asynchronous.

### "The binding is undefined"

`compatibility_date` is below `2026-03-27`. That is the cause far more often than the binding declaration. You also need a recent `wrangler` and `@cloudflare/workers-types`; if types do not resolve, check whether `AiSearchInstance` exists in your installed version before assuming the config is wrong.

### "My folder filter returns nothing"

`{ folder: "docs/" }` is an equality check. It matches files directly in `docs/`, not `docs/guides/intro.md`.

```typescript
// ❌ direct children only
filters: { folder: "docs/" }

// ✅ whole subtree ('0' sorts after '/' in ASCII)
filters: { folder: { $gte: "docs/", $lt: "docs0" } }
```

### "There is no `and` / `or` operator"

Multiple keys are ANDed implicitly. There are no compound operators. Use `$in` for an OR over one field.

```typescript
// ❌ legacy
{ operator: "or", filters: [ ... ] }

// ✅ current
filters: { folder: { $in: ["docs/guides/", "docs/tutorials/"] } }
filters: { folder: "docs/api/", timestamp: { $gte: 1735689600 } }   // AND
```

Operators are `$`-prefixed: `$eq` `$ne` `$in` `$nin` `$lt` `$lte` `$gt` `$gte`. Reference: [Filtering](https://developers.cloudflare.com/ai-search/configuration/retrieval/filtering/).

### "My timestamp filter matches nothing"

Your filter value and `item.timestamp` must be in the same unit. Read the unit off a real response before filtering.

```typescript
console.log(chunks[0]?.item.timestamp);   // 10 digits = seconds, 13 = milliseconds
```

### "My custom metadata filter never matches"

Metadata keys not declared on the instance are not indexed and cannot be filtered on. This fails silently: the upload succeeds, the filter just never matches.

```typescript
await instance.update({
  custom_metadata: [{ field_name: "category", data_type: "text" }],
});
// only now is this filterable
await instance.items.upload("guide.pdf", buf, { metadata: { category: "onboarding" } });
```

Adding a field later does not backfill already-indexed items; reupload or resync them.

### "`get()` succeeded but `search()` throws"

`env.AI_SEARCH.get("typo-name")` is synchronous and makes no network call, so you get a handle for an instance that may not exist. The error surfaces on the first `search()` / `info()` / `items.*` call. **Do not treat a successful `get()` as existence.**

### "REST or Wrangler returns a permission error"

The token needs **both** `AI Search:Edit` **and** `AI Search:Run`. Edit alone cannot query; Run alone cannot manage instances. The old "AI Search - Read" permission name is gone. Workers bindings authenticate themselves.

## Retrieval can only use an index you built

Two settings, at two different times:

- **Index time**, `index_method` on the instance: which indexes get built.
- **Retrieval time**, `retrieval_type` on the request: which of them a query reads.

**To query with `retrieval_type: "hybrid"`, enable both `vector` and `keyword` at index time.** Same for `keyword` on its own. A query cannot read an index that was never built, and new instances build vector only.

```typescript
await instance.update({ index_method: { vector: true, keyword: true } });
```

Changing `index_method` triggers a full reindex, and neither `keyword` nor `hybrid` returns a single keyword match until it finishes. Confirm it is live by reading `scoring_details.keyword_score` off a real query.

## Limits

**Do not pin numeric limits from memory or from these files.** Read the [platform limits](https://developers.cloudflare.com/ai-search/platform/limits-pricing/). The ones that change a design:

| Limit | What it decides |
|-------|-----------------|
| Files per instance | One big instance or many small ones. **Lower with hybrid search**, see below |
| Instances per account | Whether instance-per-tenant is viable at your scale |
| Max file size | Which source files need splitting before upload |
| Instances per cross-instance search | How wide a federated query can go |
| Custom metadata field count | Small, and fields must be declared before upload |
| Queries per month on Free | The limit you hit first while prototyping |

### Hybrid search lowers the file ceiling

**An instance holds fewer files with hybrid search than with vector alone** `update()` accepts the change without warning, and the shortfall appears as documents that stop getting indexed once the reindex passes the lower ceiling. Hybrid is a capacity decision, not only a relevance one.

- A corpus sized against the vector-only ceiling may not fit once hybrid is on. Check `stats()` against the current limits first.
- If you need both hybrid and the full ceiling, split the corpus across instances and use [cross-instance search](api.md#cross-instance-search).

## Silent failures

**Response caching is on by default**, matching on similarity rather than exact text. Reindexing does not immediately change answers, and retrieval benchmarks measure the cache, so tuning appears to do nothing. Turn it off while tuning, and check whether similarity hits can cross tenants before relying on it for per-tenant content.

```typescript
ai_search_options: { cache: { enabled: false } }
```

**Indexing problems are invisible from a query.** A skipped or errored document is absent from results, and an oversized or unsupported file is skipped without an error.

```typescript
await instance.stats();                            // counts by state, embedding errors
await instance.items.list({ status: "error" });    // each carries an error code
await instance.items.list({ status: "skipped" });  // filtered out or unsupported
```

**Check whether the code is item-level or instance-level before debugging the document.** Item-level codes (`over_size`, `unsupported_type`, `blocked_by_robots_txt`) fail one item. Instance-level codes (`bucket_unauthorized`, `external_source_missing_api_token`, `hybrid_search_is_full`) **pause indexing for the whole instance**. Both tiers are listed in [indexing error codes](https://developers.cloudflare.com/ai-search/troubleshooting/indexing-error-codes/).

**`retrieval.return_on_failure` defaults to true**, so a retrieval failure returns empty results instead of throwing. Zero chunks can mean the query failed, not that nothing matched.

A crawl that indexes nothing is usually bot protection rather than your path patterns: allow the `Cloudflare-AI-Search` user agent, renamed from `Cloudflare-AutoRAG`.

## Debugging empty results

In order, each step ruling out a class of cause.

1. `stats()`: is anything `completed`? If everything is `queued`, you are just early.
2. Drop `filters` entirely and rerun. If results appear, it is the filter; check the folder prefix trick above.
3. Lower the match threshold substantially. If results appear, it is tuning, not indexing.
4. Disable cache in case you are reading a stale empty result.
5. Inspect `scoring_details` on whatever does come back to see which retrieval path fired.
6. For cross-instance search, check `errors[]`: a failed instance returns partial results, not an exception.

## Anti-patterns

**Do not build agents on `chatCompletions()`.** No memory, no tools, no loop. Use the [Agents SDK](../agents-sdk/) with `search()` as a tool. See [patterns.md](patterns.md#search-as-an-agent-tool).

**Do not skip the zero-chunk check.** If `chunks.length === 0`, return "I don't know" rather than prompting a model with empty context.

**Do not apply the tenant filter at call sites.** Wrap it in one helper that requires `tenantId`, or use one instance per tenant. A single unfiltered `search()` is a cross-tenant leak.

**Do not `uploadAndPoll()` in a bulk loop.** It serializes the whole ingest. Use `upload()` and poll `stats()` once.

**Do not enable reranking and query rewriting by reflex.** Each is a model call on every query. Turn them on because `scoring_details` showed you a problem they solve.

## See Also

- [api.md](api.md) - filters, boosting, and failure surfaces in full
- [configuration.md](configuration.md) - the settings behind these traps
- [API error codes](https://developers.cloudflare.com/ai-search/troubleshooting/api-error-codes/) - request-time and public endpoint failures
- [Indexing error codes](https://developers.cloudflare.com/ai-search/troubleshooting/indexing-error-codes/) - asynchronous sync and crawl failures, item and instance level
- [AI Search docs](https://developers.cloudflare.com/ai-search/) - authoritative over this file
