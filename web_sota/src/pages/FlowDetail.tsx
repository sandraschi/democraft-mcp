import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api, apiBase, type Flow } from "../lib/api";

interface RunStep {
	index: number;
	app: string;
	demo: string;
	note?: string;
	status: string;
	artifacts: string[];
	error?: string | null;
}

interface FlowRun {
	id: string;
	status: string;
	steps: RunStep[];
	artifacts: string[];
	error?: string | null;
}

const DOT: Record<string, string> = {
	succeeded: "bg-emerald-400",
	running: "bg-amber-400",
	failed: "bg-red-400",
};

export default function FlowDetail() {
	const { id = "" } = useParams();
	const navigate = useNavigate();
	const [flow, setFlow] = useState<Flow | null>(null);
	const [run, setRun] = useState<FlowRun | null>(null);
	const [runId, setRunId] = useState("");
	const [toast, setToast] = useState("");
	const [busy, setBusy] = useState(false);

	useEffect(() => {
		api<{ flow: Flow }>(`/api/flows/${id}`)
			.then((j) => setFlow(j.flow))
			.catch(() => setToast("Flow not found."));
	}, [id]);

	useEffect(() => {
		if (!runId) return;
		let stopped = false;
		async function tick() {
			try {
				const j = await api<{ run: FlowRun }>(`/api/flows/runs/${runId}`);
				if (stopped) return;
				setRun(j.run);
				if (j.run.status === "running") {
					window.setTimeout(tick, 1500);
				} else {
					setToast(
						j.run.status === "succeeded"
							? "Flow finished - artifacts below."
							: `Flow ${j.run.status}${j.run.error ? `: ${j.run.error}` : ""}`,
					);
				}
			} catch {
				if (!stopped) setToast("Lost the run; backend may have restarted.");
			}
		}
		tick();
		return () => {
			stopped = true;
		};
	}, [runId]);

	async function runFlow() {
		setBusy(true);
		setToast("");
		try {
			const j = await api<{
				success: boolean;
				run?: FlowRun;
				message?: string;
			}>(`/api/flows/${id}/run`, { method: "POST" });
			if (!j.success || !j.run) throw new Error(j.message ?? "run rejected");
			setRun(j.run);
			setRunId(j.run.id);
		} catch (e) {
			setToast(`${e}`);
		} finally {
			setBusy(false);
		}
	}

	async function removeFlow() {
		if (!window.confirm(`Delete flow "${flow?.name}"?`)) return;
		await api(`/api/flows/${id}`, { method: "DELETE" });
		navigate("/flows");
	}

	if (!flow) {
		return (
			<p className="text-sm text-slate-300">{toast || "Loading flow..."}</p>
		);
	}

	const blocked = flow.status === "blocked";

	return (
		<div data-testid="flow-detail">
			<div className="flex flex-wrap items-start justify-between gap-3">
				<div>
					<Link to="/flows" className="text-xs underline text-slate-400">
						Flows
					</Link>
					<h1 className="mt-1 text-2xl font-bold">{flow.name}</h1>
					<p className="mt-1 max-w-2xl text-sm text-slate-300">
						{flow.description}
					</p>
					{blocked && (
						<p className="mt-2 text-sm text-amber-300">
							Blocked: {flow.blocked_reason}
						</p>
					)}
				</div>
				<div className="flex gap-2">
					<button
						type="button"
						data-testid="flow-run"
						onClick={runFlow}
						disabled={busy || blocked}
						className="rounded bg-amber-500 px-4 py-2 text-sm font-semibold text-slate-950 disabled:opacity-40"
					>
						{busy ? "Starting..." : "Run flow"}
					</button>
					<Link
						to={`/flows/${flow.id}/edit`}
						className="rounded bg-slate-800 px-4 py-2 text-sm"
					>
						Edit
					</Link>
					<button
						type="button"
						onClick={removeFlow}
						className="rounded bg-slate-800 px-4 py-2 text-sm text-red-300"
					>
						Delete
					</button>
				</div>
			</div>

			<table className="mt-5 w-full text-left text-sm">
				<thead className="text-xs uppercase tracking-wide text-slate-400">
					<tr>
						<th className="py-2 pr-3">#</th>
						<th className="py-2 pr-3">App</th>
						<th className="py-2 pr-3">Demo</th>
						<th className="py-2 pr-3">Note</th>
						<th className="py-2">Status</th>
					</tr>
				</thead>
				<tbody>
					{flow.steps.map((step, index) => {
						const live = run?.steps.find((s) => s.index === index + 1);
						return (
							<tr
								key={`${step.app}-${step.demo}-${step.note ?? ""}`}
								className="border-t border-slate-800"
							>
								<td className="py-2 pr-3 text-slate-400">{index + 1}</td>
								<td className="py-2 pr-3 font-semibold">{step.app}</td>
								<td className="py-2 pr-3">{step.demo}</td>
								<td className="py-2 pr-3 text-slate-400">{step.note}</td>
								<td className="py-2">
									<span className="flex items-center gap-2 text-xs">
										<span
											className={`h-2 w-2 rounded-full ${
												DOT[live?.status ?? ""] ?? "bg-slate-600"
											}`}
										/>
										{live?.status ?? "pending"}
									</span>
								</td>
							</tr>
						);
					})}
				</tbody>
			</table>

			{toast && <p className="mt-3 text-sm text-slate-300">{toast}</p>}

			{run && run.artifacts.length > 0 && (
				<div
					data-testid="flow-artifacts"
					className="mt-4 rounded border border-slate-800 bg-slate-900 p-4"
				>
					<p className="font-semibold">Artifacts ({run.artifacts.length})</p>
					<ul className="mt-2 list-disc pl-5 text-sm text-slate-300">
						{run.artifacts.map((artifact) => (
							<li key={artifact} className="break-all">
								<a
									href={`${apiBase()}/api/flow-artifacts/${artifact}`}
									target="_blank"
									rel="noreferrer"
									className="underline"
								>
									{artifact.split("/").pop()}
								</a>
							</li>
						))}
					</ul>
				</div>
			)}
		</div>
	);
}
