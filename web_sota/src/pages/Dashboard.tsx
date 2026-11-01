import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import ContactSheet from "../components/ContactSheet";
import { api, type CraftApp, type GalleryTile } from "../lib/api";
import { appMeta, isNew } from "../lib/appMeta";
import { useBackend } from "../store/backend";
import { useLlm } from "../store/llm";

function AppRow({ a }: { a: CraftApp }) {
	const meta = appMeta(a.key);
	return (
		<Link
			to={`/craft/${a.key}`}
			data-testid={`dash-app-${a.key}`}
			className="group flex items-center gap-3 border-b border-line py-2.5 pl-3 transition-colors hover:bg-surface"
			style={{ borderLeft: `2px solid ${meta.hue}` }}
		>
			<meta.icon size={17} style={{ color: meta.hue }} className="shrink-0" />
			<span className="min-w-0 flex-1">
				<span className="block truncate text-sm font-medium text-paper">
					{a.name}
				</span>
				<span className="block truncate text-xs text-muted">
					for {a.clone_of}
				</span>
			</span>
			<span className="hidden text-xs text-muted sm:block">
				{a.demos.length - 1} demos
			</span>
			<span className="w-24 shrink-0 pr-3 text-right font-mono text-xs">
				{a.installed ? (
					<span className={a.drift ? "text-amber-300" : "text-muted"}>
						{a.version ?? "?"}
						{a.drift && " new"}
					</span>
				) : (
					<span className="text-red-300">missing</span>
				)}
			</span>
		</Link>
	);
}

