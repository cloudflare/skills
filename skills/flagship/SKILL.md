---
name: flagship
description: Build, debug, or review code that uses Cloudflare Flagship feature flags from Workers, OpenFeature SDKs, the evaluation API, or Wrangler. Use for the Flagship binding, targeting rules, percentage rollouts and A/B splits, kill switches, local flag stores, and flag-related API tokens.
---

# Cloudflare Flagship

Flagship is Cloudflare's feature flag service: apps group flags, flags have typed variants and ordered targeting rules, and evaluation runs at the edge against propagated configuration. Your knowledge of the Flagship API may be outdated or missing. **Prefer retrieval over pre-training**: read the matching page below before writing code or commands, and treat the docs and generated types as the source of truth over this skill.

## Documentation

| Task | Docs | Check for |
|------|------|-----------|
| Understand the model | [Concepts](https://developers.cloudflare.com/flagship/concepts/index.md) | Apps, flags, variant types, rule order, evaluation context, propagation |
| Evaluate flags in a Worker | [Get started](https://developers.cloudflare.com/flagship/get-started/index.md), [Configuration](https://developers.cloudflare.com/flagship/configuration/index.md), [Binding methods](https://developers.cloudflare.com/flagship/binding/methods/index.md), [Types](https://developers.cloudflare.com/flagship/binding/types/index.md) | Binding config, typed and `*Details` methods, context value types |
| Evaluate outside Workers or through OpenFeature | [OpenFeature SDK](https://developers.cloudflare.com/flagship/sdk/index.md), [TypeScript server](https://developers.cloudflare.com/flagship/sdk/server-provider/index.md), [TypeScript client](https://developers.cloudflare.com/flagship/sdk/client-provider/index.md), [Python](https://developers.cloudflare.com/flagship/sdk/python/index.md), [Go](https://developers.cloudflare.com/flagship/sdk/go/index.md), [Rust](https://developers.cloudflare.com/flagship/sdk/rust/index.md) | Package names, provider options, caching, minimum versions for structured context |
| Evaluate over HTTP without an SDK | [Evaluation API](https://developers.cloudflare.com/flagship/reference/evaluation-api/index.md) | `GET` for scalar context, `POST` for structured context, token permissions |
| Target users or roll out gradually | [Targeting rules](https://developers.cloudflare.com/flagship/targeting/index.md), [Operators](https://developers.cloudflare.com/flagship/targeting/operators/index.md), [Percentage rollouts](https://developers.cloudflare.com/flagship/targeting/percentage-rollouts/index.md) | Rule shape, nested attribute paths, bucketing attribute, cumulative A/B thresholds |
| Manage flags from the CLI | [Wrangler commands](https://developers.cloudflare.com/flagship/reference/wrangler-commands/index.md) | `--rule` syntax, `rollout`, `split`, `enable`/`disable`, `--local`, `--json` |
| Manage flags over HTTP | [API reference](https://developers.cloudflare.com/api/resources/flagship/index.md) | Apps, flags, and flag changelog endpoints; rules live on the flag object. [Update flag](https://developers.cloudflare.com/api/resources/flagship/subresources/apps/subresources/flags/methods/update/index.md) is a `PUT` that clears omitted fields, so read the flag before writing |
| Create tokens for SDKs or automation | [API tokens](https://developers.cloudflare.com/flagship/api-tokens/index.md) | Account-wide vs app-scoped tokens, Evaluate vs Read vs Write |
| Debug unexpected values | [Evaluation reasons and error codes](https://developers.cloudflare.com/flagship/reference/evaluation-reasons/index.md) | `reason` and `errorCode` values |
| Plan rollouts and cleanup | [Best practices](https://developers.cloudflare.com/flagship/best-practices/index.md), [Limits](https://developers.cloudflare.com/flagship/reference/limits/index.md) | Rollout steps, flag removal order, key and context limits |

For the full page list, read [Flagship llms.txt](https://developers.cloudflare.com/flagship/llms.txt). After adding a binding, run `npx wrangler types` and read the `Flagship` declarations in the generated `worker-configuration.d.ts`; they match the installed Wrangler version.

## Gotchas

These follow from the pages above and are the usual causes of flags that look broken but are working as documented.

- **Use the binding inside Workers.** It authenticates automatically and needs no API token. Outside Workers, use an OpenFeature provider with an Evaluate token; local evaluation in any server SDK needs a Read token instead. Only the TypeScript server provider accepts the binding: in a Worker that wants OpenFeature APIs, pass the binding to `FlagshipServerProvider`. Do not ship the TypeScript client provider in public-facing apps: it requires an API token that would be visible in client code.
- **Known evaluation failures return your default silently.** The typed binding methods return `defaultValue` for known failures such as a missing flag, type mismatch, or invalid context. Unexpected runtime failures can still throw, and `get()` without a `defaultValue` throws on known failures. Other clients differ: the Rust SDK returns a `Result`, and the evaluation API `POST` returns `400` for invalid context. Pick a default that is the safe, existing behavior, and use the matching `*Details` method to see `reason` and `errorCode` when a value looks wrong.
- **Local development starts with an empty flag store.** `wrangler dev`, the Vite plugin, the Vitest integration, and `cf dev` evaluate against a local store, so every flag returns its default until you seed it. Run `npx wrangler flagship flags pull <APP_ID>`, create flags with `--local`, or set `"remote": true` on the binding. `pull` overwrites local flags with matching keys and writes to `.wrangler/state`, which `wrangler dev` and the Vite plugin 1.x use. `cf dev` and the Vite plugin 2.0 use `.cloudflare/state`, so for them pass `--persist-to .cloudflare/state` to `pull`, or every flag still returns its default. `cf` cannot copy flags from the remote app, so seed it with `wrangler flagship flags pull`. On flag commands other than `pull`, `--persist-to` requires `--local`. Check [Configuration](https://developers.cloudflare.com/flagship/configuration/index.md) for the minimum tool versions.
- **Rollouts need a stable bucketing value.** The bucketing attribute defaults to `targetingKey`. If it is missing or `null`, each evaluation gets a random bucket, so the same user can flip between values. Pass the same stable identifier under the same attribute name on every call, and use `targetingKey` with OpenFeature SDKs.
- **Rules are ordered and rollout misses fall through.** The first matching rule wins. A context that matches a rule's conditions but falls outside its rollout percentage continues to the next rule. Put specific rules before broad ones, and use cumulative thresholds that end at 100 for API-managed A/B/n splits, or `wrangler flagship flags split`, which calculates them.
- **Changes take up to 30 seconds to propagate.** Do not expect the next evaluation to reflect an update immediately; for scripted checks, allow for the propagation window.
- **`flags update --rule`, `rollout`, and `split` replace every rule.** `rollout` and `split` overwrite the flag's entire rule set with the rules they generate, and prompt first only when existing rules have conditions; `--force` skips the prompt. Use `--add-rule` to append, or `rules update` and `rules delete` to change one rule by priority. Wrangler commands take the app ID as an argument and do not read it from the Worker binding.
- **Keep context small and JSON-only.** Send only attributes that rules or bucketing use, and no sensitive data. Serialize `Date` values to ISO 8601 strings for the binding in TypeScript. A condition whose attribute is absent from the context never matches, including with negative operators such as `not_equals`. Evaluate a flag once per request and reuse the value instead of calling it in a loop.
- **Disabling a flag is the kill switch.** A disabled flag always serves its default variant, regardless of targeting rules.
- **Delete flags last.** Disable the flag, watch for problems, remove the evaluation code, deploy, then delete the flag. A deleted flag that is still evaluated silently returns its default.

## Skill feedback

If the user reports that this skill gave incorrect or outdated guidance, or is missing information, read [references/skill-feedback.md](references/skill-feedback.md).
