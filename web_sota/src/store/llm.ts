import { create } from "zustand";
import { api } from "../lib/api";

export interface Provider {
	id: string;
	ok: boolean;
	models?: string[];
	default_model?: string;
	error?: string;
}
interface LlmState {
	providers: Provider[];
	model: string;
	refresh: () => Promise<void>;
	setModel: (m: string) => void;
	chat: (prompt: string) => Promise<{
		text?: string;
		skipped?: boolean;
		error?: string;
		model?: string;
	}>;
}

export const useLlm = create<LlmState>((set, get) => ({
	providers: [],
	model: "gemma4:12b",
	refresh: async () => {
		try {
			const r = await api<{ providers: Provider[] }>("/api/llm/providers");
			const ollama = r.providers.find((p) => p.id === "ollama");
			set({
				providers: r.providers,
				model: ollama?.default_model ?? get().model,
			});
		} catch {
			set({ providers: [] });
		}
	},
	setModel: (m) => set({ model: m }),
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
