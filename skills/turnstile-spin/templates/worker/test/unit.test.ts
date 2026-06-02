/**
 * Unit tests for the Worker. These don't hit Cloudflare's real siteverify —
 * see integration.test.ts for that.
 */

import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import worker from '../src/index.js';
import type { Env } from '../src/types.js';

const TEST_ENV: Env = {
	TURNSTILE_SECRET_KEY: 'test-secret-key',
	ALLOWED_ORIGIN: '*',
};

const SITEVERIFY_URL = 'https://challenges.cloudflare.com/turnstile/v0/siteverify';

function mockFetchOnce(response: { status?: number; body: unknown }): void {
	vi.spyOn(globalThis, 'fetch').mockImplementationOnce(async () => {
		return new Response(JSON.stringify(response.body), {
			status: response.status ?? 200,
			headers: { 'Content-Type': 'application/json' },
		});
	});
}

describe('CORS', () => {
	beforeEach(() => vi.restoreAllMocks());
	afterEach(() => vi.restoreAllMocks());

	it('responds to OPTIONS preflight with CORS headers', async () => {
		const res = await worker.fetch(new Request('https://w/', { method: 'OPTIONS' }), TEST_ENV);
		expect(res.status).toBe(204);
		expect(res.headers.get('Access-Control-Allow-Origin')).toBe('*');
		expect(res.headers.get('Access-Control-Allow-Methods')).toContain('POST');
	});

	it('echoes ALLOWED_ORIGIN when set explicitly', async () => {
		const env = { ...TEST_ENV, ALLOWED_ORIGIN: 'https://example.com' };
		const res = await worker.fetch(new Request('https://w/', { method: 'OPTIONS' }), env);
		expect(res.headers.get('Access-Control-Allow-Origin')).toBe('https://example.com');
	});
});

describe('Health endpoints', () => {
	it('GET / returns {ok: true, version}', async () => {
		const res = await worker.fetch(new Request('https://w/'), TEST_ENV);
		expect(res.status).toBe(200);
		const body = (await res.json()) as { ok: boolean; version: string; service: string };
		expect(body.ok).toBe(true);
		expect(body.version).toMatch(/^\d+\.\d+\.\d+$/);
		expect(body.service).toBe('turnstile-siteverify');
	});

	it('GET /health returns the same shape', async () => {
		const res = await worker.fetch(new Request('https://w/health'), TEST_ENV);
		expect(res.status).toBe(200);
		const body = (await res.json()) as { ok: boolean; version: string };
		expect(body.ok).toBe(true);
		expect(typeof body.version).toBe('string');
	});

	it('GET /healthz still returns health (legacy alias)', async () => {
		const res = await worker.fetch(new Request('https://w/healthz'), TEST_ENV);
		expect(res.status).toBe(200);
		const body = (await res.json()) as { ok: boolean };
		expect(body.ok).toBe(true);
	});
});

describe('POST / (siteverify proxy) — JSON body', () => {
	beforeEach(() => vi.restoreAllMocks());
	afterEach(() => vi.restoreAllMocks());

	it('forwards a JSON token to siteverify and returns success', async () => {
		mockFetchOnce({
			body: {
				success: true,
				hostname: 'example.com',
				challenge_ts: '2026-05-22T12:00:00Z',
				'error-codes': [],
			},
		});

		const res = await worker.fetch(
			new Request('https://w/', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ token: 'abc' }),
			}),
			TEST_ENV,
		);

		expect(res.status).toBe(200);
		const body = (await res.json()) as { success: boolean; _worker?: { worker_version: string } };
		expect(body.success).toBe(true);
		expect(body._worker?.worker_version).toMatch(/^\d+\.\d+\.\d+$/);

		// Verify it called the right upstream
		expect(globalThis.fetch).toHaveBeenCalledOnce();
		expect((globalThis.fetch as ReturnType<typeof vi.fn>).mock.calls[0]?.[0]).toBe(SITEVERIFY_URL);
	});

	it('passes through siteverify failure with success=false', async () => {
		mockFetchOnce({
			body: { success: false, 'error-codes': ['invalid-input-response'] },
		});

		const res = await worker.fetch(
			new Request('https://w/', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ token: 'bad' }),
			}),
			TEST_ENV,
		);

		expect(res.status).toBe(200);
		const body = (await res.json()) as { success: boolean; 'error-codes': string[] };
		expect(body.success).toBe(false);
		expect(body['error-codes']).toContain('invalid-input-response');
	});

	it('returns 400 when token is missing', async () => {
		const res = await worker.fetch(
			new Request('https://w/', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({}),
			}),
			TEST_ENV,
		);
		expect(res.status).toBe(400);
		const body = (await res.json()) as { success: boolean; 'error-codes': string[] };
		expect(body.success).toBe(false);
		expect(body['error-codes']).toContain('missing-token');
	});

	it('returns 400 on malformed JSON', async () => {
		const res = await worker.fetch(
			new Request('https://w/', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: '{not json',
			}),
			TEST_ENV,
		);
		expect(res.status).toBe(400);
	});

	it('accepts cf-turnstile-response as alias for token', async () => {
		mockFetchOnce({
			body: { success: true, 'error-codes': [] },
		});
		const res = await worker.fetch(
			new Request('https://w/', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ 'cf-turnstile-response': 'xyz' }),
			}),
			TEST_ENV,
		);
		expect(res.status).toBe(200);
	});
});

