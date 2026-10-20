import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { useBackend } from "../store/backend";
import { useLlm } from "../store/llm";

export default function Dashboard() {
	const { missing, health, refresh } = useBackend();
	const { providers, refresh: refreshLlm } = useLlm();
	const [kpis, setKpis] = useState<{ label: string; value: number | string }[]>(
		[],
	);
	const [flowsPreview, setFlowsPreview] = useState<
		{ id: string; name: string; status: string }[]
	>([]);
	const [loading, setLoading] = useState(true);
	const [failed, setFailed] = useState(false);
	useEffect(() => {
		refresh();
		refreshLlm();
		api<{
			kpis: { label: string; value: number | string }[];
			flows_preview?: { id: string; name: string; status: string }[];
		}>("/api/dashboard")
			.then((j) => {
				setKpis(j.kpis ?? []);
				setFlowsPreview(j.flows_preview ?? []);
				setLoading(false);
			})
			.catch(() => {
				setFailed(true);
				setLoading(false);
			});
	}, [refresh, refreshLlm]);
	const llmOk = providers.some((p) => p.ok);
	const kpiValue = (label: string) =>
		kpis.find((k) => k.label === label)?.value ?? "-";
	return (
		<div>
			<h1 className="text-3xl font-bold">Demo the whole Craft family.</h1>
			<p className="mt-2 text-slate-300">
				One page per Craft app, real headless demos, a job engine with
				provenance, and twelve readymade multi-app flows you can run or edit.
				Every demo shells to the installed CLI - no mock pixels.
			</p>
			<div
				data-testid="dashboard"
				className="mt-4 flex flex-wrap items-center gap-3 text-sm"
			>
				<span className="flex items-center gap-1">
					<span
						className={`inline-block h-2 w-2 rounded-full ${health ? "bg-emerald-400" : "bg-red-400"}`}
					/>
					Backend{" "}
					{health ? `ok (${health.installed}/${health.apps} apps)` : "down"}
				</span>
				<span className="flex items-center gap-1">
					<span
						className={`inline-block h-2 w-2 rounded-full ${llmOk ? "bg-emerald-400" : "bg-slate-600"}`}
					/>
					LLM {llmOk ? "available" : "not detected"}
				</span>
			</div>
			{loading && (
				<p className="mt-4 text-sm text-slate-300">Loading dashboard...</p>
			)}
			{failed && (
				<p className="mt-4 text-sm text-amber-300">
					Backend unreachable. Start it, then{" "}
					<button
						type="button"
						className="underline"
						onClick={() => window.location.reload()}
					>
						retry
					</button>
					.
				</p>
			)}
			<div className="mt-4 flex gap-3">
				<Link
					to="/craft/cad"
					data-testid="hero-cta"
					className="rounded bg-amber-500 px-5 py-2 font-semibold text-slate-950"
				>
					Run the CAD house plan
				</Link>
				<Link
					to="/flows"
					data-testid="flows-cta"
					className="rounded bg-slate-800 px-5 py-2"
				>
					Browse flows
				</Link>
				<Link to="/help" className="rounded border border-slate-700 px-5 py-2">
					How it works
				</Link>
			</div>
			{missing.length > 0 && (
				<Link
					to="/onboarding"
					data-testid="onboarding-cta"
					className="mt-4 block rounded border-2 border-red-500 bg-red-950 p-4 font-semibold text-red-200"
				>
					{missing.length} Craft app(s) missing (
					{missing.slice(0, 4).join(", ")}
					{missing.length > 4 ? "..." : ""}) - install them to clear MOCK badges
				</Link>
			)}
			<div className="mt-6 grid gap-3 md:grid-cols-3">
				<Link
					to="/flows"
					className="rounded border border-slate-800 bg-slate-900 p-4 hover:border-amber-500/50"
				>
					<p className="text-xs uppercase tracking-widest text-amber-400">
						Multi-app
					</p>
					<p className="mt-1 text-lg font-semibold">Flows</p>
					<p className="text-sm text-slate-300">
						{kpiValue("Flows")} readymade chains - grade, lay out, assemble -
						with a CRUD step editor.
					</p>
				</Link>
				<Link
					to="/hands-in"
					className="rounded border border-slate-800 bg-slate-900 p-4 hover:border-amber-500/50"
				>
					<p className="text-xs uppercase tracking-widest text-amber-400">
						Watch it build
					</p>
					<p className="mt-1 text-lg font-semibold">Hands-in</p>
					<p className="text-sm text-slate-300">
						{kpiValue("Live demos")} demos stream each CLI step, with playback
						controls.
					</p>
				</Link>
				<Link
					to="/depot"
					className="rounded border border-slate-800 bg-slate-900 p-4 hover:border-amber-500/50"
				>
					<p className="text-xs uppercase tracking-widest text-amber-400">
						Every run
					</p>
					<p className="mt-1 text-lg font-semibold">Depot</p>
					<p className="text-sm text-slate-300">
						{kpiValue("Demo runs")} demo runs kept with artifacts and source
						links.
					</p>
				</Link>
			</div>

			{flowsPreview.length > 0 && (
				<div className="mt-4">
					<p className="text-xs uppercase tracking-widest text-slate-400">
						Readymade
					</p>
					<div className="mt-2 flex flex-wrap gap-2">
						{flowsPreview.map((flow) => (
							<Link
								key={flow.id}
								to={`/flows/${flow.id}`}
								className="rounded bg-slate-800 px-2 py-1 text-xs text-slate-200 hover:bg-slate-700"
							>
								{flow.name}
								{flow.status === "blocked" && (
									<span className="ml-1 text-amber-300">blocked</span>
								)}
							</Link>
						))}
					</div>
				</div>
			)}

			<div className="mt-6 grid grid-cols-2 gap-3 md:grid-cols-4">
				{kpis.map((k) => (
					<div
						key={k.label}
						data-testid={`kpi-${k.label.toLowerCase().replace(/\s+/g, "-")}`}
						className="rounded border border-slate-800 bg-slate-900 p-4"
					>
						<p className="text-2xl font-bold">{k.value}</p>
						<p className="text-sm text-slate-300">{k.label}</p>
					</div>
				))}
			</div>
			<p className="mt-4 text-sm text-slate-300">
				Numbers update live from the backend on this machine.
			</p>
		</div>
	);
}
