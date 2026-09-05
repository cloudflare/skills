# Browse the Web With Agents SDK Browser Tools

Fetch https://developers.cloudflare.com/agents/tools/browser/ and https://developers.cloudflare.com/browser-run/ for complete documentation.

Use this reference for the Agents SDK browser tool surface from `agents/browser/ai`. It wires Browser Run and a Worker Loader into an Agent so the model can run durable CDP code and, by default, stateless Browser Run Quick Actions.

Load `browser-run` for Browser Run-only work such as direct Playwright, Puppeteer, raw CDP sessions, Stagehand, WebMCP, REST Quick Actions, limits, and pricing. Load `dynamic-workers` when changing Worker Loader or Code Mode internals beyond the browser tool setup.

## Setup

Browser tools must be created inside a Durable Object, such as an Agent, because the durable runtime facet and browser session store live on `this.ctx`.

```jsonc
// wrangler.jsonc
{
  "browser": { "binding": "BROWSER" },
  "worker_loaders": [{ "binding": "LOADER" }],
  "compatibility_flags": ["nodejs_compat"]
}
```

Export the durable Code Mode runtime unless the `@cloudflare/codemode/vite` plugin already does it for the app:

```typescript
export { CodemodeRuntime } from "agents/browser";
```

## Usage with AI SDK

```typescript
import { AIChatAgent } from "@cloudflare/ai-chat";
import { openai } from "@ai-sdk/openai";
import { createBrowserTools } from "agents/browser/ai";
import { convertToModelMessages, stepCountIs, streamText } from "ai";

export class MyAgent extends AIChatAgent<Env> {
  async onChatMessage() {
    const browserTools = createBrowserTools({
      ctx: this.ctx,
      browser: this.env.BROWSER,
      loader: this.env.LOADER,
      session: { mode: "dynamic" }
    });

    const result = streamText({
      model: openai("gpt-4o"),
      system: "You can inspect web pages with browser tools.",
      messages: await convertToModelMessages(this.messages),
      tools: browserTools,
      stopWhen: stepCountIs(10)
    });
    return result.toUIMessageStreamResponse();
  }
}
```

## Available Tools

| Tool | Purpose |
|------|---------|
| `browser_execute` | Run sandboxed code against a live browser over CDP |
| `browser_markdown` | Read a page or raw HTML as Markdown |
| `browser_extract` | Extract structured data from a page with AI |
| `browser_links` | List links on a page |
| `browser_scrape` | Scrape elements by CSS selector |

`browser_execute` gives the model a `cdp` connector. Generated code can call `cdp.send()`, `cdp.spec()`, `cdp.getLiveViewUrl()`, and the session helpers enabled by the selected session mode.

## Fit

- Need a real browser (JS rendering, screenshots, interaction) → browser tools
- Just need HTML/API data → use `fetch()` instead (faster, cheaper)
- Need direct Browser Run integrations outside Agents SDK tools → load `browser-run`
- Need Worker Loader or Code Mode internals → load `dynamic-workers`

## Options

```typescript
createBrowserTools({
  ctx: this.ctx,
  browser: this.env.BROWSER,
  loader: this.env.LOADER,
  session: { mode: "dynamic" }, // or { mode: "reuse", key: "main" }
  quickActions: { maxChars: 20_000 } // or false to expose only browser_execute
});
```

- `one-shot` is the default: each `browser_execute` run gets a fresh session.
- `dynamic` lets the model promote a session with `cdp.startSession()` so later executions continue in the same browser.
- `reuse` keeps a named shared session until explicitly closed or swept.
- Quick Action tools need only the `browser` binding and are included by default when `browser` is present.

For Quick Action-only agents:

```typescript
import { createQuickActionTools } from "agents/browser/ai";

const tools = createQuickActionTools({ browser: this.env.BROWSER });
```

## Safety Notes

- Treat Live View URLs, CDP endpoints, browser session IDs, screenshots, and recordings as sensitive.
- Use human-in-the-loop or Live View for MFA, CAPTCHA, and sensitive confirmations.
- Quick Actions require a current compatibility date and `remote: true` for local `wrangler dev`; retrieve current Browser Run docs before debugging local binding behavior.
- Browser Run was formerly Browser Rendering, so older examples may mix names or API paths.
