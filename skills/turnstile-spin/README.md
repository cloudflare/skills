# turnstile-spin (skill)

End-to-end setup skill for Cloudflare Turnstile. Loads when an agent is asked to add Turnstile, set up CAPTCHA, or protect a form from bots.

This is a mirror of the canonical docs page at [`developers.cloudflare.com/turnstile/spin`](https://developers.cloudflare.com/turnstile/spin/). If the two disagree, the docs page wins.

## Layout

| File                              | Purpose                                                                |
| --------------------------------- | ---------------------------------------------------------------------- |
| `SKILL.md`                        | Main wizard instructions for the agent                                 |
| `references/vanilla-html.md`      | Code snippet for static / vanilla HTML projects                        |
| `references/nextjs-app.md`        | Code snippet for Next.js App Router projects                           |
| `references/nextjs-pages.md`      | Code snippet for Next.js Pages Router projects                         |
| `references/astro.md`             | Code snippet for Astro projects                                        |
| `references/sveltekit.md`         | Code snippet for SvelteKit projects                                    |
| `references/hugo.md`              | Code snippet for Hugo projects                                         |
| `tests/validation.md`             | Validation cases matching the MVP rows in the PRD                      |

## How agents load it

Agents that load skill bundles from `github.com/cloudflare/skills` will pick this up automatically. For agents that load skills out of a local directory:

```sh
# Claude Code
mkdir -p .claude/skills/turnstile-spin && \
  curl -sSL https://developers.cloudflare.com/turnstile/spin.md \
  -o .claude/skills/turnstile-spin/SKILL.md

# Or, install the whole skills bundle into a global location
git clone https://github.com/cloudflare/skills ~/.config/cloudflare-skills
ln -s ~/.config/cloudflare-skills/turnstile-spin ~/.claude/skills/turnstile-spin
```

For other agents, see the table in [`SKILL.md`](./SKILL.md#step-8--persist-the-skill).

## Sync with the docs page

The canonical source of truth is `src/content/docs/turnstile/spin/index.mdx` in the `cloudflare-docs` repo. This skill mirrors that content with the JSX stripped out. CI keeps them in sync on each docs release; if you are hand-editing, mirror your change to both places.

## Related

- [Canonical docs page](https://developers.cloudflare.com/turnstile/spin/)
- [`cloudflare/turnstile-siteverify`](https://github.com/cloudflare/turnstile-siteverify) — the managed Worker that this skill deploys
- [`cloudflare/skills`](https://github.com/cloudflare/skills) — root index for all Cloudflare agent skills
