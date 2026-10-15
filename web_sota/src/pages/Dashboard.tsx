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
	const [loading, setLoading] = useState(true);
	const [failed, setFailed] = useState(false);
	useEffect(() => {
		refresh();
		refreshLlm();
		api<{ kpis: { label: string; value: number | string }[] }>("/api/dashboard")
			.then((j) => {
				setKpis(j.kpis ?? []);
				setLoading(false);
			})
			.catch(() => {
				setFailed(true);
				setLoading(false);
			});
	}, [refresh, refreshLlm]);
	const llmOk = providers.some((p) => p.ok);
	return (
		<div>
			<h1 className="text-3xl font-bold">Demo the whole Craft family.</h1>
			<p className="mt-2 text-slate-300">
				One page per Craft app. Every demo runs the real headless CLI plus a
				local-LLM step.
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
