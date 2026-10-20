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
}
