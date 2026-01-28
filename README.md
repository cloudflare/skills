# Cloudflare Skills

A collection of [Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) for building on Cloudflare, Workers, the Agents SDK, and the wider Cloudflare Developer Platform.

## Installing

These skills work with any agent that supports the Agent Skills standard, including Claude Code, OpenCode, OpenAI Codex, and Pi.

### Claude Code

Install using the [plugin marketplace](https://code.claude.com/docs/en/discover-plugins#add-from-github):

```
/plugin marketplace add cloudflare/skills
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
| OpenCode | `~/.config/opencode/skill/` | [docs](https://opencode.ai/docs/skills/) |
| OpenAI Codex | `~/.codex/skills/` | [docs](https://developers.openai.com/codex/skills/) |
| Pi | `~/.pi/agent/skills/` | [docs](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent#skills) |

## Skills

| Skill | Useful for | Directory |
|-------|------------|-----------|
| cloudflare | Comprehensive platform skill covering Workers, Pages, storage (KV, D1, R2), AI (Workers AI, Vectorize, Agents SDK), networking (Tunnel, Spectrum), security (WAF, DDoS), and IaC (Terraform, Pulumi) | `cloudflare/` |
| agents-sdk | Building stateful AI agents with state, scheduling, RPC, MCP servers, email, and streaming chat | `agents-sdk/` |
| durable-objects | Stateful coordination (chat rooms, games, booking), RPC, SQLite, alarms, WebSockets | `durable-objects/` |
| wrangler | Deploying and managing Workers, KV, R2, D1, Vectorize, Queues, Workflows | `wrangler/` |
| web-perf | Auditing Core Web Vitals (FCP, LCP, TBT, CLS), render-blocking resources, network chains | `web-perf/` |
| building-mcp-server-on-cloudflare | Building remote MCP servers with tools, OAuth, and deployment | `building-mcp-server-on-cloudflare/` |
| building-ai-agent-on-cloudflare | Building AI agents with state, WebSockets, and tool integration | `building-ai-agent-on-cloudflare/` |

## Usage

When a request matches a skill's triggers, the agent loads and applies the relevant skill to provide accurate, up-to-date guidance.

## Resources

- [Cloudflare Agents Documentation](https://developers.cloudflare.com/agents/)
- [Cloudflare MCP Guide](https://developers.cloudflare.com/agents/model-context-protocol/)
- [Agents SDK Repository](https://github.com/cloudflare/agents)
- [Agents Starter Template](https://github.com/cloudflare/agents-starter)
