/**
 * Structured logging helpers. Output is JSON-per-line so Workers Observability
 * + log-shipping pipelines can parse + index without regex hacks.
 */

import type { SiteverifyLogEntry, ErrorCode } from './types.js';

export interface LogContext {
	durationMs: number;
	upstreamStatus?: number;
	errorCodes?: ErrorCode[];
	cdataValue?: string;
	remoteipPresent: boolean;
	idempotencyKeyPresent: boolean;
}

export function logSiteverify(outcome: 'ok' | 'fail' | 'error', ctx: LogContext): void {
	const entry: SiteverifyLogEntry = {
		level: outcome === 'ok' ? 'info' : outcome === 'fail' ? 'warn' : 'error',
		event: 'siteverify',
		outcome,
		duration_ms: ctx.durationMs,
		upstream_status: ctx.upstreamStatus,
		error_codes: ctx.errorCodes ?? [],
		cdata_present: typeof ctx.cdataValue === 'string' && ctx.cdataValue.length > 0,
		cdata_value: ctx.cdataValue,
		remoteip_present: ctx.remoteipPresent,
		idempotency_key_present: ctx.idempotencyKeyPresent,
		ts: new Date().toISOString(),
	};
	// console.log goes to Workers logs and Observability.
	// Using a JSON line for machine-readability.
	console.log(JSON.stringify(entry));
}
