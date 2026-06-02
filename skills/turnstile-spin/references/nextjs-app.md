# Next.js (App Router)

For `app/`-directory Next.js projects. The widget needs to run on the client, so the page or component must be `"use client"`.

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
					data-action="turnstile-spin-v1"
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

## Variant: Server Action

If you are using Server Actions, do the siteverify call from the action itself. The widget still goes in a client component, but the verify call moves server-side:

```tsx title="app/signup/actions.ts"
"use server";

export async function submitSignup(formData: FormData) {
	const token = formData.get("cf-turnstile-response") as string;

	const res = await fetch("https://YOUR_WORKER_URL/", {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ token }),
	});
	const data = await res.json();
	if (!data.success) {
		return { error: "Verification failed" };
	}

	// process signup
	return { ok: true };
}
```

```tsx title="app/signup/page.tsx"
"use client";
import { submitSignup } from "./actions";

export default function SignupPage() {
	return (
		<form action={submitSignup}>
			<input name="email" type="email" required />
			<div
				className="cf-turnstile"
				data-sitekey="YOUR_SITEKEY"
				data-action="turnstile-spin-v1"
			/>
			<button type="submit">Sign up</button>
		</form>
	);
}
```

## Substitutions

| Placeholder        | Replace with                                |
| ------------------ | ------------------------------------------- |
| `YOUR_WORKER_URL`  | Deployed Worker URL from Step 5             |
| `YOUR_SITEKEY`     | Widget site key from Step 4                 |
