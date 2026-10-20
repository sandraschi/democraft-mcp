import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type Flow } from "../lib/api";

const BADGE: Record<string, string> = {
	ready: "bg-emerald-500/20 text-emerald-300",
	exploratory: "bg-amber-500/20 text-amber-300",
	blocked: "bg-slate-700 text-slate-300",
};

export default function Flows() {
	const [flows, setFlows] = useState<Flow[]>([]);
	const [failed, setFailed] = useState(false);

	useEffect(() => {
		api<{ flows: Flow[] }>("/api/flows")
			.then((j) => setFlows(j.flows))
			.catch(() => setFailed(true));
	}, []);

	return (
		<div data-testid="flows-page">
			<div className="flex flex-wrap items-start justify-between gap-3">
				<div>
					<h1 className="text-2xl font-bold">Flows</h1>
					<p className="mt-1 max-w-2xl text-sm text-slate-400">
						Readymade multi-app sequences: grade in PhotoCraft, lay out in
						DesignCraft, assemble in PdfCraft. Each flow is an ordered list of
						real demos; the runner records every step and bundles the artifacts.
						More flows arrive as the Craft suite grows.
					</p>
				</div>
				<Link
					to="/flows/new"
					data-testid="flow-new"
					className="rounded bg-amber-500 px-4 py-2 text-sm font-semibold text-slate-950"
				>
					New flow
				</Link>
			</div>

			{failed && (
				<p className="mt-3 text-sm text-amber-300">
					Backend unreachable - start it and retry.
				</p>
			)}
			<div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
				{flows.map((flow) => (
					<article
						key={flow.id}
						data-testid="flow-card"
						className="rounded border border-slate-800 bg-slate-900 p-4"
					>
						<div className="flex items-start justify-between gap-2">
							<h2 className="font-semibold">{flow.name}</h2>
							<span
								className={`rounded px-2 py-0.5 text-xs ${
									BADGE[flow.status] ?? BADGE.blocked
								}`}
							>
								{flow.status}
							</span>
						</div>
						<p className="mt-2 text-sm text-slate-300">{flow.description}</p>
						<p className="mt-1 text-xs text-slate-400">
							{flow.steps.length} steps:{" "}
							{flow.steps.map((s) => s.app).join(" -> ")}
						</p>
						{flow.status === "blocked" && flow.blocked_reason && (
							<p className="mt-2 text-xs text-amber-300">
								{flow.blocked_reason}
							</p>
						)}
						<div className="mt-3 flex gap-3 text-sm">
							<Link to={`/flows/${flow.id}`} className="underline">
								Open
							</Link>
							<Link to={`/flows/${flow.id}/edit`} className="underline">
								Edit
							</Link>
						</div>
					</article>
				))}
			</div>
		</div>
	);
}
