import { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function Logs() {
	const [logs, setLogs] = useState<
		{ ts: string; source: string; message: string }[]
	>([]);
	const [loading, setLoading] = useState(true);
	const [failed, setFailed] = useState(false);
	useEffect(() => {
		api<{ logs: { ts: string; source: string; message: string }[] }>(
			"/api/logs?limit=300",
		)
			.then((j) => {
				setLogs(j.logs ?? []);
				setLoading(false);
			})
			.catch(() => {
				setFailed(true);
				setLoading(false);
			});
	}, []);
	return (
		<div data-testid="logs-page">
			<h1 className="text-2xl font-bold">Logs</h1>
			{loading && (
				<p className="mt-2 text-sm text-slate-300">Loading logs...</p>
			)}
			{failed && (
				<p className="mt-2 text-sm text-amber-300">
					Backend unreachable - start it and retry.
				</p>
			)}
			<div className="mt-3 rounded border border-slate-800 bg-slate-900 p-3 font-mono text-sm">
				{logs.map((l) => (
					<p key={`${l.ts}-${l.source}-${l.message.slice(0, 32)}`}>
						[{l.ts}] {l.source}: {l.message}
					</p>
				))}
				{!logs.length && <p className="text-slate-300">No log entries yet.</p>}
			</div>
		</div>
	);
}
