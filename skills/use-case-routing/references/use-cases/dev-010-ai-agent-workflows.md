---
id: dev-010
name: Build and manage AI agent workflows
category: developer-platform-build
description: Framework and orchestration tools for deploying agents, including remote MCP servers.
products: [Agents, Workflows, Workers AI, Durable Objects, Access]
default_path: conversational-agent
aliases:
  - Build a ChatGPT app
  - Build an AI code executor
  - Build a code review bot
  - Build a remote MCP server
keywords:
  - "AI agent framework"
  - "agent orchestration"
  - "stateful AI agents"
  - "MCP server"
  - "remote MCP"
  - "tool-using chatbot"
  - "multi-step LLM workflow"
related:
  - aisec-003
  - dev-009
  - ops-002
---

# Build and manage AI agent workflows

## Ask first

**What kind of AI agent are you building?**
- Conversational agent (chatbot with tool use) → conversational-agent
- Task automation agent → task-automation
- MCP server for AI tool access → mcp-server

## Paths

### conversational-agent (default)

For a conversational agent with tool use:

1. Create a new Agents project using the Agents SDK
2. Define the tools the agent can call
3. Configure the LLM backend (Workers AI or an external provider)
4. Use Durable Objects for conversation state
5. Deploy to Cloudflare's network

### mcp-server

For a remote MCP server that exposes tools to AI clients:

1. Create an MCP server using the Agents SDK
2. Define MCP tools and resources
3. Configure OAuth or other authentication via Access
4. Deploy the MCP server

### task-automation

For a multi-step task automation agent:

1. Create a Workflow for multi-step task execution
2. Define workflow steps with retry logic
3. Integrate an LLM for decision-making within steps
4. Deploy the automation agent

## Hand off

For implementation, retrieve from Cloudflare docs:
https://developers.cloudflare.com/agents/, /workflows/, /workers-ai/, /durable-objects/, /cloudflare-one/.
Browse https://github.com/cloudflare/skills/tree/main/skills for any
matching builder skills.
