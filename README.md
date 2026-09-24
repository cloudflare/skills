# Cloudflare Skills

A collection of [Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) for building on Cloudflare, Workers, the Agents SDK, and the wider Cloudflare Developer Platform.

## Installing

These skills work with any agent that supports the Agent Skills standard, including Claude Code, Cursor, Droid, OpenCode, OpenAI Codex, and Pi.

Use the native plugin where supported to install both Cloudflare guidance and the Cloudflare MCP server. Agents that only support the Agent Skills standard can install the skills separately.

### Codex

Install from the Cloudflare plugin marketplace:

```sh
codex plugin marketplace add cloudflare/skills
codex plugin add cloudflare@cloudflare
```

Start a new Codex session after installation.

### Claude Code

Install using the [plugin marketplace](https://code.claude.com/docs/en/discover-plugins#add-from-github):

```
/plugin marketplace add cloudflare/skills
/plugin install cloudflare@cloudflare
```

### VS Code / GitHub Copilot

Install directly from this repository:

1. Enable `chat.plugins.enabled` in VS Code settings.
2. Open the Command Palette and run **Chat: Install Plugin From Source**.
3. Enter `https://github.com/cloudflare/skills`.

For marketplace installation or troubleshooting, see [VS Code's agent plugin documentation](https://code.visualstudio.com/docs/agent-customization/agent-plugins).

### Cursor

Install from the Cursor Marketplace or add manually via **Settings > Rules > Add Rule > Remote Rule (Github)** with `cloudflare/skills`.

### Droid

Install using the [Droid plugin manager](https://docs.factory.ai/cli/configuration/plugins):

```
droid plugin marketplace add https://github.com/cloudflare/skills
droid plugin install cloudflare@skills
```

### npx skills

Install using the [`npx skills`](https://skills.sh) CLI:

```
npx skills add https://github.com/cloudflare/skills
```

### Clone / Copy

Clone this repo and copy the skill folders into the appropriate directory for your agent:

| Agent | Skill Directory | Docs |
|-------|-----------------|------|
| Claude Code | `~/.claude/skills/` | [docs](https://code.claude.com/docs/en/skills) |
| Cursor | `~/.cursor/skills/` | [docs](https://cursor.com/docs/context/skills) |
| Droid | `~/.factory/skills/` | [docs](https://docs.factory.ai/cli/configuration/skills) |
| OpenCode | `~/.config/opencode/skills/` | [docs](https://opencode.ai/docs/skills/) |
| OpenAI Codex | `~/.codex/skills/` | [docs](https://developers.openai.com/codex/skills/) |
| Pi | `~/.pi/agent/skills/` | [docs](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent#skills) |

## Skills

Skills are contextual and auto-loaded based on your conversation. When a request matches a skill's triggers, the agent loads and applies the relevant skill to provide accurate, up-to-date guidance.

| Skill | Useful for |
|-------|------------|
| cloudflare | Helps agents discover which Cloudflare products fit their needs, then find the right skills and docs |
| nextjs-on-cloudflare | Next.js on Workers with vinext; routes to vinext's upstream skills and docs |
| agents-sdk | Building stateful AI agents with state, scheduling, RPC, MCP servers, email, and streaming chat |
| durable-objects | Stateful coordination (chat rooms, games, booking), RPC, SQLite, alarms, WebSockets |
| sandbox-next | Sandbox on `@cloudflare/sandbox@next` (1.0 preview); recommended for new projects |
| sandbox-stable | Sandbox on the current stable `@cloudflare/sandbox` package |
| sandbox-migrate-to-next | Port a stable Sandbox app to `@cloudflare/sandbox@next` |
| wrangler | Deploying and managing Workers, KV, R2, D1, Vectorize, Queues, Workflows |
| workers-best-practices | Writing, reviewing, or configuring production Workers |
| cloudflare-email-service | Implementing or troubleshooting Email Sending, Email Routing, and delivery configuration |
| turnstile-spin | Setting up, repairing, or migrating Turnstile bot verification, including server-side Siteverify |
| web-perf | Auditing Core Web Vitals (FCP, LCP, TBT, CLS), render-blocking resources, network chains |
| cloudflare-one | Designing, configuring, troubleshooting, or reviewing [Cloudflare One](https://developers.cloudflare.com/cloudflare-one/) deployments across Access, Gateway, WARP, Tunnel, Magic WAN, DLP, CASB, posture, and identity |
| cloudflare-one-migrations | Migration assessments, policy mapping, rollout plans, and gap analysis for Zscaler, Palo Alto, legacy VPN/SWG, and SASE migrations to Cloudflare One |

## MCP Servers

This plugin includes Cloudflare's main [remote MCP server](https://developers.cloudflare.com/agents/model-context-protocol/cloudflare/servers-for-cloudflare/) for enhanced functionality:

| Server | Purpose |
|--------|---------|
| cloudflare | Access the Cloudflare API and current developer documentation through the Code Mode MCP server |

Cloudflare also publishes product-specific MCP servers. This plugin intentionally bundles only the main `cloudflare` server.
