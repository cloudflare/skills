# AI Search Patterns

## Search as an agent tool

The [Agents SDK](../agents-sdk/) owns the loop, memory, and tool selection; AI Search is one tool it calls.

```typescript
import { Agent } from "agents";
import { tool } from "ai";
import { z } from "zod";

interface Env { AI_SEARCH: AiSearchNamespace }

export class SupportAgent extends Agent<Env> {
  searchDocs = tool({
    description:
      "Search product documentation. Use for questions about features, " +
      "configuration, limits, or error messages.",
    parameters: z.object({
      query: z.string().describe("A specific, self-contained question"),
    }),
    execute: async ({ query }) => {
      const { chunks } = await this.env.AI_SEARCH.get("product-docs").search({
        messages: [{ role: "user", content: query }],
        ai_search_options: { retrieval: { max_num_results: 8 } },
      });
      return chunks.map((c) => ({ source: c.item.key, text: c.text }));
    },
  });
}
```

**The model picks tools from the description alone.** Say what is in the index and when to reach for it.

**Return trimmed objects, not the raw response.** Every field becomes context the agent carries on every later turn. `key` and `text` are usually enough.

**Turn off query rewriting for agent-issued queries.** The agent already wrote a clean, self-contained query; rewriting adds a model call and can drift from intent. Turn it on for raw human input.

### Multiple indexes, one agent

Give the agent one tool per corpus rather than one tool with a corpus argument. The descriptions do the routing.

```typescript
searchDocs    = tool({ description: "Public product documentation.",         /* → get("docs") */ });
searchTickets = tool({ description: "Past support tickets and resolutions.", /* → get("tickets") */ });
```

If corpora overlap, use [cross-instance search](#cross-instance-search) instead.

## Multitenancy

Prefer instance-per-tenant unless tenant count makes it impractical.

### Instance per tenant (strong isolation)

Isolation comes from the instance boundary, not a filter you have to get right at every call site.

```typescript
async function searchForTenant(env: Env, tenantId: string, query: string) {
  return env.TENANTS.get(`tenant-${tenantId}`)
    .search({ messages: [{ role: "user", content: query }] });
}

// Provision on signup
await env.TENANTS.create({ id: `tenant-${tenantId}` });
await env.TENANTS.get(`tenant-${tenantId}`).items.upload("welcome.md", welcomeDoc);
```

Instances per account is a plan limit and the Paid ceiling is high; check the [platform limits](https://developers.cloudflare.com/ai-search/platform/limits-pricing/) before ruling this out on tenant count.

## Per-agent knowledge isolation

Each agent gets its own instance, created at runtime. Built-in storage indexes immediately, so this is write-then-read memory. It replaces Durable Object storage plus your own embedding calls for agent recall.

```typescript
export class ResearchAgent extends Agent<Env> {
  private get memory() {
    return this.env.AGENTS.get(`agent-${this.name}`);
  }

  async onStart() {
    await this.env.AGENTS.create({ id: `agent-${this.name}` }).catch(() => {});  // idempotent
  }

  async remember(key: string, content: string) {
    const item = await this.memory.items.uploadAndPoll(key, content);
    return item.status;   // the wait is bounded, not guaranteed
  }

  async recall(query: string) {
    const { chunks } = await this.memory.search({
      messages: [{ role: "user", content: query }],
    });
    return chunks;
  }
}
```

**Check the `status` `uploadAndPoll()` returns** rather than assuming `completed`, and degrade gracefully if it is still `running`. Use plain `upload()` when the next read does not depend on this write, and always for bulk.

## Citations

**Dedupe by `item.key`:** several chunks often come from one document.

```typescript
const sources = [...new Map(
  chunks.map((c) => [c.item.key, { key: c.item.key, score: c.score }])
).values()];
```

If you do stream `chatCompletions()`, the `event: chunks` frame arrives **before** the token deltas, so render the source list first.

## Cross-instance search

One query across several instances, merged and re-ranked.

```typescript
const { chunks, errors } = await env.AI_SEARCH.search({
  messages: [{ role: "user", content: query }],
  ai_search_options: {
    instance_ids: ["product-docs", "api-reference", "changelog"],
    retrieval: { max_num_results: 15 },
  },
});

if (errors?.length) console.warn("partial results", errors);
```

**Always check `errors`.** Failures are returned rather than thrown, so a partial result set looks identical to a complete one. Instances per query is capped; see the [limits](https://developers.cloudflare.com/ai-search/platform/limits-pricing/).

## Tuning retrieval

Reach for these in order, changing one at a time. Exhaust the levers that add nothing before adding a model call to every query.

| Symptom | Lever | Adds |
|---------|-------|------|
| Misses exact strings (error codes, IDs, flags) | Enable keyword indexing, then `retrieval_type: "hybrid"` | A reindex; a lower file ceiling |
| Misses paraphrases | Lower the match threshold | Nothing |
| Chunks relevant but truncated mid-thought | `context_expansion: 1` to `3` | Tokens downstream |
| Right documents, wrong order | `reranking: { enabled: true }` | A model call per query |
| Stale content outranks fresh | [`boost_by`](api.md#boosting) with `direction: "desc"` | Nothing |
| Too much noise | Raise the threshold, lower `max_num_results` | Nothing |
| Vague human queries | Query rewriting | A model call per query |

### Read `scoring_details` instead of guessing

```typescript
chunks.forEach((c) =>
  console.log(c.item.key, c.score, c.scoring_details.vector_score,
              c.scoring_details.keyword_score, c.scoring_details.fusion_method));
```

This tells you whether hybrid is active (`keyword_score` present and non-zero), whether the threshold is cutting good results, and whether reranking changed anything. **Disable caching while doing this** or you are reading a previous response.

### Choosing a match threshold

Read the current default off `info()` rather than assuming a number.

| Direction | Use |
|-----------|-----|
| Below default | Broad recall; agent tools, where the model filters for you |
| Around default | General-purpose starting point |
| Above default | High precision; you would rather return nothing than something wrong |

Agent tools want a lower threshold than direct-to-user results: an extra irrelevant chunk costs some context, a missing chunk costs the answer.

## See Also

- [api.md](api.md) - method signatures, filters, boosting, failure surfaces
- [configuration.md](configuration.md) - instance setup, data sources, keeping a source fresh
- [gotchas.md](gotchas.md) - what to check when results are empty
- [agents-sdk](../agents-sdk/) - the agent loop these patterns plug into
- [workers-ai](../workers-ai/) - models for the generation step you own
