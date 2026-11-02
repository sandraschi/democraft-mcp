import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { MockBadge } from "../components/AppLayout";
import { todayLocal } from "../lib/api";
import { useBackend } from "../store/backend";

export default function Apps() {
	const { apps } = useBackend();
	const [q, setQ] = useState("");
	const today = todayLocal();

	const filtered = useMemo(() => {
		const needle = q.trim().toLowerCase();
		if (!needle) return apps;
		return apps.filter((a) =>
			[a.name, a.tagline, a.clone_of, a.description]
				.join(" ")
				.toLowerCase()
				.includes(needle),
		);
	}, [apps, q]);

	const installed = apps.filter((a) => a.installed).length;
	const fresh = apps.filter((a) => (a.modified ?? "").startsWith(today)).length;
	const drift = apps.filter((a) => a.drift).length;

	return (
		<div>
			<h1 className="text-3xl font-bold">Craft apps</h1>
			<p className="mt-2 text-muted">
				Thirteen native Rust apps, one per craft. Versions below are read from
				the CLI actually installed on this machine - not from GitHub, not from a
				release feed. Upstream ships new builds several times a week, so the
				table is a snapshot: treat the version as evidence, never as a pin.
			</p>

			<div className="mt-4 grid grid-cols-2 gap-3 md:grid-cols-4">
				<div className="rounded-md border border-line bg-surface p-3">
					<p className="text-2xl font-bold">
						{installed}/{apps.length}
					</p>
					<p className="text-sm text-muted">installed</p>
				</div>
				<div className="rounded-md border border-line bg-surface p-3">
					<p className="text-2xl font-bold">{fresh}</p>
					<p className="text-sm text-muted">built today</p>
				</div>
				<div className="rounded-md border border-line bg-surface p-3">
					<p className="text-2xl font-bold">{drift}</p>
					<p className="text-sm text-muted">drift vs baseline</p>
				</div>
				<div className="rounded-md border border-line bg-surface p-3">
					<p className="text-2xl font-bold">
						{apps.reduce((n, a) => n + a.demos.length, 0)}
					</p>
					<p className="text-sm text-muted">runnable demos</p>
				</div>
			</div>

			<div className="mt-4 flex items-center gap-2">
				<input
					value={q}
					onChange={(e) => setQ(e.target.value)}
					placeholder="Filter apps, taglines, targets"
					data-testid="apps-filter"
					className="w-full max-w-sm rounded-md border border-line bg-surface px-3 py-1.5 text-sm"
				/>
				<span className="text-sm text-muted">
					{filtered.length} of {apps.length}
				</span>
			</div>

			<div className="mt-4 overflow-x-auto rounded-md border border-line">
				<table data-testid="apps-table" className="w-full text-left text-sm">
					<thead className="bg-surface text-xs uppercase tracking-wider text-muted">
						<tr>
							<th className="px-3 py-2 font-medium">App</th>
							<th className="px-3 py-2 font-medium">Version</th>
							<th className="px-3 py-2 font-medium">Built</th>
							<th className="px-3 py-2 font-medium">Status</th>
							<th className="px-3 py-2 font-medium">Demos</th>
						</tr>
					</thead>
					<tbody>
						{filtered.map((a) => {
							const isToday = (a.modified ?? "").startsWith(today);
							return (
								<tr
									key={a.key}
									data-testid={`app-row-${a.key}`}
									className="border-t border-line align-top hover:bg-slate-900/60"
								>
									<td className="px-3 py-2">
										<div className="flex flex-wrap items-center gap-2">
											<Link
												to={`/craft/${a.key}`}
												className="font-semibold hover:text-amber-400"
											>
												{a.name}
											</Link>
											{a.clone_of && (
												<span className="rounded-md bg-raised px-1.5 py-0.5 text-xs text-muted">
													vs {a.clone_of}
												</span>
											)}
											{a.drift && (
												<span
													data-testid={`app-drift-${a.key}`}
													className="rounded-md bg-amber-500/20 px-1.5 py-0.5 text-xs font-semibold text-amber-300"
												>
													drift
												</span>
											)}
										</div>
										<p className="text-muted">{a.tagline}</p>
										<p
											className="mt-0.5 max-w-2xl text-xs text-muted"
											title={a.description}
										>
											{a.description}
										</p>
										{a.gaps.length > 0 && (
											<p className="mt-1 text-xs text-slate-500">
												{a.gaps.length} known gap
												{a.gaps.length === 1 ? "" : "s"} - {a.gaps[0]}
											</p>
										)}
									</td>
									<td className="whitespace-nowrap px-3 py-2 font-mono">
										{a.version ?? "-"}
										{a.baseline_version && a.baseline_version !== a.version && (
											<span className="ml-1 text-xs text-amber-300">
												(base {a.baseline_version})
											</span>
										)}
									</td>
									<td className="whitespace-nowrap px-3 py-2 font-mono text-muted">
										{a.modified ? (
											<>
												{a.modified.slice(0, 10)}
												<span
													className={
														isToday
															? "ml-1 text-amber-300"
															: "ml-1 text-slate-500"
													}
												>
													{isToday ? "today" : a.modified.slice(11, 16)}
												</span>
											</>
										) : (
											"-"
										)}
									</td>
									<td className="whitespace-nowrap px-3 py-2">
										{a.installed ? (
											<span className="text-emerald-400">installed</span>
										) : (
											<span className="flex items-center gap-1 text-muted">
												missing <MockBadge />
											</span>
										)}
									</td>
									<td className="px-3 py-2 text-muted">{a.demos.length}</td>
								</tr>
							);
						})}
						{filtered.length === 0 && (
							<tr>
								<td colSpan={5} className="px-3 py-6 text-center text-muted">
									No app matches "{q}".
								</td>
							</tr>
						)}
					</tbody>
				</table>
			</div>

			<p className="mt-3 text-sm text-muted">
				Built = the CLI file's own timestamp, so a launcher update shows here
				before GitHub publishes the tag. Drift compares the installed build
				against the last accepted baseline; accepting it is deliberate (
				<code>craft_commands(force=True)</code>) so a silent engine upgrade
				never looks like a green run.
			</p>
		</div>
	);
}
