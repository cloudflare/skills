---
name: browser-run
description: "Build and review Cloudflare Browser Run integrations. Load when a task needs real browser automation from Workers or agents: screenshots, PDFs, rendered HTML, Markdown extraction, crawlers, Playwright, Puppeteer, CDP sessions, Stagehand, Quick Actions, Live View, WebMCP, or browser bindings in wrangler config. Retrieve current Cloudflare docs before exact APIs, limits, pricing, or compatibility dates."
---

# Cloudflare Browser Run

Use Browser Run when a Cloudflare Worker or agent needs a real Chromium browser. Do not use it for simple API calls or static HTML scraping that `fetch()` can handle.

## Retrieval Sources

Prefer current sources before exact APIs, command flags, limits, or pricing:

| Topic | URL |
| --- | --- |
| Overview | https://developers.cloudflare.com/browser-run/ |
| Get started | https://developers.cloudflare.com/browser-run/get-started/ |
| Quick Actions | https://developers.cloudflare.com/browser-run/quick-actions/ |
| Worker binding and Wrangler | https://developers.cloudflare.com/browser-run/reference/wrangler/ |
| Wrangler browser commands | https://developers.cloudflare.com/browser-run/reference/wrangler-commands/ |
| CDP sessions | https://developers.cloudflare.com/browser-run/cdp/ |
| Playwright | https://developers.cloudflare.com/browser-run/playwright/ |
| Puppeteer | https://developers.cloudflare.com/browser-run/puppeteer/ |
| Human in the loop | https://developers.cloudflare.com/browser-run/features/human-in-the-loop/ |
| WebMCP | https://developers.cloudflare.com/browser-run/features/webmcp/ |

## Workflow

1. Classify the browser need:
   - One-shot screenshot, PDF, Markdown, HTML, links, JSON extraction, snapshot, or crawl: use Quick Actions.
   - Multi-step scripted automation: use a Browser Session with Playwright, Puppeteer, CDP, or Stagehand.
   - AI coding agent/browser control: use Browser Run through MCP/CDP or the Agents SDK browser tools.
   - A WebMCP-enabled site: prefer WebMCP tools over click/type automation when available.
2. Inspect the project: `wrangler.jsonc` or `wrangler.toml`, package manager, `wrangler` version, framework, compatibility date/flags, generated types, and existing bindings.
3. Add the Browser Run binding and regenerate types.
4. Choose the local development mode deliberately. Quick Actions through the Worker binding require remote mode; CDP/Playwright/Puppeteer workflows may have different local support.
5. Validate with `npx wrangler types`, local or remote `wrangler dev`, focused tests, and a real deployed smoke test when browser behavior matters.

## Binding Pattern

```jsonc
{
  "browser": {
    "binding": "BROWSER"
  }
}
```

Use the generated `Env` type from `npx wrangler types`; do not hand-write browser binding types.

Add Node.js compatibility flags only when the selected library requires them. Browser Run docs and examples often require current Node compatibility for Puppeteer, Playwright, or related packages.

## Quick Actions

- Use Quick Actions for common stateless jobs: screenshots, PDFs, rendered Markdown, rendered HTML, links, structured JSON, snapshots, and crawls.
- The Worker binding `.quickAction()` path requires a current compatibility date from the docs. As of the June 2026 docs, it requires `2026-03-24` or later.
- For `snapshot`, use `formats` when you need multiple outputs in one call, such as `["screenshot", "markdown", "accessibilityTree"]`. Request at least two formats; use the single-format Quick Action or endpoint when only one output is needed.
- `.quickAction()` is not supported in default local mode. Use `npx wrangler dev --remote` or set the browser binding `remote: true` for local testing of Quick Actions.
- If local calls fail with `The RPC receiver does not implement the method "quickAction"`, check remote mode and compatibility date before debugging application code.

## Browser Sessions

- Use sessions for multi-step navigation, login flows, DOM interaction, frontend debugging, and stateful automation.
- Prefer Playwright or Puppeteer when the app already uses them. Prefer CDP when you need lower-level control or MCP integration.
- Reuse sessions only when the workflow benefits from retained browser state; otherwise close sessions promptly.
- Treat Live View URLs, CDP WebSocket endpoints, and session IDs as sensitive. They can expose pages, credentials, or human interactions.
- Browser Run traffic is identified as automated/bot traffic. Do not assume sites will treat it like a normal end-user browser.

## Agent And WebMCP Patterns

- For Agents SDK browser tools, load `agents-sdk` too. Browser Run supplies the browser capability; Agents SDK supplies the agent lifecycle and chat/tooling patterns.
- For generated code that orchestrates browser actions, load `dynamic-workers` too if Worker Loader or Code Mode behavior is involved.
- For WebMCP, use lab sessions only after retrieving current limitations. Lab sessions run experimental Chrome builds and are not production browser pools.
- When WebMCP tools exist on a page, call them first and re-list tools after navigation or state changes. Fall back to DOM clicks only when no relevant structured tool exists.
- Use human-in-the-loop or Live View for MFA, confirmations, or sensitive actions that should not be fully automated.

## Gotchas

- Browser Run was formerly documented as Browser Rendering. Some API paths, examples, package names, or account features may still use `browser-rendering` terminology.
- Screenshot/PDF correctness depends on viewport, fonts, waits, auth state, media emulation, and network timing. Make these explicit in tests.
- Respect robots, terms of service, authentication boundaries, and user confirmation requirements.
- Do not put Browser Run in the critical path for simple fetchable APIs. It is heavier, slower, and more expensive than `fetch()`.
- Remote bindings can touch real Cloudflare resources and may incur cost. Call this out before enabling `remote: true`.
- Retrieve current limits and pricing before designing crawlers, concurrent sessions, or long-running browser pools.
