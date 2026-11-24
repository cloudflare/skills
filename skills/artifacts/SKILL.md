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
| Use Artifacts from a Worker | [Workers get started](https://developers.cloudflare.com/artifacts/get-started/workers/index.md), [Workers binding](https://developers.cloudflare.com/artifacts/api/workers-binding/index.md) | Binding config, namespace and repository methods, return shapes, minimum Wrangler version |
| Develop and test locally | [Local development](https://developers.cloudflare.com/artifacts/guides/local-development/index.md) | Local simulator default, `remote` setting, Git and tool versions, where local repos persist and how to reset them |
| Write files from a Worker | [isomorphic-git example](https://developers.cloudflare.com/artifacts/examples/isomorphic-git/index.md), [Git protocol](https://developers.cloudflare.com/artifacts/api/git-protocol/index.md) | Commit and push flow, token format, in-memory filesystem |
| Issue and scope tokens | [Authentication](https://developers.cloudflare.com/artifacts/guides/authentication/index.md), [Errors](https://developers.cloudflare.com/artifacts/api/errors/index.md) | Token scopes and how each interface authenticates; the allowed TTL range is under `INVALID_TTL` |
| Handle failures | [Errors](https://developers.cloudflare.com/artifacts/api/errors/index.md) | Error names, numeric codes, and what each means |
| Manage repos over HTTP or the CLI | [REST API](https://developers.cloudflare.com/artifacts/api/rest-api/index.md), [Wrangler commands](https://developers.cloudflare.com/artifacts/api/wrangler/index.md) | Routes, authentication, CLI usage |
| Design for scale and safety | [Best practices](https://developers.cloudflare.com/artifacts/concepts/best-practices/index.md), [Limits](https://developers.cloudflare.com/artifacts/platform/limits/index.md) | Repo naming, forking from a baseline, token lifetimes, rate limits |
| React to pushes or import repos | [Event subscriptions](https://developers.cloudflare.com/artifacts/guides/event-subscriptions/index.md), [Import repositories](https://developers.cloudflare.com/artifacts/guides/import-repositories/index.md) | Event shapes; retry on `409 Conflict` while an import finishes. Repository `status` values are under `list()` in the Workers binding reference |

For the full page list, read [Artifacts llms.txt](https://developers.cloudflare.com/artifacts/llms.txt).

## Find the binding types first

Run `npx wrangler types` after adding the Artifacts binding, then read the `Artifacts`, `ArtifactsRepo`, and `ArtifactsError` declarations in the generated `worker-configuration.d.ts`. They document every method, return shape, and error code for the installed Wrangler version, and work without network access. Do not guess method names or probe the binding at runtime.

## Gotchas

Most of these follow from the [Workers binding](https://developers.cloudflare.com/artifacts/api/workers-binding/index.md) reference; the last two are general Git and application guidance. They are the usual causes of Workers that pass a manual test but fail in a fresh environment.

- **The binding doesn't write files or commits.** It creates, imports, forks, and deletes repositories, manages tokens, and reads metadata, history, and files. To change files, commit with a Git client, such as isomorphic-git in a Worker, and push to the repository's remote with a `write` token.
- **Create the repository in code if the task needs it to exist.** `get()` throws if the repository does not exist or is not ready yet, so check the error code before treating it as missing. Handle a missing repository by calling `create()`, and treat `ALREADY_EXISTS` from `create()` as a concurrent request winning the race. A new repository has no commits, so the first write initializes a working tree and pushes, rather than cloning.
- **Mint a short-lived token when you need to push.** `create()` and `import()` return an initial token, but prefer not to keep it in module scope or rely on it for later pushes. Call `repo.createToken("write", ttl)` when you need to push, use its `plaintext`, keep the TTL short, and revoke it when done if appropriate. [Best practices](https://developers.cloudflare.com/artifacts/concepts/best-practices/index.md) recommends short lifetimes and a fresh token for each agent session. Tokens end in an `?expires=<unix_seconds>` suffix; do not assume a fixed prefix. Send the full string as a Bearer token, or only the part before `?expires=` as the Basic auth password, as in the [Git protocol](https://developers.cloudflare.com/artifacts/api/git-protocol/index.md) reference.
- **Read metadata with `repo.info()`.** `get()` returns a disposable capability, not metadata. `info()` performs a fresh lookup and returns `ArtifactsRepoInfo`; read its field names, such as the remote URL and default branch, from the generated types. Declare handles with `using` so they are released before the request ends.
- **Match errors on their code, not message text.** The codes, such as `NOT_FOUND` and `ALREADY_EXISTS`, are listed on [Errors](https://developers.cloudflare.com/artifacts/api/errors/index.md); check how the binding exposes them in the `ArtifactsError` declaration in `worker-configuration.d.ts`. Retry `IMPORT_IN_PROGRESS` and `FORK_IN_PROGRESS` briefly. Return a clear error for the rest.
- **Handle concurrent pushes (general Git guidance).** Two writers can race on the same branch. Push without force, and on a rejected push fetch again, reapply the change, and retry.
- **Read current state from Artifacts (general application guidance).** Read files and metadata through the binding or Git when a request needs them, instead of caching repository contents, tokens, or remote URLs in module scope or another store, unless the task asks for that. Cached copies go stale and are lost on restart.

## Verify

Test the way a new deployment runs: start from a namespace without the repository, exercise every route, restart the Worker, and exercise them again. If you created repositories or tokens by hand while exploring, delete them first, or the code that creates them is never tested. With the local simulator and persistence on, repositories persist across dev-server restarts and are separate from deployed ones. [Local development](https://developers.cloudflare.com/artifacts/guides/local-development/index.md) covers which dev tools use the simulator by default and how to reset it to start empty.

## Skill feedback

If the user reports that this skill gave incorrect or outdated guidance, or is missing information, read [references/skill-feedback.md](references/skill-feedback.md).
