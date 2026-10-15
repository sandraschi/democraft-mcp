import { create } from "zustand";
import { api, type CraftApp } from "../lib/api";

interface BackendState {
	health: { status: string; apps: number; installed: number } | null;
	apps: CraftApp[];
	missing: string[];
	refresh: () => Promise<void>;
}

export const useBackend = create<BackendState>((set) => ({
	health: null,
	apps: [],
	missing: [],
	refresh: async () => {
		try {
			const [health, crafts] = await Promise.all([
				api<{ status: string; apps: number; installed: number }>("/api/health"),
				api<{ apps: CraftApp[] }>("/api/crafts"),
			]);
			set({
				health,
				apps: crafts.apps,
				missing: crafts.apps.filter((a) => !a.installed).map((a) => a.name),
			});
		} catch {
			set({ health: null });
		}
	},
}));
