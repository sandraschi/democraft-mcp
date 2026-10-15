import { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function Logs() {
	const [logs, setLogs] = useState<
		{ ts: string; source: string; message: string }[]
	>([]);
	useEffect(() => {
		api<{ logs: { ts: string; source: string; message: string }[] }>(
			"/api/logs?limit=300",
		)
			.then((j) => setLogs(j.logs ?? []))
			.catch(() => {});
	}, []);
	return (
		<div>
			<h1 className="text-2xl font-bold">Logs</h1>
			<div className="mt-3 rounded border border-slate-800 bg-slate-900 p-3 font-mono text-xs">
				{logs.map((l) => (
					<p key={`${l.ts}-${l.source}-${l.message.slice(0, 32)}`}>
						[{l.ts}] {l.source}: {l.message}
					</p>
				))}
				{!logs.length && <p className="text-slate-500">No log entries yet.</p>}
			</div>
		</div>
	);
}
