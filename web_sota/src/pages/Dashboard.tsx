import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { useBackend } from "../store/backend";

export default function Dashboard() {
	const { missing, refresh } = useBackend();
	const [kpis, setKpis] = useState<{ label: string; value: number | string }[]>(
		[],
	);
	useEffect(() => {
		refresh();
		api<{ kpis: { label: string; value: number | string }[] }>("/api/dashboard")
			.then((j) => setKpis(j.kpis ?? []))
			.catch(() => {});
	}, [refresh]);
	return (
		<div>
			<h1 className="text-3xl font-bold">Demo the whole Craft family.</h1>
			<p className="mt-2 text-slate-400">
				One page per Craft app. Every demo runs the real headless CLI plus a
				local-LLM step.
			</p>
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
						<p className="text-sm text-slate-400">{k.label}</p>
					</div>
				))}
			</div>
			<p className="mt-4 text-xs text-slate-500">
				Numbers update live from the backend on this machine.
			</p>
		</div>
	);
}
