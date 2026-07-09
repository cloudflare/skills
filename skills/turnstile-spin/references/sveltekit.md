# SvelteKit

For SvelteKit projects. Widget renders in the page; siteverify can be called from a form action server-side, or directly against the Worker from the client.

```svelte title="src/routes/signup/+page.svelte"
<script lang="ts">
	import { onMount } from "svelte";
	let token = "";

	onMount(() => {
		(window as any).onTurnstileSuccess = (t: string) => (token = t);
	});

	async function handleSubmit(e: Event) {
		e.preventDefault();
		const res = await fetch("https://YOUR_WORKER_URL/", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ token }),
		});
		const data = await res.json();
		if (data.success) {
			// proceed
		}
	}
</script>

<svelte:head>
	<script
		src="https://challenges.cloudflare.com/turnstile/v0/api.js"
		async
		defer
	></script>
</svelte:head>

<form on:submit={handleSubmit}>
	<input name="email" type="email" required />
	<div
		class="cf-turnstile"
		data-sitekey="YOUR_SITEKEY"
		data-action="turnstile-spin-v1"
		data-callback="onTurnstileSuccess"
	></div>
	<button type="submit" disabled={!token}>Sign up</button>
</form>
```

## Variant: Form action server-side

If you use SvelteKit's form actions for the signup logic, do siteverify from the action:

```ts title="src/routes/signup/+page.server.ts"
import type { Actions } from "./$types";
import { fail } from "@sveltejs/kit";

export const actions: Actions = {
	default: async ({ request }) => {
		const data = await request.formData();
		const token = data.get("cf-turnstile-response") as string;

		const verify = await fetch("https://YOUR_WORKER_URL/", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ token }),
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

With this variant the form posts via SvelteKit's progressive enhancement; the page component drops the explicit `fetch` call and just uses a native `<form method="POST">`.

## Substitutions

| Placeholder        | Replace with                                |
| ------------------ | ------------------------------------------- |
| `YOUR_WORKER_URL`  | Deployed Worker URL from Step 5             |
| `YOUR_SITEKEY`     | Widget site key from Step 4                 |
