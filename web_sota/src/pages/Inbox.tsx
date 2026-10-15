import { useEffect, useState } from "react";
import { api, apiBase } from "../lib/api";

interface Run {
	app: string;
	demo: string;
	artifacts: number;
	files: string[];
}

export default function Inbox() {
	const [runs, setRuns] = useState<Run[]>([]);
	const [query, setQuery] = useState("");
	const [loading, setLoading] = useState(true);
	const [failed, setFailed] = useState(false);
	useEffect(() => {
		api<{ runs: Run[] }>("/api/runs")
			.then((j) => {
				setRuns(j.runs);
				setLoading(false);
			})
			.catch(() => {
				setFailed(true);
				setLoading(false);
			});
	}, []);
	const shown = runs.filter((r) =>
		`${r.app}/${r.demo}`.toLowerCase().includes(query.toLowerCase()),
	);
	return (
		<div data-testid="inbox-page">
			<h1 className="text-2xl font-bold">Inbox - demo runs</h1>
			<div className="mt-2 flex items-center gap-2 text-sm">
				<label htmlFor="inbox-search">Search</label>
				<input
					id="inbox-search"
					data-testid="inbox-search"
					value={query}
					onChange={(e) => setQuery(e.target.value)}
					placeholder="filter app/demo..."
					className="rounded bg-slate-800 p-1"
				/>
				<span data-testid="inbox-count" className="text-slate-300">
					{shown.length} of {runs.length} runs
				</span>
			</div>
			{loading && (
				<p className="mt-2 text-sm text-slate-300">Loading runs...</p>
			)}
			{failed && (
				<p className="mt-2 text-sm text-amber-300">
					Backend unreachable - start it and retry.
				</p>
			)}
			{!loading && !failed && !runs.length && (
				<p className="mt-2 text-sm text-slate-300">
					No demo runs yet. Run one from any Craft page - every attempt lands
					here, including failures.
				</p>
			)}
			<ul className="mt-4 flex flex-col gap-2">
				{shown.map((r) => (
					<li
						key={`${r.app}/${r.demo}`}
						className="rounded border border-slate-800 bg-slate-900 p-3 text-sm"
					>
						<span className="font-semibold">
							{r.app}/{r.demo}
						</span>{" "}
						- {r.artifacts} artifacts
						<ul className="mt-1 list-disc pl-5 text-sm text-slate-300">
							{r.files.map((f) => (
								<li key={f} className="break-all">
									<a
										href={`${apiBase()}/api/artifacts/${r.app}/${r.demo}/${f}`}
										target="_blank"
										rel="noreferrer"
										className="underline"
									>
										{f}
									</a>
								</li>
							))}
						</ul>
					</li>
				))}
			</ul>
		</div>
	);
}
