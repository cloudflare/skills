# Next.js (App Router)

For `app/`-directory Next.js projects. The widget needs to run on the client, so the page or component must be `"use client"`. The siteverify call lives server-side, either in a Server Action or an API route.

```tsx title="app/signup/page.tsx"
"use client";
import Script from "next/script";
import { useEffect, useState } from "react";

declare global {
	interface Window {
		onTurnstileSuccess?: (token: string) => void;
	}
}

export default function SignupPage() {
	const [token, setToken] = useState("");

	useEffect(() => {
		window.onTurnstileSuccess = (t: string) => setToken(t);
	}, []);

	async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
		e.preventDefault();
		const res = await fetch("/api/signup", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ token }),
		});
		const data = await res.json();
		if (data.ok) {
			// proceed
		}
	}

	return (
		<>
			<Script
				src="https://challenges.cloudflare.com/turnstile/v0/api.js"
				strategy="afterInteractive"
			/>
			<form onSubmit={handleSubmit}>
				<input name="email" type="email" required />
				<div
					className="cf-turnstile"
					data-sitekey="YOUR_SITEKEY"
					data-action="turnstile-spin-v2"
					data-callback="onTurnstileSuccess"
				/>
				<button type="submit" disabled={!token}>
					Sign up
				</button>
			</form>
		</>
	);
}
```

`data-callback` expects a string referencing a global function. The `useEffect` wires `window.onTurnstileSuccess` so the widget can call back into React state.

API route (canonical siteverify):

```ts title="app/api/signup/route.ts"
export async function POST(req: Request) {
	const { token } = await req.json();
	const remoteip = req.headers.get("x-forwarded-for") ?? undefined;

	const r = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
		method: "POST",
		headers: { "Content-Type": "application/x-www-form-urlencoded" },
		body: new URLSearchParams({
			secret: process.env.TURNSTILE_SECRET!,
			response: token,
			...(remoteip ? { remoteip } : {}),
		}),
	});
	const { success } = await r.json();
	if (!success) return new Response("forbidden", { status: 403 });

	// existing signup logic runs here
	return Response.json({ ok: true });
}
```

## Variant: Server Action

If you are using Server Actions, do the siteverify call from the action itself. The widget still goes in a client component, but the verify call moves server-side:

```tsx title="app/signup/actions.ts"
"use server";
import { headers } from "next/headers";

export async function submitSignup(formData: FormData) {
	const token = formData.get("cf-turnstile-response") as string;
	const remoteip = (await headers()).get("x-forwarded-for") ?? undefined;

	const r = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
		method: "POST",
		headers: { "Content-Type": "application/x-www-form-urlencoded" },
		body: new URLSearchParams({
			secret: process.env.TURNSTILE_SECRET!,
			response: token,
			...(remoteip ? { remoteip } : {}),
		}),
	});
	const { success } = await r.json();
	if (!success) return { error: "Verification failed" };

	// process signup
	return { ok: true };
}
```

```tsx title="app/signup/page.tsx (server-action variant)"
"use client";
import { submitSignup } from "./actions";

export default function SignupPage() {
	return (
		<form action={submitSignup}>
			<input name="email" type="email" required />
			<div
				className="cf-turnstile"
				data-sitekey="YOUR_SITEKEY"
				data-action="turnstile-spin-v2"
			/>
			<button type="submit">Sign up</button>
		</form>
	);
}
```

## Substitutions

| Placeholder         | Replace with                                                         |
| ------------------- | -------------------------------------------------------------------- |
| `YOUR_SITEKEY`      | The widget site key from Step 8                                      |
| `TURNSTILE_SECRET`  | Env-var name. Value is the secret captured in Step 8, kept off disk. |
