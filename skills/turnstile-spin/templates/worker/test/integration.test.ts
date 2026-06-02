/**
 * Integration tests that hit Cloudflare's real siteverify endpoint using the
 * documented test sitekeys + test secrets.
 *
 * Test keys reference:
 *   https://developers.cloudflare.com/turnstile/troubleshooting/testing/
 *
 * Test secrets:
 *   1x0000000000000000000000000000000AA  — always passes
 *   2x0000000000000000000000000000000AA  — always fails
 *   3x0000000000000000000000000000000AA  — already-spent token (timeout-or-duplicate)
 *
 * Test sitekeys:
 *   1x00000000000000000000AA  — visible, always passes
 *   2x00000000000000000000AB  — visible, always blocks
 *   1x00000000000000000000BB  — invisible, always passes
 *   2x00000000000000000000BB  — invisible, always blocks
 *   3x00000000000000000000FF  — forces an interactive challenge
 *
 * These tests make real network calls. Run with `npm run test:integration`.
 */

import { describe, expect, it } from 'vitest';
import worker from '../src/index.js';
import type { Env } from '../src/types.js';

const PASSING_SECRET = '1x0000000000000000000000000000000AA';
const FAILING_SECRET = '2x0000000000000000000000000000000AA';
const SPENT_TOKEN_SECRET = '3x0000000000000000000000000000000AA';

// The widget produces some opaque token string. For test secrets the actual
// content doesn't matter; siteverify decides based on the secret.
const FAKE_TOKEN = 'XXXX.DUMMY.TOKEN.XXXX';

function envWith(secret: string): Env {
	return {
		TURNSTILE_SECRET_KEY: secret,
		ALLOWED_ORIGIN: '*',
	};
}

describe('integration: real siteverify with test secrets', () => {
	it('passing-secret returns success=true', async () => {
		const res = await worker.fetch(
			new Request('https://w/', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ token: FAKE_TOKEN }),
			}),
			envWith(PASSING_SECRET),
		);
		expect(res.status).toBe(200);
		const body = (await res.json()) as { success: boolean; _worker?: { duration_ms: number } };
		expect(body.success).toBe(true);
		expect(body._worker?.duration_ms).toBeGreaterThan(0);
	}, 15_000);

	it('failing-secret returns success=false', async () => {
		const res = await worker.fetch(
			new Request('https://w/', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ token: FAKE_TOKEN }),
			}),
			envWith(FAILING_SECRET),
		);
		expect(res.status).toBe(200);
		const body = (await res.json()) as { success: boolean; 'error-codes': string[] };
		expect(body.success).toBe(false);
		expect(body['error-codes'].length).toBeGreaterThan(0);
	}, 15_000);

	it('spent-token secret returns timeout-or-duplicate', async () => {
		const res = await worker.fetch(
			new Request('https://w/', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ token: FAKE_TOKEN }),
			}),
			envWith(SPENT_TOKEN_SECRET),
		);
		expect(res.status).toBe(200);
		const body = (await res.json()) as { success: boolean; 'error-codes': string[] };
		expect(body.success).toBe(false);
		expect(body['error-codes']).toContain('timeout-or-duplicate');
	}, 15_000);
});
