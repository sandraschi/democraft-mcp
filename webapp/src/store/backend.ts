import { create } from "zustand";
import { api, type CraftApp } from "../lib/api";

interface BackendState {
	health: {
		status: string;
		apps: number;
		installed: number;
		version?: string;
	} | null;
	apps: CraftApp[];
	missing: string[];
	refresh: () => Promise<void>;
}

export const useBackend = create<BackendState>((set) => ({
	health: null,
	apps: [],
	missing: [],
	refresh: async () => {
		// Exponential backoff: 1s, 2s, 4s, 8s - backend may still be booting.
		for (const wait of [0, 1000, 2000, 4000, 8000]) {
			if (wait) await new Promise((r) => setTimeout(r, wait));
			try {
				const [health, crafts] = await Promise.all([
					api<{
						status: string;
						apps: number;
						installed: number;
						version?: string;
					}>("/api/health"),
					api<{ apps: CraftApp[] }>("/api/crafts"),
				]);
				set({
					health,
					apps: crafts.apps,
					missing: crafts.apps.filter((a) => !a.installed).map((a) => a.name),
				});
				return;
			} catch {
				/* retry on the backoff schedule */
			}
		}
		set({ health: null });
	},
}));
