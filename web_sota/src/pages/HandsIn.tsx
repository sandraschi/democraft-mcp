import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type CraftApp } from "../lib/api";

export default function HandsIn() {
	const [apps, setApps] = useState<CraftApp[]>([]);
	const [failed, setFailed] = useState(false);

	useEffect(() => {
		api<{ apps: CraftApp[] }>("/api/crafts")
			.then((j) => setApps(j.apps))
			.catch(() => setFailed(true));
	}, []);

	const live = apps.flatMap((a) =>
		a.demos.filter((d) => d.live).map((d) => ({ app: a, demo: d })),
	);

	return (
		<div data-testid="hands-in-page">
			<h1 className="text-2xl font-bold">Hands-in</h1>
			<p className="mt-1 max-w-2xl text-sm text-slate-400">
				Demos worth watching while they run: each CLI step streams in, and
				artifacts appear as the engine writes them. No progress theatre - if a
				step fails, you see the return code and stderr.
			</p>
			{failed && (
				<p className="mt-3 text-sm text-amber-300">
					Backend unreachable - start it and retry.
				</p>
			)}
			<div className="mt-4 grid gap-3 md:grid-cols-2">
				{live.map(({ app, demo }) => (
					<article
						key={`${app.key}/${demo.id}`}
						data-testid="hands-in-card"
						className="rounded border border-slate-800 bg-slate-900 p-4"
					>
						<p className="text-xs uppercase tracking-widest text-amber-400">
							{app.name}
						</p>
						<h2 className="mt-1 font-semibold">{demo.title}</h2>
						<p className="mt-2 text-sm text-slate-300">{demo.blurb}</p>
						<Link
							to={`/craft/${app.key}?demo=${demo.id}&watch=1`}
							className="mt-3 inline-block rounded bg-amber-500 px-4 py-2 text-sm font-semibold text-slate-950"
						>
							Watch it build
						</Link>
					</article>
				))}
				{!failed && live.length === 0 && (
					<p className="text-sm text-slate-300">
						No live demos registered yet (a demo opts in with live=True).
					</p>
				)}
			</div>
		</div>
	);
}
