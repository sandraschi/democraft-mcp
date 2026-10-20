declare global {
	interface Window {
		__TAURI__?: unknown;
		__TAURI_INTERNALS__?: unknown;
	}
}

function isTauri(): boolean {
	if (typeof window === "undefined") return false;
	return (
		window.__TAURI__ !== undefined ||
		window.__TAURI_INTERNALS__ !== undefined ||
		window.location.hostname === "tauri.localhost"
	);
}

// Canonical shape: same-origin "" everywhere EXCEPT behind a Tauri gate,
// where the baked VITE_API_TARGET is used. Absolute backend URLs in plain
// browser tabs break on any non-localhost hostname (CORS).
const BASE = isTauri()
	? ((import.meta.env.VITE_API_TARGET as string | undefined) ?? "")
	: "";

export function apiBase(): string {
	return BASE;
}

/** Local calendar date as YYYY-MM-DD (modified times are local, not UTC). */
export function todayLocal(): string {
	const d = new Date();
	const m = String(d.getMonth() + 1).padStart(2, "0");
	const day = String(d.getDate()).padStart(2, "0");
	return `${d.getFullYear()}-${m}-${day}`;
}

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
	const r = await fetch(`${BASE}${path}`, {
		headers: { "content-type": "application/json" },
		...init,
	});
	if (!r.ok) throw new Error(`${path}: ${r.status}`);
	return (await r.json()) as T;
}

export interface CraftDemo {
	id: string;
	title: string;
	blurb: string;
	requires: string;
	topics?: string[];
	live?: boolean;
}

export interface FlowStep {
	app: string;
	demo: string;
	note?: string;
	topic?: string;
	_key?: string;
}

export interface Flow {
	id: string;
	name: string;
	description?: string;
	status: string;
	blocked_reason?: string;
	steps: FlowStep[];
}
export interface CraftApp {
	key: string;
	name: string;
	installed: boolean;
	runnable: boolean;
	tagline: string;
	clone_of: string;
	description: string;
	gaps: string[];
	demos: CraftDemo[];
	/** Installed CLI version, read from the binary on this machine. */
	version?: string | null;
	/** CLI file mtime, local time, ISO-ish (YYYY-MM-DDTHH:MM:SS). */
	modified?: string | null;
	/** Last accepted baseline version; differs from `version` after an upgrade. */
	baseline_version?: string | null;
	/** True when the installed build differs from the accepted baseline. */
	drift?: boolean;
}
