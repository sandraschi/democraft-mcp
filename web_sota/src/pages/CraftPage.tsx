import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { MockBadge } from "../components/AppLayout";
import { api, apiBase } from "../lib/api";
import { useBackend } from "../store/backend";

interface RunResult {
	success: boolean;
	message: string;
	ai_step?: {
		success: boolean;
		model?: string;
		text?: string;
		skipped?: boolean;
		ms?: number;
		reason?: string;
	};
	cli_steps?: {
		argv?: string[];
		returncode?: number;
		stdout?: string;
		stderr?: string;
		ms?: number;
		note?: string;
	}[];
	artifacts?: string[];
	all_cli_ok?: boolean;
	run_dir?: string;
}

export default function CraftPage() {
	const { app = "" } = useParams();
	const { apps } = useBackend();
	const craft = apps.find((a) => a.key === app);
	const [running, setRunning] = useState(false);
	const [result, setResult] = useState<RunResult | null>(null);
	const [toast, setToast] = useState("");
	const [topicPick, setTopicPick] = useState("");
	const [topicCustom, setTopicCustom] = useState("");
	const [selectedId, setSelectedId] = useState("");
	const [lastDemo, setLastDemo] = useState("");

	const demo = craft?.demos.find((d) => d.id === selectedId) ?? craft?.demos[0];

	async function run(demoId: string, topic: string) {
		setRunning(true);
		setToast("");
		setLastDemo(demoId);
		try {
			const r = await api<RunResult>("/api/demos/run", {
				method: "POST",
				body: JSON.stringify({ app, demo: demoId, topic }),
			});
			setResult(r);
			setToast(
				r.success
					? "Demo finished - see artifacts below."
					: `Demo reported: ${r.message}`,
			);
		} catch (e) {
			setToast(`Request failed: ${e}`);
		} finally {
			setRunning(false);
		}
	}

	if (!craft)
		return apps.length === 0 ? (
			<p>
				Loading backend registry - is the backend up on :11246?{" "}
				<Link to="/help" className="underline">
					Help
				</Link>
			</p>
		) : (
			<p>
				Unknown craft app.{" "}
				<Link to="/" className="underline">
					Dashboard
				</Link>
			</p>
		);

	return (
		<div data-testid="craft-page">
			<section
				data-testid="craft-hero"
				className="rounded border border-slate-800 bg-slate-900 p-6"
			>
				<p className="text-xs uppercase tracking-widest text-amber-400">
					Local alternative to {craft.clone_of}
				</p>
				<h1 className="mt-2 text-3xl font-bold">
					{craft.name} {!craft.installed && <MockBadge />}
				</h1>
				<p className="mt-3 max-w-3xl text-slate-200">
					{craft.description || craft.tagline}
				</p>
				<p className="mt-2 text-sm text-slate-400">{craft.tagline}</p>
				{craft.gaps.length > 0 && (
					<div className="mt-5">
						<p className="text-xs uppercase tracking-widest text-slate-400">
							Observed gaps - not a roadmap
						</p>
						<ul className="mt-2 flex flex-wrap gap-2">
							{craft.gaps.map((g) => (
								<li
									key={g}
									data-testid="gap-chip"
									className="rounded bg-slate-800 px-2 py-1 text-xs text-slate-300"
								>
									{g}
								</li>
							))}
						</ul>
					</div>
				)}
			</section>

			<div
				role="tablist"
				aria-label="Demos"
				className="mt-6 flex flex-wrap gap-2"
			>
				{craft.demos.map((d) => (
					<button
						key={d.id}
						type="button"
						role="tab"
						data-testid="demo-tab"
						aria-selected={d.id === demo?.id}
						onClick={() => {
							setSelectedId(d.id);
							setResult(null);
							setToast("");
						}}
						className={`rounded px-3 py-2 text-sm ${
							d.id === demo?.id
								? "bg-amber-500 font-semibold text-slate-950"
								: "bg-slate-800 text-slate-300"
						}`}
					>
						{d.title}
					</button>
				))}
			</div>

			{demo && (
				<div
					key={demo.id}
					className="mt-4 rounded border border-slate-800 bg-slate-900 p-4"
				>
					<h2 className="font-semibold">{demo.title}</h2>
					<p className="text-sm text-slate-300">
						{demo.blurb} (requires: {demo.requires})
					</p>
					{demo.topics && demo.topics.length > 0 && (
						<div className="mt-3 flex flex-col gap-2 text-sm">
							<label htmlFor={`topic-pick-${demo.id}`}>
								Topic - pick one or write your own below
							</label>
							<select
								id={`topic-pick-${demo.id}`}
								data-testid="topic-pick"
								value={topicPick}
								onChange={(e) => setTopicPick(e.target.value)}
								className="rounded bg-slate-800 p-2"
							>
								<option value="">Surprise me</option>
								{demo.topics.map((t) => (
									<option key={t} value={t}>
										{t}
									</option>
								))}
							</select>
							<input
								data-testid="topic-custom"
								value={topicCustom}
								onChange={(e) => setTopicCustom(e.target.value)}
								placeholder="Or type your own topic..."
								maxLength={200}
								className="rounded bg-slate-800 p-2"
							/>
						</div>
					)}
					<button
						type="button"
						data-testid="craft-run"
						onClick={() => run(demo.id, topicCustom.trim() || topicPick)}
						disabled={running || !craft.runnable}
						className="mt-3 rounded bg-amber-500 px-4 py-2 font-semibold text-slate-950 disabled:opacity-40"
					>
						{running
							? "Running..."
							: `Run ${demo.title.replace(/^Demo \d+: /, "")}`}
					</button>
					{!craft.runnable && (
						<p className="mt-2 text-sm text-amber-300">
							Install {craft.name} to run - see onboarding.
						</p>
					)}
					{craft.runnable && !craft.installed && (
						<p className="mt-2 text-sm text-amber-300">
							{craft.name} does not exist yet - this demo runs on a fallback
							engine.
						</p>
					)}
				</div>
			)}

			{toast && (
				<p
					data-testid="toast"
					className="mt-3 rounded bg-slate-800 p-2 text-sm"
				>
					{toast}
				</p>
			)}
			{result && (
				<div
					data-testid="craft-artifacts"
					className="mt-4 rounded border border-slate-800 bg-slate-900 p-4 text-sm"
				>
					<p>{result.message}</p>
					<p className="text-slate-300">
						AI step:{" "}
						{result.ai_step?.skipped
							? `skipped (${result.ai_step?.reason ?? result.ai_step?.model})`
							: `ok (${result.ai_step?.model}, ${result.ai_step?.ms}ms)`}
					</p>
					{result.ai_step?.text && (
						<pre className="mt-2 max-h-40 overflow-auto whitespace-pre-wrap text-xs text-slate-300">
							{result.ai_step.text}
						</pre>
					)}
					<p className="mt-2 font-semibold">
						Artifacts ({result.artifacts?.length ?? 0})
					</p>
					<ul className="list-disc pl-5 text-sm text-slate-300">
						{result.artifacts?.slice(0, 30).map((f) => (
							<li key={f} className="break-all">
								<a
									href={`${apiBase()}/api/artifacts/${app}/${lastDemo}/${f}`}
									target="_blank"
									rel="noreferrer"
									className="underline"
									title="Open - PNG/PDF open inline, documents download for their Craft app"
								>
									{f.split("/").pop()}
								</a>
							</li>
						))}
					</ul>
					<details className="mt-2">
						<summary className="cursor-pointer">
							CLI steps ({result.cli_steps?.length ?? 0})
						</summary>
						{result.cli_steps?.map((s) => (
							<pre
								key={`${(s.argv ?? []).join(" ")}-${s.ms}`}
								className="mt-1 max-h-40 overflow-auto text-xs text-slate-300"
							>
								$ {(s.argv ?? []).join(" ")} (rc={s.returncode}, {s.ms}ms)
								{s.note ? `\nnote: ${s.note}` : ""}
								{s.stderr ? `\nstderr: ${s.stderr.slice(-500)}` : ""}
							</pre>
						))}
					</details>
				</div>
			)}
		</div>
	);
}
