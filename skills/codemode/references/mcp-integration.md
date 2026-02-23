# MCP Integration Patterns

## Merging MCP Tools with Standard Tools

MCP tools integrate seamlessly with Code Mode. Merge them into the tools object:

```typescript
const codemode = createCodeTool({
  tools: {
    ...myLocalTools,
    ...this.mcp.getAITools(),
  },
  executor,
});
```

All MCP tool names are automatically sanitized to valid JavaScript identifiers via `sanitizeToolName()`.

## Tool Name Sanitization

MCP servers often use namespaced tool names with hyphens and dots. These are converted:

```typescript
import { sanitizeToolName } from "@cloudflare/codemode";

// MCP tools like "github.list-repos" become "github_list_repos"
// The LLM writes: codemode.github_list_repos({ owner: "cloudflare" })
```

The type generation step uses sanitized names, so the LLM sees valid identifiers in the TypeScript declarations.

## Multi-Server Orchestration

Code Mode excels when composing tools from multiple MCP servers in a single execution:

```javascript
// LLM generates code that orchestrates across servers:
async () => {
  // Query filesystem MCP
  const files = await codemode.fs_list_files({ path: "/projects" });

  // Query database MCP
  const records = await codemode.db_query({
    query: "SELECT * FROM projects WHERE name = ?",
    params: [files[0].name],
  });

  // Conditional logic across servers
  if (records.length === 0) {
    await codemode.tasks_create({
      title: `Review: ${files[0].name}`,
      priority: "high",
    });
  }

  return { files: files.length, records: records.length };
};
```

Without Code Mode, this would require 3+ LLM round-trips. With Code Mode, it's a single tool call.

## Token Comparison

| Approach | Token Cost | Round Trips |
|----------|-----------|-------------|
| Traditional MCP (90 tools loaded) | ~70K at startup | N per workflow |
| Code Mode with search | ~1K fixed + ~800 per search | 1 per workflow |
| Code Mode with merged tools | ~2K fixed (tool definition) | 1 per workflow |

## Server-Side Code Mode (Cloudflare MCP Pattern)

For exposing large APIs (like the Cloudflare API with 2,500+ endpoints), the server-side Code Mode pattern uses two tools:

1. **`search()`** — Queries the OpenAPI spec through code execution
2. **`execute()`** — Performs authenticated API operations

```javascript
// search: Agent explores the API
async () => {
  const results = [];
  for (const [path, methods] of Object.entries(spec.paths)) {
    if (path.includes("/zones/") && path.includes("dns")) {
      for (const [method, op] of Object.entries(methods)) {
        results.push({ method: method.toUpperCase(), path, summary: op.summary });
      }
    }
  }
  return results;
};

// execute: Agent calls the discovered endpoints
async () => {
  const zones = await cloudflare.request({
    method: "GET",
    path: "/zones",
  });
  const records = await cloudflare.request({
    method: "GET",
    path: `/zones/${zones.result[0].id}/dns_records`,
  });
  return records.result.map((r) => ({ name: r.name, type: r.type, content: r.content }));
};
```

This reduces ~1.17M tokens (traditional one-tool-per-endpoint MCP) to ~1K tokens.

## Best Practices

- **Merge all relevant tools** before creating the code tool — the LLM can compose across any tools it sees
- **Use descriptive tool names and descriptions** — the LLM relies on these to generate correct code
- **Keep tool granularity fine** — Code Mode handles composition, so tools can be atomic
- **Monitor generated code quality** — depends on prompt engineering and model capability
- **Set appropriate timeouts** — multi-server orchestration may need longer than the 30s default
