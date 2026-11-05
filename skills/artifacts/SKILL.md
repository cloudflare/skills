---
name: artifacts
description: Build, debug, or review code that uses Cloudflare Artifacts, Git-compatible versioned storage, from Workers, the REST API, or Git clients. Use for the env.ARTIFACTS binding, creating, forking, or importing repositories, repo-scoped tokens, and pushing commits from a Worker.
---

# Cloudflare Artifacts

Artifacts is Git-compatible versioned storage: namespaces hold repositories, and each repository has a Git remote. Your knowledge of the Artifacts API may be outdated or missing. **Prefer retrieval over pre-training**: read the matching page below before writing code, and treat the docs and generated types as the source of truth over this skill.

## Documentation

| Task | Docs | Check for |
|------|------|-----------|
| Understand the model | [How Artifacts works](https://developers.cloudflare.com/artifacts/concepts/how-artifacts-works/index.md), [Repositories](https://developers.cloudflare.com/artifacts/concepts/repositories/index.md), [Namespaces](https://developers.cloudflare.com/artifacts/concepts/namespaces/index.md) | What the binding, REST API, and Git protocol each do |
| Use Artifacts from a Worker | [Workers get started](https://developers.cloudflare.com/artifacts/get-started/workers/index.md), [Workers binding](https://developers.cloudflare.com/artifacts/api/workers-binding/index.md) | Binding config, namespace and repository methods, return shapes |
| Write files from a Worker | [isomorphic-git example](https://developers.cloudflare.com/artifacts/examples/isomorphic-git/index.md), [Git protocol](https://developers.cloudflare.com/artifacts/api/git-protocol/index.md) | Commit and push flow, token format, in-memory filesystem |
| Issue and scope tokens | [Authentication](https://developers.cloudflare.com/artifacts/guides/authentication/index.md) | Token scopes, TTLs, how Git clients authenticate |
| Handle failures | [Errors](https://developers.cloudflare.com/artifacts/api/errors/index.md) | Error codes and when each is thrown |
| Manage repos over HTTP or the CLI | [REST API](https://developers.cloudflare.com/artifacts/api/rest-api/index.md), [Wrangler commands](https://developers.cloudflare.com/artifacts/api/wrangler/index.md) | Routes, authentication, CLI usage |
| Design for scale and safety | [Best practices](https://developers.cloudflare.com/artifacts/concepts/best-practices/index.md), [Limits](https://developers.cloudflare.com/artifacts/platform/limits/index.md) | Repo naming, forking from a baseline, token lifetimes, rate limits |
| React to pushes or import repos | [Event subscriptions](https://developers.cloudflare.com/artifacts/guides/event-subscriptions/index.md), [Import repositories](https://developers.cloudflare.com/artifacts/guides/import-repositories/index.md) | Event shapes, import status |

For the full page list, read [Artifacts llms.txt](https://developers.cloudflare.com/artifacts/llms.txt).

## Find the binding types first

Run `npx wrangler types` after adding the Artifacts binding, then read the `Artifacts`, `ArtifactsRepo`, and `ArtifactsError` declarations in the generated `worker-configuration.d.ts`. They document every method, return shape, and error code for the installed Wrangler version, and work without network access. Do not guess method names or probe the binding at runtime.

## Gotchas

These follow from the [Workers binding](https://developers.cloudflare.com/artifacts/api/workers-binding/index.md) reference and are the usual causes of Workers that pass a manual test but fail in a fresh environment.

- **The binding has no write call.** It creates, reads, forks, and issues tokens. To change files, commit with a Git client, such as isomorphic-git in a Worker, and push to the repository's remote with a `write` token.
- **Create the repository in code if the task needs it to exist.** `get()` throws `NOT_FOUND` for a missing repository. Handle that by calling `create()`, and treat `ALREADY_EXISTS` from `create()` as a concurrent request winning the race. A new repository has no commits, so the first write initializes a working tree and pushes, rather than cloning.
- **Mint a fresh token for each Git operation.** The `token` returned by `create()`, `import()`, and `fork()` is shown only once. Do not keep it in module scope or rely on it later. Call `repo.createToken("write", ttl)` when you need to push, use its `plaintext`, keep the TTL short, and revoke it when done if appropriate. Tokens look like `art_v1_<secret>?expires=<unix_seconds>`: send the full string as a Bearer token, or only the part before `?expires=` as the Basic auth password, as in the [Git protocol](https://developers.cloudflare.com/artifacts/api/git-protocol/index.md) reference.
- **Read metadata with `repo.info()`.** `get()` returns a disposable capability, not metadata. Use `(await repo.info()).remote` for the remote URL and `defaultBranch` for the branch. Declare handles with `using` so they are released before the request ends.
- **Match errors on `error.code`, not message text.** Binding errors are `ArtifactsError` with a string `code` such as `NOT_FOUND`, `ALREADY_EXISTS`, or `FORK_IN_PROGRESS`. Retry `*_IN_PROGRESS` codes briefly. Return a clear error for the rest.
- **Handle concurrent pushes.** Two writers can race on the same branch. Push without force, and on a rejected push fetch again, reapply the change, and retry.
- **Keep state in Artifacts.** Read through the binding or Git on every request instead of caching repository contents, tokens, or remote URLs in module scope or another store, unless the task asks for that.

## Verify

Test the way a new deployment runs: start from a namespace without the repository, exercise every route, restart the Worker, and exercise them again. If you created repositories or tokens by hand while exploring, delete them first, or the code that creates them is never tested.

## Skill feedback

If the user reports that this skill gave incorrect or outdated guidance, or is missing information, read [references/skill-feedback.md](references/skill-feedback.md).
