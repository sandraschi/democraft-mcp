import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, apiBase } from "../lib/api";

interface Run {
	app: string;
	demo: string;
	run_id: string;
	started?: string;
	topic?: string;
	artifacts: number;
	files: string[];
	inputs: string[];
	latest: boolean;
}

function artifactUrl(run: Run, file: string): string {
	return run.latest
		? `${apiBase()}/api/artifacts/${run.app}/${run.demo}/${file}`
		: `${apiBase()}/api/history/${run.app}/${run.demo}/${run.run_id}/${file}`;
}

function when(iso?: string): string {
	if (!iso) return "unknown time";
	const date = new Date(iso);
	return Number.isNaN(date.getTime()) ? iso : date.toLocaleString();
}

export default function Depot() {
	const [runs, setRuns] = useState<Run[]>([]);
	const [query, setQuery] = useState("");
	const [loading, setLoading] = useState(true);
	const [failed, setFailed] = useState(false);
	const [view, setView] = useState<"cards" | "list">(() => {
		const stored = localStorage.getItem("democraft.depot.view");
		return stored === "list" ? "list" : "cards";
	});

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

	function pick(next: "cards" | "list") {
		setView(next);
		localStorage.setItem("democraft.depot.view", next);
	}

	const shown = runs.filter((r) =>
		`${r.app}/${r.demo} ${r.topic ?? ""}`
			.toLowerCase()
			.includes(query.toLowerCase()),
	);

	return (
		<div data-testid="depot-page">
			<h1 className="text-2xl font-bold">Depot - every demo run</h1>
			<p className="mt-1 text-sm text-slate-400">
				Each run keeps its artifacts and provenance; the newest stays live,
				older runs move to history.
			</p>
			<div className="mt-3 flex flex-wrap items-center gap-3 text-sm">
				<label htmlFor="depot-search">Search</label>
				<input
					id="depot-search"
					data-testid="depot-search"
					value={query}
					onChange={(e) => setQuery(e.target.value)}
					placeholder="filter app/demo/topic..."
					className="rounded bg-slate-800 p-1"
				/>
				<span data-testid="depot-count" className="text-slate-300">
					{shown.length} of {runs.length} runs
				</span>
				<div className="ml-auto flex gap-1">
					<button
						type="button"
						data-testid="depot-view-cards"
						onClick={() => pick("cards")}
						className={`rounded px-3 py-1 ${
							view === "cards"
								? "bg-amber-500 font-semibold text-slate-950"
								: "bg-slate-800 text-slate-300"
						}`}
					>
						Cards
					</button>
					<button
						type="button"
						data-testid="depot-view-list"
						onClick={() => pick("list")}
						className={`rounded px-3 py-1 ${
							view === "list"
								? "bg-amber-500 font-semibold text-slate-950"
								: "bg-slate-800 text-slate-300"
						}`}
					>
						List
					</button>
				</div>
			</div>

			{loading && (
				<p className="mt-3 text-sm text-slate-300">Loading runs...</p>
			)}
			{failed && (
				<p className="mt-3 text-sm text-amber-300">
					Backend unreachable - start it and retry.
				</p>
			)}
			{!loading && !failed && !runs.length && (
				<p className="mt-3 text-sm text-slate-300">
					No demo runs yet. Run one from any Craft page - every attempt lands
					here, including failures.
				</p>
			)}

			{view === "cards" ? (
				<div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
					{shown.map((r) => (
						<article
							key={`${r.app}/${r.demo}/${r.run_id}`}
							data-testid="depot-card"
							className="rounded border border-slate-800 bg-slate-900 p-4 text-sm"
						>
							<div className="flex items-start justify-between gap-2">
								<div>
									<p className="font-semibold">
										{r.app}/{r.demo}
									</p>
									<p className="text-xs text-slate-400">{when(r.started)}</p>
								</div>
								<span
									className={`rounded px-2 py-0.5 text-xs ${
										r.latest
											? "bg-emerald-500/20 text-emerald-300"
											: "bg-slate-800 text-slate-400"
									}`}
								>
									{r.latest ? "latest" : r.run_id}
								</span>
							</div>
							{r.topic && (
								<p className="mt-2 text-slate-300">Topic: {r.topic}</p>
							)}
							<p className="mt-1 text-xs text-slate-400">
								{r.artifacts} artifacts
							</p>
							{r.inputs.length > 0 && (
								<p className="mt-2 text-xs text-slate-400">
									source:{" "}
									{r.inputs.map((f) => (
										<a
											key={f}
											data-testid="depot-source"
											href={artifactUrl(r, f)}
											target="_blank"
											rel="noreferrer"
											className="mr-2 underline"
										>
											{f}
										</a>
									))}
								</p>
							)}
							<div className="mt-2 flex flex-wrap gap-2 text-xs">
								{r.files.slice(0, 6).map((f) => (
									<a
										key={f}
										href={artifactUrl(r, f)}
										target="_blank"
										rel="noreferrer"
										className="rounded bg-slate-800 px-2 py-1 underline"
									>
										{f.split("/").pop()}
									</a>
								))}
							</div>
							<div className="mt-3 flex gap-3 text-xs">
								<Link to={`/craft/${r.app}`} className="underline">
									Open app
								</Link>
								<Link
									to={`/craft/${r.app}?demo=${r.demo}&watch=1`}
									className="underline"
								>
									Replay hands-in
								</Link>
							</div>
						</article>
					))}
				</div>
			) : (
				<div className="mt-4 overflow-x-auto">
					<table className="w-full text-left text-sm">
						<thead className="text-xs uppercase tracking-wide text-slate-400">
							<tr>
								<th className="py-2 pr-4">Run</th>
								<th className="py-2 pr-4">When</th>
								<th className="py-2 pr-4">Topic</th>
								<th className="py-2 pr-4">Artifacts</th>
								<th className="py-2">Links</th>
							</tr>
						</thead>
						<tbody>
							{shown.map((r) => (
								<tr
									key={`${r.app}/${r.demo}/${r.run_id}`}
									data-testid="depot-row"
									className="border-t border-slate-800"
								>
									<td className="py-2 pr-4 font-semibold">
										{r.app}/{r.demo}
										{r.latest && (
											<span className="ml-2 rounded bg-emerald-500/20 px-1 text-xs text-emerald-300">
												latest
											</span>
										)}
									</td>
									<td className="py-2 pr-4 text-slate-400">
										{when(r.started)}
									</td>
									<td className="py-2 pr-4 text-slate-300">{r.topic || "-"}</td>
									<td className="py-2 pr-4">{r.artifacts}</td>
									<td className="py-2">
										<Link to={`/craft/${r.app}`} className="mr-3 underline">
											app
										</Link>
										{r.files.slice(0, 3).map((f) => (
											<a
												key={f}
												href={artifactUrl(r, f)}
												target="_blank"
												rel="noreferrer"
												className="mr-3 underline"
											>
												{f.split("/").pop()}
											</a>
										))}
									</td>
								</tr>
							))}
						</tbody>
					</table>
				</div>
			)}
		</div>
	);
}
