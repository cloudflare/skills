# Code Mode API Reference

## `createCodeTool(options)`

Creates an AI SDK compatible tool that wraps all provided tools into a single "write code" tool.

**Import:** `@cloudflare/codemode/ai`

```typescript
import { createCodeTool } from "@cloudflare/codemode/ai";

const codemode = createCodeTool({ tools, executor });
```

### Options

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `tools` | `ToolSet \| ToolDescriptors` | Yes | — | AI SDK tools or raw tool descriptors |
| `executor` | `Executor` | Yes | — | Code execution environment |
| `description` | `string` | No | Auto-generated | Custom tool description. Supports `{{types}}` placeholder for injecting generated TypeScript declarations |

### Return Value

Returns an AI SDK `Tool<{ code: string }, { code: string; result: unknown; logs?: string[] }>`.

**Input schema:** `{ code: string }` — a JavaScript async arrow function.

**Output:** `{ code, result, logs }` where:
- `code` — the normalized code that was executed
- `result` — the return value of the async arrow function
- `logs` — captured `console.log/warn/error` output from the sandbox

### Behavior

1. Filters out tools with `needsApproval` (not supported in sandbox execution)
2. Calls `generateTypes()` to produce TypeScript declarations for all tools
3. Injects types into the tool description (replaces `{{types}}` placeholder)
4. On execution: normalizes code via acorn, extracts tool execute functions, calls `executor.execute()`

### Default Description Template

```text
Execute code to achieve a goal.

Available:
{{types}}

Write an async arrow function that returns the result.
Do NOT define named functions then call them — just write the arrow function body directly.

Example: async () => { const r = await codemode.searchWeb({ query: "test" }); return r; }
```

---

## `DynamicWorkerExecutor`

Executes code in isolated Cloudflare Workers (V8 isolates).

**Import:** `@cloudflare/codemode`

```typescript
import { DynamicWorkerExecutor } from "@cloudflare/codemode";

const executor = new DynamicWorkerExecutor({
  loader: env.LOADER,
  timeout: 30000,
  globalOutbound: null,
});
```

### Options

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `loader` | `WorkerLoader` | Yes | — | Cloudflare WorkerLoader binding from wrangler config |
| `timeout` | `number` | No | `30000` | Execution timeout in milliseconds |
| `globalOutbound` | `Fetcher \| null` | No | `null` | Network access control. `null` = blocked, `Fetcher` = routed |

### `execute(code, fns)`

```typescript
async execute(
  code: string,
  fns: Record<string, (...args: unknown[]) => Promise<unknown>>
): Promise<ExecuteResult>
```

**Parameters:**
- `code` — JavaScript async arrow function as a string
- `fns` — Map of tool name to execute function

**Returns:** `ExecuteResult`

### Execution Flow

1. Generates a complete ES module wrapping the code in a `WorkerEntrypoint`
2. Overrides `console.log/warn/error` into a `__logs` array
3. Creates a `codemode` Proxy that intercepts all property access
4. `codemode.toolName(args)` calls route through `dispatcher.call()` via Workers RPC
5. Spins up an isolated Worker via `WorkerLoader.get()` with `nodejs_compat`
6. Calls `entrypoint.evaluate(dispatcher)` via Workers RPC
7. Returns `{ result, error?, logs? }`

---

## `Executor` Interface

The abstract interface for code execution environments. Implement this to create custom sandboxes.

```typescript
interface Executor {
  execute(
    code: string,
    fns: Record<string, (...args: unknown[]) => Promise<unknown>>
  ): Promise<ExecuteResult>;
}
```

Contract: implementations should never throw. Errors go into `ExecuteResult.error`.

---

## `ExecuteResult`

```typescript
interface ExecuteResult {
  result: unknown;   // Return value of the async arrow function
  error?: string;    // Error message if execution failed
  logs?: string[];   // Captured console output
}
```

---

## `ToolDispatcher`

RPC target that the sandboxed Worker calls back into for tool execution. Extends `RpcTarget`.

```typescript
import { ToolDispatcher } from "@cloudflare/codemode";
```

### `call(name, argsJson)`

```typescript
async call(name: string, argsJson: string): Promise<string>
```

- Parses JSON args, invokes matching function, returns JSON-serialized result
- Returns `{ error: "Tool not found" }` for unknown tools
- Catches exceptions and returns `{ error: message }` — never throws

---

## `generateTypes(tools)`

Generates TypeScript type declarations from tool schemas for inclusion in LLM prompts.

**Import:** `@cloudflare/codemode`

```typescript
import { generateTypes } from "@cloudflare/codemode";

const types = generateTypes(myTools);
// Returns string with type aliases and `declare const codemode: { ... }`
```

**Output format:**
- Named type aliases: `{ToolName}Input`, `{ToolName}Output`
- JSDoc comments from tool descriptions and Zod field descriptions
- `declare const codemode: { toolName(input: ToolNameInput): Promise<ToolNameOutput>; ... }`

Uses `zod-to-ts` to convert Zod schemas into TypeScript AST nodes.

---

## `sanitizeToolName(name)`

Converts tool names to valid JavaScript identifiers.

**Import:** `@cloudflare/codemode`

```typescript
import { sanitizeToolName } from "@cloudflare/codemode";
```

**Rules:**
- Replaces `-`, `.`, spaces with `_`
- Strips non-identifier characters
- Prefixes with `_` if starts with a digit
- Appends `_` to JavaScript reserved words
- Falls back to `_` for empty strings

**Examples:**

| Input | Output |
|-------|--------|
| `"get-weather"` | `"get_weather"` |
| `"my-server.list-items"` | `"my_server_list_items"` |
| `"3d-render"` | `"_3d_render"` |
| `"delete"` | `"delete_"` |
| `"hello world"` | `"hello_world"` |

---

## `ToolDescriptor`

Raw tool descriptor shape (alternative to AI SDK's `tool()` format).

```typescript
interface ToolDescriptor {
  description?: string;
  inputSchema: ZodType;
  outputSchema?: ZodType;
  execute?: (args: unknown) => Promise<unknown>;
}

type ToolDescriptors = Record<string, ToolDescriptor>;
```

Both `ToolDescriptors` and AI SDK's `ToolSet` are accepted by `createCodeTool` and `generateTypes`.

---

## `normalizeCode(code)` (Internal)

Parses LLM output with acorn and normalizes it into a valid async arrow function:

- Empty input → `async () => {}`
- Single arrow function expression → passes through
- Statements ending with expression → wraps in `async () => { ... return (lastExpr) }`
- Multiple statements → wraps in `async () => { ... }`
- Parse failure → wraps blindly in `async () => { ... }`

This handles various LLM code formats gracefully.
