import { create } from "zustand";
import { api } from "../lib/api";

export interface ProviderState {
	id: string;
	ok: boolean;
}

interface LlmState {
	providers: ProviderState[];
	provider: string;
	model: string;
	models: string[];
	gpu: boolean;
	probing: boolean;
	refresh: () => Promise<void>;
	setProvider: (p: string) => void;
	setModel: (m: string) => void;
	chat: (prompt: string) => Promise<{
		text?: string;
		skipped?: boolean;
		error?: string;
		model?: string;
	}>;
}

const LS_PROVIDER = "llm_provider";
const LS_MODEL = "llm_model";

function stored(key: string, fallback: string): string {
	try {
		return localStorage.getItem(key) ?? fallback;
	} catch {
		return fallback;
	}
}

function store(key: string, value: string): void {
	try {
		localStorage.setItem(key, value);
	} catch {
		/* private mode - selection simply does not persist */
	}
}

async function sleep(ms: number): Promise<void> {
	return new Promise((r) => setTimeout(r, ms));
}

export const useLlm = create<LlmState>((set, get) => ({
	providers: [],
	provider: stored(LS_PROVIDER, "ollama"),
	model: stored(LS_MODEL, "gemma4:12b"),
	models: [],
	gpu: false,
	probing: true,
	refresh: async () => {
		set({ probing: true });
		// Exponential backoff: 1s, 2s, 4s - backend may still be booting.
		let discover: {
			providers?: Record<string, boolean>;
			gpu?: boolean;
		} | null = null;
		for (const wait of [0, 1000, 2000, 4000]) {
			if (wait) await sleep(wait);
			try {
				discover = await api<{
					providers?: Record<string, boolean>;
					gpu?: boolean;
				}>("/api/llm/discover");
				break;
			} catch {
				discover = null;
			}
		}
		const found = discover?.providers ?? {};
		const providers: ProviderState[] = ["ollama", "lmstudio", "vllm"].map(
			(id) => ({
				id,
				ok: found[id] ?? false,
			}),
		);
		let models: string[] = [];
		try {
			const m = await api<{ models: string[] }>("/api/llm/models");
			models = m.models;
		} catch {
			models = [];
		}
		const savedProvider = stored(LS_PROVIDER, "ollama");
		const savedModel = stored(LS_MODEL, "gemma4:12b");
		const provider = providers.some((p) => p.id === savedProvider && p.ok)
			? savedProvider
			: "ollama";
		const model = models.includes(savedModel)
			? savedModel
			: (models[0] ?? savedModel);
		set({
			providers,
			provider,
			model,
			models,
			gpu: discover?.gpu ?? false,
			probing: false,
		});
	},
	setProvider: (p) => {
		store(LS_PROVIDER, p);
		set({ provider: p });
	},
	setModel: (m) => {
		store(LS_MODEL, m);
		set({ model: m });
	},
	chat: async (prompt) => {
		const r = await api<{
			success: boolean;
			text?: string;
			skipped?: boolean;
			error?: string;
			model?: string;
		}>("/api/llm/chat", {
			method: "POST",
			body: JSON.stringify({ prompt, model: get().model }),
		});
		return r;
	},
}));
