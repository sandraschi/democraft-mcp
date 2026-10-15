import { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function Inbox() {
	const [runs, setRuns] = useState<
		{ app: string; demo: string; artifacts: number; files: string[] }[]
	>([]);
	useEffect(() => {
		api<{ runs: typeof runs }>("/api/runs")
			.then((j) => setRuns(j.runs))
			.catch(() => {});
	}, []);
	if (!runs.length)
		return (
			<div>
				<h1 className="text-2xl font-bold">Inbox</h1>
				<p className="mt-2 text-slate-400">
					No demo runs yet. Run one from any Craft page - every attempt lands
					here, including failures.
				</p>
			</div>
		);
	return (
		<div>
			<h1 className="text-2xl font-bold">Inbox - demo runs</h1>
			<ul className="mt-4 flex flex-col gap-2">
				{runs.map((r) => (
					<li
						key={`${r.app}/${r.demo}`}
						className="rounded border border-slate-800 bg-slate-900 p-3 text-sm"
					>
						<span className="font-semibold">
							{r.app}/{r.demo}
						</span>{" "}
						- {r.artifacts} artifacts
						<ul className="mt-1 list-disc pl-5 text-xs text-slate-400">
							{r.files.map((f) => (
								<li key={f}>{f}</li>
							))}
						</ul>
					</li>
				))}
			</ul>
		</div>
	);
}
