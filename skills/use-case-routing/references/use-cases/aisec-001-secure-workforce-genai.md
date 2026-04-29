---
id: aisec-001
name: Govern workforce AI use with granular access, prompt redaction, and read-only policies
category: ai-security
description: Discover shadow AI tools, enforce usage controls, analyze prompt content and intent, and block data leaks to AI services.
products: [Gateway, DLP, CASB, AI Security for Apps]
default_path: shadow-ai-discovery
aliases:
  - Enforce AI prompt protection and guardrails
  - AI prompt security
  - Workforce AI governance
keywords:
  - "shadow AI"
  - "ChatGPT data leak"
  - "block ChatGPT"
  - "employees using AI"
  - "prompt injection"
  - "jailbreak detection"
  - "AI acceptable use policy"
  - "Copilot governance"
  - "redact prompts"
related:
  - aisec-004
  - aisec-002
  - zt-008
  - zt-009
---

# Govern workforce AI use with granular access, prompt redaction, and read-only policies

## Ask first

**What is your primary concern with workforce AI usage?**
- Employees leaking sensitive data into AI tools → data-leak-prevention
- No visibility into which AI tools are being used → shadow-ai-discovery
- Need to enforce acceptable use policies for AI → workforce-prompt-protection
- All of the above → walk shadow-ai-discovery, then data-leak-prevention, then workforce-prompt-protection

**Have you sanctioned specific AI tools for employee use?**
- Yes (e.g., ChatGPT Enterprise, Copilot) → also walk ai-posture-management
- No, no formal AI policy yet → start with shadow-ai-discovery

If the user is also exposing AI features to customers (not just employees), walk the `customer-facing-guardrails` path regardless of the answers above.

## Paths

### shadow-ai-discovery (default)

Discover and govern shadow AI:

1. Enable Shadow IT Discovery in Gateway to catalog all AI tool usage
2. Review CASB confidence scores for discovered AI applications
3. Mark applications as sanctioned, unsanctioned, or under review in Gateway
4. Create a Gateway block policy for unsanctioned AI tools

### data-leak-prevention

Prevent data leaks to AI tools:

1. Create DLP profiles for PII, source code, and financial data
2. Create a Gateway HTTP policy to inspect traffic to AI tools
3. Enable DLP prompt content and intent analysis for AI tools
4. Use Browser Isolation to control copy/paste, upload, and download in AI tool sessions

### ai-posture-management

For organizations with sanctioned AI tools:

1. Connect sanctioned AI tools (ChatGPT, Claude, Gemini) to CASB via API
2. Scan for misconfigurations and exposed data in those tools
3. Create DLP profiles to detect sensitive data in prompts
4. Use Gateway tenant policy to redirect employees to approved organizational AI tenants

### workforce-prompt-protection

Apply guardrails to prompts in flight:

1. Create DLP profiles targeting PII, source code, and financial data
2. Enable intent detection for jailbreak attempts, code abuse, and PII extraction
3. Create a Gateway HTTP policy to inspect and block risky prompts
4. Enable Gateway logging so blocked prompts are captured for security review

### customer-facing-guardrails

For AI features your application exposes to customers:

1. Enable Firewall for AI on your AI application endpoints
2. Configure prompt injection and jailbreak detection
3. Configure response scanning to catch PII and sensitive data before delivery
4. Add a WAF rate limiting rule to prevent abuse of AI endpoints

## Hand off

For implementation, retrieve from Cloudflare docs:
https://developers.cloudflare.com/cloudflare-one/, /waf/.
Browse https://github.com/cloudflare/skills/tree/main/skills for any
matching builder skills.
