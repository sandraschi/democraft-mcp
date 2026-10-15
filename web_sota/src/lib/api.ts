const BASE = (import.meta.env.VITE_API_TARGET as string | undefined) ?? "";

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
}
export interface CraftApp {
	key: string;
	name: string;
	installed: boolean;
	tagline: string;
	demos: CraftDemo[];
}