export default function Dashboard() {
	const { apps, missing, health, refresh } = useBackend();
	const { providers, refresh: refreshLlm } = useLlm();
	const [kpis, setKpis] = useState<{ label: string; value: number | string }[]>(
		[],
	);
	const [tiles, setTiles] = useState<GalleryTile[]>([]);
	const [loading, setLoading] = useState(true);
	const [failed, setFailed] = useState(false);

	useEffect(() => {
		refresh();
		refreshLlm();
		Promise.all([
			api<{ kpis: { label: string; value: number | string }[] }>(
				"/api/dashboard",
			),
			api<{ tiles: GalleryTile[] }>("/api/gallery?limit=8"),
		])
			.then(([d, g]) => {
				setKpis(d.kpis ?? []);
				setTiles(g.tiles ?? []);
			})
			.catch(() => setFailed(true))
			.finally(() => setLoading(false));
	}, [refresh, refreshLlm]);

	const llmOk = providers.some((p) => p.ok);
	const core = apps.filter((a) => a.family !== "community");
	const community = apps.filter((a) => a.family === "community");
	const fresh = apps.flatMap((a) =>
		a.demos.filter((d) => isNew(d.added)).map((d) => ({ app: a, demo: d })),
	);

	return (
		<div data-testid="dashboard">
			<motion.section
				initial={{ opacity: 0 }}
				animate={{ opacity: 1 }}
				transition={{ duration: 0.5 }}
				aria-label="Latest renders"
			>
				{tiles.length > 0 ? (
					<ContactSheet tiles={tiles} apps={apps} />
				) : (
					!loading && (
						<div className="print flex aspect-[16/5] items-center justify-center text-sm text-muted">
							No renders yet. Run any demo and its output lands here.
						</div>
					)
				)}
			</motion.section>

			<section className="mt-10 grid gap-8 lg:grid-cols-[1fr_20rem]">
				<div>
					<h1 className="max-w-[18ch] text-4xl font-semibold leading-[1.05] tracking-tight sm:text-5xl">
						Every Craft app, run for real.
					</h1>
					<p className="mt-4 max-w-[62ch] text-[15px] leading-relaxed text-muted">
						Each picture above came out of an installed Craft CLI on this
						machine, with the engine version and every step recorded. Pick an
						app, run a demo, keep the files.
					</p>
					<div className="mt-6 flex flex-wrap gap-3">
						<Link
							to={
								tiles[0]
									? `/craft/${tiles[0].app}?demo=${tiles[0].demo}`
									: "/craft/solid"
							}
							data-testid="hero-cta"
							className="rounded-md bg-accent px-4 py-2 text-sm font-semibold text-zinc-950 hover:bg-amber-400"
						>
							Open the latest run
						</Link>
						<Link
							to="/flows"
							data-testid="flows-cta"
							className="rounded-md border border-line px-4 py-2 text-sm hover:border-zinc-500"
						>
							Chain apps in a flow
						</Link>
					</div>
					<p className="mt-5 flex flex-wrap gap-x-5 gap-y-1 text-xs text-muted">
						<span className="flex items-center gap-1.5">
							<span
								className={`h-1.5 w-1.5 rounded-full ${health ? "bg-emerald-400" : "bg-red-400"}`}
							/>
							{health
								? `${health.installed} of ${health.apps} apps installed`
								: "backend down"}
						</span>
						<span className="flex items-center gap-1.5">
							<span
								className={`h-1.5 w-1.5 rounded-full ${llmOk ? "bg-emerald-400" : "bg-zinc-600"}`}
							/>
							{llmOk
								? "local model available for AI steps"
								: "no local model: AI steps skip"}
						</span>
					</p>
					{failed && (
						<p className="mt-4 text-sm text-amber-300">
							The backend did not answer. Start it with start.bat, then{" "}
							<button
								type="button"
								className="underline"
								onClick={() => window.location.reload()}
							>
								reload
							</button>
							.
						</p>
					)}
					{missing.length > 0 && (
						<Link
							to="/onboarding"
							data-testid="onboarding-cta"
							className="mt-5 block rounded-md border border-red-500/70 bg-red-950/60 p-3 text-sm font-medium text-red-200"
						>
							{missing.length} Craft app(s) not installed (
							{missing.slice(0, 4).join(", ")}
							{missing.length > 4 ? "..." : ""}). Install them to clear the MOCK
							badges.
						</Link>
					)}
				</div>

				{fresh.length > 0 && (
					<aside
						data-testid="whats-new"
						className="lg:border-l lg:border-line lg:pl-6"
					>
						<h2 className="text-sm font-medium">New with the Oct 31 builds</h2>
						<ul className="mt-3 space-y-3">
							{fresh.map(({ app, demo }) => {
								const meta = appMeta(app.key);
								return (
									<li key={`${app.key}/${demo.id}`}>
										<Link
											to={`/craft/${app.key}?demo=${demo.id}`}
											className="group block text-sm"
										>
											<span className="flex items-center gap-1.5 text-xs text-muted">
												<meta.icon size={13} style={{ color: meta.hue }} />
												{app.name}
											</span>
											<span className="text-paper group-hover:text-accent">
												{demo.title.replace(/^Demo \d+: /, "")}
											</span>
										</Link>
									</li>
								);
							})}
						</ul>
					</aside>
				)}
			</section>

			<section className="mt-12 grid gap-x-10 gap-y-8 md:grid-cols-2">
				<div data-testid="dashboard-builds">
					<h2 className="mb-2 text-sm font-medium">
						Storytold ArtCraft{" "}
						<span className="text-muted">({core.length})</span>
					</h2>
					<div className="border-t border-line">
						{core.map((a) => (
							<AppRow key={a.key} a={a} />
						))}
					</div>
				</div>
				<div>
					<h2 className="mb-2 text-sm font-medium">
						Community members{" "}
						<span className="text-muted">({community.length})</span>
					</h2>
					<div className="border-t border-line">
						{community.map((a) => (
							<AppRow key={a.key} a={a} />
						))}
					</div>
					<p className="mt-3 max-w-[48ch] text-xs leading-relaxed text-muted">
						Third-party apps built to the Craft conventions. SolidCraft is by
						Tangency Labs and updates itself in place, so its version can move
						between runs.
					</p>
					<dl className="mt-8 grid grid-cols-2 gap-x-6 gap-y-3 sm:grid-cols-4 md:grid-cols-2">
						{kpis.map((k) => (
							<div
								key={k.label}
								data-testid={`kpi-${k.label.toLowerCase().replace(/\s+/g, "-")}`}
								className="flex flex-col-reverse"
							>
								<dt className="text-xs text-muted">{k.label}</dt>
								<dd className="text-xl font-semibold tabular-nums">
									{k.value}
								</dd>
							</div>
						))}
					</dl>
				</div>
			</section>
		</div>
	);
}
