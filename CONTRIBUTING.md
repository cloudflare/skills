# Contributing

Keep skills small: help agents find the right documentation instead of maintaining another copy of it.

For changes to skills, commands, or bundled references:

- Read the relevant page on [Cloudflare's developer documentation](https://developers.cloudflare.com/) and verify that it supports the proposed guidance; a working URL alone is not enough.
- Link directly to the relevant product or workflow page. Prefer links over duplicated API signatures, limits, pricing, configuration, or examples that can become stale.
- When correcting outdated reference content, replace it with a short pointer to the current documentation where possible.
- If the required guidance is missing from `developers.cloudflare.com`, describe the documentation gap in the pull request rather than adding unsupported guidance to a skill.

## Test the edited checkout locally

The repository's normal Codex catalog intentionally tracks GitHub. Adding that catalog from a checkout does not make its remote plugin entry load your local edits. Stage a separate local marketplace instead:

```sh
python3 scripts/stage-local-plugin.py /tmp/cloudflare-plugin-dev-1
codex plugin marketplace add /tmp/cloudflare-plugin-dev-1
codex plugin add cloudflare@cloudflare-dev
```

The helper copies the working tree's nonignored files into a new directory and creates a local source entry. It never installs a plugin, changes user settings, fetches a remote revision, or overwrites an existing destination. Review new/untracked files before staging. Use a Python 3.12 environment and Git. Existing ignored secrets are excluded; do not put credentials in tracked or unignored files.

Disable another Cloudflare plugin/skill installation for the test session to avoid duplicate discovery. Start a new session, invoke a changed skill, and verify the loaded location and content refer to the staged copy. Test from a separate disposable project, not the plugin directory. Account authentication is deferred until needed; a discovery check does not require cloud access.

Codex loads an installed cache copy. After edits, stage a new directory, remove the development plugin and marketplace with `codex plugin remove cloudflare@cloudflare-dev` and `codex plugin marketplace remove cloudflare-dev`, then repeat the commands using the new directory. Restart the session and verify the changed content again. Remove the development installation when finished and restore any installation disabled for testing. See the [OpenAI packaging guide](https://developers.openai.com/plugins/build/plugins) for cache and marketplace behavior.

Also test the claimed native clients and a skills-only installation. Record the client/version and component discovery results in the PR; do not claim an authenticated MCP or live deployment test unless it actually ran.

## Prepare a release

Use one version across all four plugin manifests. Choose a stable semantic version according to compatibility and scope, write concise release notes to a file, then run:

```sh
python3 scripts/prepare-release.py 1.0.1 --notes-file /tmp/cloudflare-release-notes.md
python3 scripts/prepare-release.py 1.0.1
```

The first command updates the manifests and inserts the notes in `CHANGELOG.md`; the second checks them without writing. Review and submit those changes in a release PR. Run the available package validation and offline tests, plus client installation smoke checks. Resolve any Unreleased notes into the versioned entry before publication.

After the release PR is merged and checks pass, a maintainer can tag that exact commit `v1.0.1` and push the tag. The tag workflow verifies that all manifest versions and release notes match. It does not create a release, publish to a marketplace, or deploy resources automatically. Publish release notes and directory updates through the normal maintainer process.

For reproducible Codex distribution, pin the plugin entry's Git source to a released `ref` or exact `sha`, not just the marketplace source. For example:

```json
{
  "name": "cloudflare",
  "source": {
    "source": "url",
    "url": "https://github.com/cloudflare/skills.git",
    "ref": "v1.0.1"
  },
  "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
  "category": "Developer Tools"
}
```

This is an example for use after that tag exists. An exact commit SHA is preferable when tags might move. Leave the normal repository catalog tracking development unless deliberately changing its distribution policy. See [Git-backed plugin sources](https://developers.openai.com/plugins/build/plugins).