describe('POST / (siteverify proxy) — form body', () => {
	beforeEach(() => vi.restoreAllMocks());
	afterEach(() => vi.restoreAllMocks());

	it('accepts urlencoded body', async () => {
		mockFetchOnce({
			body: { success: true, 'error-codes': [] },
		});

		const res = await worker.fetch(
			new Request('https://w/', {
				method: 'POST',
				headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
				body: 'token=abc',
			}),
			TEST_ENV,
		);

		expect(res.status).toBe(200);
		const body = (await res.json()) as { success: boolean };
		expect(body.success).toBe(true);
	});

	it('accepts cf-turnstile-response from form body', async () => {
		mockFetchOnce({
			body: { success: true, 'error-codes': [] },
		});
		const res = await worker.fetch(
			new Request('https://w/', {
				method: 'POST',
				headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
				body: 'cf-turnstile-response=xyz',
			}),
			TEST_ENV,
		);
		expect(res.status).toBe(200);
	});
});

describe('Content-Type handling', () => {
	beforeEach(() => vi.restoreAllMocks());
	afterEach(() => vi.restoreAllMocks());

	it('returns 415 for unsupported content type', async () => {
		const res = await worker.fetch(
			new Request('https://w/', {
				method: 'POST',
				headers: { 'Content-Type': 'text/plain' },
				body: 'token=abc',
			}),
			TEST_ENV,
		);
		expect(res.status).toBe(415);
		const body = (await res.json()) as { 'error-codes': string[] };
		expect(body['error-codes']).toContain('invalid-content-type');
	});
});

describe('Path routing', () => {
	beforeEach(() => vi.restoreAllMocks());
	afterEach(() => vi.restoreAllMocks());

	it('accepts POST /siteverify as alias of POST /', async () => {
		mockFetchOnce({
			body: { success: true, 'error-codes': [] },
		});
		const res = await worker.fetch(
			new Request('https://w/siteverify', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ token: 'abc' }),
			}),
			TEST_ENV,
		);
		expect(res.status).toBe(200);
	});

	it('returns 404 for unknown paths', async () => {
		const res = await worker.fetch(new Request('https://w/random'), TEST_ENV);
		expect(res.status).toBe(404);
	});
});

describe('CF-Connecting-IP fallback', () => {
	beforeEach(() => vi.restoreAllMocks());
	afterEach(() => vi.restoreAllMocks());

	it('uses CF-Connecting-IP if customer did not pass remoteip', async () => {
		const fetchSpy = vi.spyOn(globalThis, 'fetch').mockImplementationOnce(async (_url, init) => {
			const form = init?.body as FormData;
			expect(form.get('remoteip')).toBe('1.2.3.4');
			return new Response(JSON.stringify({ success: true, 'error-codes': [] }), { status: 200 });
		});

		const res = await worker.fetch(
			new Request('https://w/', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'CF-Connecting-IP': '1.2.3.4',
				},
				body: JSON.stringify({ token: 'abc' }),
			}),
			TEST_ENV,
		);

		expect(res.status).toBe(200);
		expect(fetchSpy).toHaveBeenCalledOnce();
	});

	it('prefers explicit remoteip over CF-Connecting-IP', async () => {
		vi.spyOn(globalThis, 'fetch').mockImplementationOnce(async (_url, init) => {
			const form = init?.body as FormData;
			expect(form.get('remoteip')).toBe('9.9.9.9');
			return new Response(JSON.stringify({ success: true, 'error-codes': [] }), { status: 200 });
		});

		await worker.fetch(
			new Request('https://w/', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'CF-Connecting-IP': '1.2.3.4',
				},
				body: JSON.stringify({ token: 'abc', remoteip: '9.9.9.9' }),
			}),
			TEST_ENV,
		);
	});
});

describe('Hostname-mismatch defense', () => {
	beforeEach(() => vi.restoreAllMocks());
	afterEach(() => vi.restoreAllMocks());

	it('rejects success response when hostname does not match EXPECTED_HOSTNAME', async () => {
		mockFetchOnce({
			body: { success: true, hostname: 'attacker.com', 'error-codes': [] },
		});
		const env: Env = { ...TEST_ENV, EXPECTED_HOSTNAME: 'mysite.com' };
		const res = await worker.fetch(
			new Request('https://w/', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ token: 'abc' }),
			}),
			env,
		);
		expect(res.status).toBe(200);
		const body = (await res.json()) as { success: boolean; 'error-codes': string[] };
		expect(body.success).toBe(false);
		expect(body['error-codes']).toContain('hostname-mismatch');
	});

	it('accepts success response when hostname matches EXPECTED_HOSTNAME', async () => {
		mockFetchOnce({
			body: { success: true, hostname: 'mysite.com', 'error-codes': [] },
		});
		const env: Env = { ...TEST_ENV, EXPECTED_HOSTNAME: 'mysite.com' };
		const res = await worker.fetch(
			new Request('https://w/', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ token: 'abc' }),
			}),
			env,
		);
		const body = (await res.json()) as { success: boolean };
		expect(body.success).toBe(true);
	});

	it('does not apply hostname check when EXPECTED_HOSTNAME is unset', async () => {
		mockFetchOnce({
			body: { success: true, hostname: 'anywhere.com', 'error-codes': [] },
		});
		const res = await worker.fetch(
			new Request('https://w/', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ token: 'abc' }),
			}),
			TEST_ENV,
		);
		const body = (await res.json()) as { success: boolean };
		expect(body.success).toBe(true);
	});
});

describe('Missing secret', () => {
	beforeEach(() => vi.restoreAllMocks());
	afterEach(() => vi.restoreAllMocks());

	it('returns 500 with missing-input-secret when TURNSTILE_SECRET_KEY is empty', async () => {
		const env = { ...TEST_ENV, TURNSTILE_SECRET_KEY: '' };
		const res = await worker.fetch(
			new Request('https://w/', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ token: 'abc' }),
			}),
			env,
		);
		expect(res.status).toBe(500);
		const body = (await res.json()) as { 'error-codes': string[] };
		expect(body['error-codes']).toContain('missing-input-secret');
	});
});
