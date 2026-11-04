import {
	AudioWaveform,
	Binary,
	Box,
	Clapperboard,
	Database,
	DraftingCompass,
	FileStack,
	FileText,
	Frame,
	Image,
	Lamp,
	LayoutTemplate,
	type LucideIcon,
	PenTool,
	Presentation,
	Server,
	Sheet,
	Wand2,
} from "lucide-react";

/** Visual identity per Craft app: a hue for edge markers and an icon. */
export interface AppMeta {
	hue: string;
	icon: LucideIcon;
}

const META: Record<string, AppMeta> = {
	cad: { hue: "#38bdf8", icon: DraftingCompass },
	deck: { hue: "#fb923c", icon: Presentation },
	design: { hue: "#f472b6", icon: LayoutTemplate },
	effect: { hue: "#a78bfa", icon: Wand2 },
	fig: { hue: "#2dd4bf", icon: Frame },
	film: { hue: "#f87171", icon: Clapperboard },
	grid: { hue: "#4ade80", icon: Sheet },
	sound: { hue: "#facc15", icon: AudioWaveform },
	word: { hue: "#60a5fa", icon: FileText },
	pdf: { hue: "#e879f9", icon: FileStack },
	light: { hue: "#fde68a", icon: Lamp },
	photo: { hue: "#22d3ee", icon: Image },
	vector: { hue: "#fbbf24", icon: PenTool },
	solid: { hue: "#94a3b8", icon: Box },
	database: { hue: "#10b981", icon: Database },
	virt: { hue: "#3b82f6", icon: Server },
	rev: { hue: "#a855f7", icon: Binary },
	doc: { hue: "#0284c7", icon: FileText },
};

const FALLBACK: AppMeta = { hue: "#a1a1aa", icon: Box };

export function appMeta(key: string): AppMeta {
	return META[key] ?? FALLBACK;
}

export const IMAGE_EXT = /\.(png|jpe?g|gif|webp)$/i;

/** True when a demo shipped within the last `days` days. */
export function isNew(added?: string, days = 21): boolean {
	if (!added) return false;
	const t = Date.parse(added);
	return !Number.isNaN(t) && Date.now() - t < days * 86_400_000;
}
