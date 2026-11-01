import {
	Box,
	File,
	FileAudio,
	FileCode2,
	FileSpreadsheet,
	FileText,
	FileVideo,
	type LucideIcon,
} from "lucide-react";
import { IMAGE_EXT } from "../lib/appMeta";

const KIND: [RegExp, LucideIcon, string][] = [
	[/\.(mp4|mov|webm|gif)$/i, FileVideo, "video"],
	[/\.(wav|mp3|flac|aiff?)$/i, FileAudio, "audio"],
	[/\.(xlsx|csv)$/i, FileSpreadsheet, "sheet"],
	[/\.(step|stp|stl|3mf|sc|dxf)$/i, Box, "model"],
	[/\.(json|jsonl|py|svg)$/i, FileCode2, "data"],
	[/\.(md|txt|pdf|docx|epub)$/i, FileText, "document"],
];

function kindOf(file: string): [LucideIcon, string] {
	for (const [re, icon, label] of KIND) if (re.test(file)) return [icon, label];
	return [File, "file"];
}

/**
 * A run's artifacts: images as prints first, everything else as typed chips.
 * `urlFor` maps a run-relative path to its served URL.
 */
export default function ArtifactGrid({
	files,
	urlFor,
	maxImages = 8,
}: {
	files: string[];
	urlFor: (file: string) => string;
	maxImages?: number;
}) {
	const rel = files.map((f) => f.replace(/\\/g, "/"));
	const images = rel.filter(
		(f) => IMAGE_EXT.test(f) && !/(^|\/)diff\./i.test(f),
	);
	const shown = images.slice(0, maxImages);
	const others = rel.filter(
		(f) => !shown.includes(f) && !f.endsWith("run.json"),
	);
	const reports = others.filter((f) => /report\.md$/i.test(f));
	const rest = others.filter((f) => !reports.includes(f));
	return (
		<div data-testid="artifact-grid">
			{shown.length > 0 && (
				<div className="grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-4">
					{shown.map((f) => (
						<figure key={f} className="min-w-0">
							<a
								href={urlFor(f)}
								target="_blank"
								rel="noreferrer"
								className="print block aspect-[4/3] overflow-hidden"
							>
								<img src={urlFor(f)} alt={f} loading="lazy" />
							</a>
							<figcaption className="mt-1 truncate text-xs text-muted">
								{f.split("/").pop()}
							</figcaption>
						</figure>
					))}
				</div>
			)}
			{reports.length > 0 && (
				<p className="mt-4 text-sm">
					{reports.map((f) => (
						<a
							key={f}
							href={urlFor(f)}
							target="_blank"
							rel="noreferrer"
							data-testid="artifact-report"
							className="mr-3 font-medium text-accent underline-offset-4 hover:underline"
						>
							Read {f.split("/").pop()}
						</a>
					))}
				</p>
			)}
			{rest.length > 0 && (
				<ul className="mt-3 flex flex-wrap gap-2 text-xs">
					{rest.map((f) => {
						const [Icon, label] = kindOf(f);
						return (
							<li key={f}>
								<a
									href={urlFor(f)}
									target="_blank"
									rel="noreferrer"
									title={`${label}: ${f}`}
									className="flex items-center gap-1.5 rounded-md border border-line bg-raised px-2 py-1 text-paper hover:border-accent/60"
								>
									<Icon size={13} className="text-muted" />
									{f.split("/").pop()}
								</a>
							</li>
						);
					})}
				</ul>
			)}
		</div>
	);
}
