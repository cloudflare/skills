# Contributing

Keep skills small: help agents find the right documentation instead of maintaining another copy of it.

For changes to skills, commands, or bundled references:

- Read the relevant page on [Cloudflare's developer documentation](https://developers.cloudflare.com/) and verify that it supports the proposed guidance; a working URL alone is not enough.
- Link directly to the relevant product or workflow page. Prefer links over duplicated API signatures, limits, pricing, configuration, or examples that can become stale.
- Link `developers.cloudflare.com` pages by their markdown route (`<route>/index.md`, e.g. `https://developers.cloudflare.com/workers/index.md`), not the HTML route. Not every agent does content negotiation, so the explicit route guarantees markdown. Use `https://developers.cloudflare.com/llms.txt` for the docs root. Keep human-facing files (README, plugin manifests) on HTML routes.
- When correcting outdated reference content, replace it with a short pointer to the current documentation where possible.
- If the required guidance is missing from `developers.cloudflare.com`, describe the documentation gap in the pull request rather than adding unsupported guidance to a skill.

