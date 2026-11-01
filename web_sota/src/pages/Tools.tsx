import { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function Tools() {
	const [tools, setTools] = useState<
		{ name: string; pattern: string; operations?: string[] }[]
	>([]);
	const [open, setOpen] = useState<string | null>(null);
	const [loading, setLoading] = useState(true);
	const [failed, setFailed] = useState(false);
	useEffect(() => {
		api<{ tools: typeof tools }>("/api/tools")
			.then((j) => {
				setTools(j.tools);
				setLoading(false);
			})
			.catch(() => {
				setFailed(true);
				setLoading(false);
			});
	}, []);
	return (
		<div data-testid="tools-page">
			<h1 className="text-2xl font-bold">Tools</h1>
			<p className="text-sm text-muted">
				Discovered live from /api/tools - never hardcoded.
			</p>
			<span data-testid="tools-count" className="mt-1 text-sm text-muted">
				{tools.length} tools
			</span>
			{loading && <p className="mt-2 text-sm text-muted">Loading tools...</p>}
			{failed && (
				<p className="mt-2 text-sm text-amber-300">
					Backend unreachable - start it and retry.
				</p>
			)}
			<ul data-testid="tools-list" className="mt-4 flex flex-col gap-2">
				{tools.map((t) => (
					<li
						key={t.name}
						className="rounded-md border border-line bg-surface p-3"
					>
						<button
							type="button"
							className="font-mono font-semibold"
							onClick={() => setOpen(open === t.name ? null : t.name)}
						>
							{t.name} <span className="text-sm text-muted">({t.pattern})</span>
						</button>
						{open === t.name && t.operations && (
							<ul className="mt-2 list-disc pl-5 font-mono text-sm text-muted">
								{t.operations.map((o) => (
									<li key={o}>{o}</li>
								))}
							</ul>
						)}
					</li>
				))}
			</ul>
		</div>
	);
}
