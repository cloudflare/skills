# Think (Experimental)

## Contents
- Minimal Agent
- Wrangler Config
- Custom Tools
- Agent Skills
- Messengers
- Scheduled Tasks
- Think Workflows
- Lifecycle Hooks
- Sub-Agents
- Client
- Think vs AIChatAgent


Fetch https://developers.cloudflare.com/agents/harnesses/think/ for complete documentation.

`@cloudflare/think` — a higher-level chat agent class that handles the `streamText` loop, tool execution, and message persistence for you. You provide `getModel()` and `getSystemPrompt()`; Think handles the rest.

```bash
npm install @cloudflare/think
```

## Minimal Agent

```typescript
import { Think } from "@cloudflare/think";
import { createWorkersAI } from "workers-ai-provider";
import { routeAgentRequest } from "agents";

export class MyAgent extends Think<Env> {
  getModel() {
    return createWorkersAI({ binding: this.env.AI })("@cf/meta/llama-4-scout-17b-16e-instruct");
  }

  getSystemPrompt() {
    return "You are a helpful assistant.";
  }
}

export default {
  fetch: (req, env) => routeAgentRequest(req, env)
};
```

## Wrangler Config

```jsonc
{
  "compatibility_flags": ["nodejs_compat"],
  "durable_objects": {
    "bindings": [{ "name": "MyAgent", "class_name": "MyAgent" }]
  },
  "migrations": [{ "tag": "v1", "new_sqlite_classes": ["MyAgent"] }],
  "ai": { "binding": "AI" }
}
```

Some older Think examples used the `experimental` compatibility flag. Retrieve current docs before adding or removing compatibility flags for the specific Think features in use.

## Custom Tools

```typescript
import { tool } from "ai";
import { z } from "zod";

export class MyAgent extends Think<Env> {
  getTools() {
    return {
      getWeather: tool({
        description: "Get weather",
        parameters: z.object({ city: z.string() }),
        execute: async ({ city }) => `72°F in ${city}`
      })
    };
  }
}
```

## Agent Skills

Agent Skills are experimental. They let Think expose on-demand skill activation, resource reads, and optional scripts without placing every instruction in the base prompt.

```typescript
import { Think, skills } from "@cloudflare/think";
import bundledSkills from "agents:skills";

export class MyAgent extends Think<Env> {
  getSkills() {
    return [
      bundledSkills,
      skills.r2(this.env.SKILLS_BUCKET, { prefix: "skills/" })
    ];
  }
}
```

`agents:skills` bundles a local `./skills` directory through the Agents Vite plugin. Skills can also load from R2 or a manifest. When skills are available, Think can expose tools such as `activate_skill`, `read_skill_resource`, and `run_skill_script`. Treat script execution as early API surface and retrieve current docs before enabling it.

## Messengers

Think can own chat-provider webhook routing, conversation mapping, durable reply fibers, and streamed delivery. Telegram is the first built-in provider.

```typescript
import { defineMessengers, ThinkMessengerStateAgent } from "@cloudflare/think/messengers";
import telegramMessenger from "@cloudflare/think/messengers/telegram";

export { ThinkMessengerStateAgent };

export class SupportAgent extends Think<Env> {
  getMessengers() {
    return defineMessengers({
      telegram: telegramMessenger({
        token: this.env.TELEGRAM_BOT_TOKEN,
        userName: "support_bot",
        secretToken: this.env.TELEGRAM_WEBHOOK_SECRET_TOKEN
      })
    });
  }
}
```

Keep provider tokens in secrets. Verify webhook secrets and conversation routing before enabling public providers.

## Scheduled Tasks

Use `defineScheduledTasks()` for recurring, timezone-aware prompts and handlers. Think reconciles declarations on startup and re-arms the next occurrence with durable idempotent submissions.

```typescript
import { defineScheduledTasks } from "@cloudflare/think";

getScheduledTasks() {
  return defineScheduledTasks({
    weeklyDigest: {
      schedule: "every week on monday at 09:00",
      prompt: "Compile the last week's activity into a digest."
    }
  });
}
```

## Think Workflows

Use `ThinkWorkflow` when a Workflow step should run a durable model turn with typed structured output, long waits, tools, or approval gates.

```typescript
import { z } from "zod";
import { ThinkWorkflow } from "@cloudflare/think/workflows";

const draftSchema = z.object({ title: z.string(), labels: z.array(z.string()) });

export class TriageWorkflow extends ThinkWorkflow<TriageAgent, Params> {
  async run(event, step) {
    const draft = await step.prompt("triage-issue", {
      prompt: `Triage issue #${event.payload.issueNumber}`,
      output: draftSchema,
      timeout: "3 days"
    });

    await step.do("apply-labels", async () => {
      await this.agent.applyLabels(draft.labels);
    });
  }
}
```

Current `step.prompt()` runs a full agentic turn before returning structured output, so the agent can call tools before producing the typed result.

## Lifecycle Hooks

| Hook | When | Use for |
|------|------|---------|
| `configureSession()` | Agent starts | Set up memory, context providers |
| `beforeTurn(ctx)` | Before each LLM call | Per-turn model/tools/system prompt; return `TurnConfig` |
| `onChunk(chunk)` | Each streaming chunk | Progress tracking |
| `onChatResponse(result)` | After LLM turn completes | Chaining, follow-up `saveMessages` |
| `onChatError(error)` | On LLM error | Error handling |

```typescript
async beforeTurn(ctx: TurnContext): Promise<TurnConfig> {
  if (ctx.continuation) {
    return { model: cheaperModel };
  }
  return {};
}
```

## Sub-Agents

```typescript
const child = this.subAgent(SpecialistAgent, "specialist-1");
await child.chat("Analyze this data...", (chunk) => {
  // stream callback
});
```

Think sub-agents can also receive caller-provided client tools over RPC:

```typescript
await child.chat(message, callback, {
  clientTools: [{
    name: "get_user_timezone",
    description: "Get the caller's timezone",
    parameters: { type: "object" }
  }],
  onClientToolCall: async ({ toolName, input }) => runClientTool(toolName, input)
});
```

## Client

Same React hooks as `AIChatAgent`:

```tsx
const agent = useAgent({ agent: "MyAgent", name: "session-1" });
const { messages, input, handleInputChange, handleSubmit } = useAgentChat({ agent });
```

## Think vs AIChatAgent

| | Think | AIChatAgent |
|-|-------|-------------|
| `streamText` loop | Built-in | You write it |
| Tool execution | Automatic | You wire it |
| Customization | Override hooks | Full control in `onChatMessage` |
| Built-in tools | Workspace, execute, browser | None |
| Compatibility flag | Retrieve current docs | Standard |
