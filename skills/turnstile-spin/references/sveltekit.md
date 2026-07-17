# SvelteKit

For SvelteKit projects. The widget renders in the page; siteverify is called from a SvelteKit form action (or a `+server.ts` endpoint) server-side.

```svelte title="src/routes/signup/+page.svelte"
<script>
	import { enhance } from "$app/forms";
</script>

<svelte:head>
	<script
		src="https://challenges.cloudflare.com/turnstile/v0/api.js"
		async
		defer
	></script>
</svelte:head>

<form
	method="POST"
	use:enhance={() => {
		return async ({ result, update }) => {
			await update();
			// Tokens are single-use. Reset after each submit so a retry
			// on failure gets a fresh token.
			if (result.type !== "redirect") {
				window.turnstile?.reset();
			}
		};
	}}
>
	<input name="email" type="email" required />
	<div
		class="cf-turnstile"
		data-sitekey="YOUR_SITEKEY"
		data-action="turnstile-spin-v2"
	></div>
	<button type="submit">Sign up</button>
</form>
```

Form action (canonical siteverify):

```ts title="src/routes/signup/+page.server.ts"
import type { Actions } from "./$types";
import { fail } from "@sveltejs/kit";
import { TURNSTILE_SECRET } from "$env/static/private";

export const actions: Actions = {
	default: async ({ request, getClientAddress }) => {
		const data = await request.formData();
		const token = data.get("cf-turnstile-response") as string;

		const verify = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
			method: "POST",
			headers: { "Content-Type": "application/x-www-form-urlencoded" },
			body: new URLSearchParams({
				secret: TURNSTILE_SECRET,
				response: token,
				remoteip: getClientAddress(),
			}),
		});
		const result = await verify.json();
		if (!result.success) {
			return fail(403, { error: "Verification failed" });
		}

		// process signup
		return { ok: true };
	},
};
```

In `.env`:

```text
TURNSTILE_SECRET=YOUR_SECRET
```

The `$env/static/private` import enforces that the secret never reaches the client bundle.

## Variant: client-side fetch to an endpoint

If you need a JSON API rather than progressive-enhancement form post, use `+server.ts`:

```ts title="src/routes/api/signup/+server.ts"
import type { RequestHandler } from "./$types";
import { TURNSTILE_SECRET } from "$env/static/private";

export const POST: RequestHandler = async ({ request, getClientAddress }) => {
	const { token } = await request.json();
	const verify = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
		method: "POST",
		headers: { "Content-Type": "application/x-www-form-urlencoded" },
		body: new URLSearchParams({
			secret: TURNSTILE_SECRET,
			response: token,
			remoteip: getClientAddress(),
		}),
	});
	const { success } = await verify.json();
	if (!success) return new Response("forbidden", { status: 403 });
	// process signup
	return new Response(JSON.stringify({ ok: true }), { status: 200 });
};
```

When calling this endpoint from client-side fetch, reset the widget in the error branch:

```svelte
<script>
	async function submit(e) {
		e.preventDefault();
		const token = new FormData(e.target).get("cf-turnstile-response");
		const res = await fetch("/api/signup", {
			method: "POST",
			body: JSON.stringify({ token }),
		});
		if (!res.ok) {
			window.turnstile?.reset();
			// surface error
		}
	}
</script>
```

## Substitutions

| Placeholder         | Replace with                                                         |
| ------------------- | -------------------------------------------------------------------- |
| `YOUR_SITEKEY`      | The widget site key from Step 8                                      |
| `YOUR_SECRET`       | The secret captured in Step 8. Stays in env, never inlined.          |
