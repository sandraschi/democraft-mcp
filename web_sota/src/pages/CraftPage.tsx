import { useEffect, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { MockBadge } from "../components/AppLayout";
import ArtifactGrid from "../components/ArtifactGrid";
import { api, apiBase } from "../lib/api";
import { appMeta, isNew } from "../lib/appMeta";
import { useBackend } from "../store/backend";

interface LatestRun {
	app: string;
	demo: string;
	run_id: string;
	started?: string;
	files: string[];
	latest: boolean;
}

interface FocusInfo {
	ok: boolean;
	reason?: string | null;
	exe?: string;
	window?: string;
	launched?: boolean;
	maximized?: boolean;
	foreground?: boolean;
	ms?: number;
}

interface RunResult {
	success: boolean;
	message: string;
	focus?: FocusInfo | null;
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

interface LiveEvent {
	id?: string;
	kind: string;
	focus?: FocusInfo;
	app?: string;
	demo?: string;
	status?: string;
	success?: boolean;
	skipped?: boolean;
	model?: string;
	ms?: number;
	argv?: string[];
	returncode?: number;
	artifacts?: string[];
	error?: string;
}

function focusLabel(focus?: FocusInfo): string {
	if (!focus) return "app window: unknown";
	if (!focus.ok)
		return `app window: unavailable (${focus.reason ?? "unknown"})`;
	const bits = [focus.window || "app", focus.launched ? "launched" : "raised"];
	if (focus.maximized) bits.push("maximised");
	if (!focus.foreground) bits.push("not foreground");
	return `app window: ${bits.join(", ")}`;
}

/** Run artifacts arrive as absolute paths; the artifact route wants run-relative ones. */
function relativeTo(files: string[], runDir?: string): string[] {
	const base = (runDir ?? "").replace(/\\/g, "/").replace(/\/$/, "");
	return files.map((f) => {
		const p = f.replace(/\\/g, "/");
		return base && p.startsWith(`${base}/`) ? p.slice(base.length + 1) : p;
	});
}

export default function CraftPage() {
	const { app = "" } = useParams();
	const [params] = useSearchParams();
	const { apps } = useBackend();
	const craft = apps.find((a) => a.key === app);
	const [running, setRunning] = useState(false);
	const [result, setResult] = useState<RunResult | null>(null);
	const [toast, setToast] = useState("");
	const [topicPick, setTopicPick] = useState("");
	const [topicCustom, setTopicCustom] = useState("");
	const [selectedId, setSelectedId] = useState(params.get("demo") ?? "");
	const [lastDemo, setLastDemo] = useState("");
	const [watch, setWatch] = useState(params.get("watch") === "1");
	const [events, setEvents] = useState<LiveEvent[]>([]);
	const [cursor, setCursor] = useState(0);
	const [playing, setPlaying] = useState(false);
	const [speed, setSpeed] = useState(1);
	const [finalResult, setFinalResult] = useState<RunResult | null>(null);
	const [jobId, setJobId] = useState("");
	const [latest, setLatest] = useState<LatestRun[]>([]);

	const demo = craft?.demos.find((d) => d.id === selectedId) ?? craft?.demos[0];
	const latestForDemo = latest.find((r) => r.demo === demo?.id);

	// biome-ignore lint/correctness/useExhaustiveDependencies: refetch after each finished run
	useEffect(() => {
		api<{ runs: LatestRun[] }>("/api/runs")
			.then((j) => setLatest(j.runs.filter((r) => r.app === app && r.latest)))
			.catch(() => setLatest([]));
	}, [app, result]);

	async function run(demoId: string, topic: string) {
		setRunning(true);
		setToast("");
		setEvents([]);
		setCursor(0);
		setPlaying(false);
		setFinalResult(null);
		setJobId("");
		setLastDemo(demoId);
		try {
			const target = craft?.demos.find((d) => d.id === demoId);
			const r = await api<RunResult>("/api/demos/run", {
				method: "POST",
				body: JSON.stringify({
					app,
					demo: demoId,
					topic,
					focus: Boolean(target?.live),
				}),
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

	async function runStream(demoId: string, topic: string) {
		setRunning(true);
		setToast("");
		setResult(null);
		setEvents([]);
		setCursor(0);
		setFinalResult(null);
		setJobId("");
		setPlaying(true);
		setLastDemo(demoId);
		try {
			const created = await api<{
				success: boolean;
				job?: { id: string };
				message?: string;
			}>("/api/jobs", {
				method: "POST",
				body: JSON.stringify({
					app,
					demo: demoId,
					topic,
					focus: Boolean(craft?.demos.find((d) => d.id === demoId)?.live),
				}),
			});
			if (!created.success || !created.job) {
				throw new Error(created.message ?? "job rejected");
			}
			setJobId(created.job.id);
			const response = await fetch(
				`${apiBase()}/api/jobs/${created.job.id}/events`,
			);
			if (!response.body) throw new Error("no stream body");
			const reader = response.body.getReader();
			const decoder = new TextDecoder();
			let buffer = "";
			for (;;) {
				const { done, value } = await reader.read();
				if (done) break;
				buffer += decoder.decode(value, { stream: true });
				let split = buffer.indexOf("\n\n");
				while (split >= 0) {
					const chunk = buffer.slice(0, split);
					buffer = buffer.slice(split + 2);
					const line = chunk.split("\n").find((l) => l.startsWith("data: "));
					if (line) {
						const event = JSON.parse(line.slice(6)) as LiveEvent & {
							result?: RunResult;
						};
						if (event.kind === "done") {
							if (event.result) {
								setFinalResult(event.result);
							} else if (event.status === "cancelled") {
								setToast("Job cancelled.");
								setPlaying(false);
							} else if (event.error) {
								setToast(`Job failed: ${event.error}`);
								setPlaying(false);
							}
						} else if (event.kind === "error") {
							setToast(`Stream error: ${event.error}`);
							setPlaying(false);
						} else {
							setEvents((prev) => [
								...prev,
								{ ...event, id: crypto.randomUUID() },
							]);
						}
					}
					split = buffer.indexOf("\n\n");
				}
			}
		} catch (e) {
			setToast(`Stream failed: ${e}`);
		} finally {
			setRunning(false);
		}
	}

	async function cancelJob() {
		if (!jobId) return;
		try {
			await api<{ success: boolean }>(`/api/jobs/${jobId}/cancel`, {
				method: "POST",
			});
			setToast("Cancel requested - stops after the current step.");
		} catch (e) {
			setToast(`Cancel failed: ${e}`);
		}
	}

	function playback() {
		if (cursor >= events.length) {
			setCursor(0);
			setResult(null);
		}
		setPlaying(true);
	}

	useEffect(() => {
		if (!playing) return;
		if (cursor >= events.length) {
			if (finalResult) {
				setResult(finalResult);
				setPlaying(false);
				setToast(
					finalResult.success
						? "Demo finished - see artifacts below."
						: `Demo reported: ${finalResult.message}`,
				);
			}
			return;
		}
		const timer = window.setTimeout(
			() => setCursor((c) => Math.min(c + 1, events.length)),
			1500 / speed,
		);
		return () => window.clearTimeout(timer);
	}, [playing, cursor, events.length, speed, finalResult]);

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

	const meta = appMeta(craft.key);
	return (
		<div data-testid="craft-page">
			<section
				data-testid="craft-hero"
				className="grid gap-6 border-b border-line pb-8 md:grid-cols-[1fr_16rem]"
			>
				<div>
					<p className="flex items-center gap-2 text-sm text-muted">
						<meta.icon size={16} style={{ color: meta.hue }} />
						For people who use {craft.clone_of}
					</p>
					<h1 className="mt-2 flex flex-wrap items-center gap-3 text-4xl font-semibold tracking-tight">
						{craft.name} {!craft.installed && <MockBadge />}
					</h1>
					<p className="mt-3 max-w-[64ch] text-[15px] leading-relaxed text-paper/90">
						{craft.description || craft.tagline}
					</p>
				</div>
				<dl
					className="grid grid-cols-2 content-start gap-x-4 gap-y-3 text-sm md:border-l md:border-line md:pl-6"
					style={{ borderLeftColor: meta.hue }}
				>
					<div className="flex flex-col-reverse">
						<dt className="text-xs text-muted">installed build</dt>
						<dd className="font-mono">{craft.version ?? "none"}</dd>
					</div>
					<div className="flex flex-col-reverse">
						<dt className="text-xs text-muted">made by</dt>
						<dd>{craft.maker ?? "Storytold"}</dd>
					</div>
					<div className="flex flex-col-reverse">
						<dt className="text-xs text-muted">family</dt>
						<dd>
							{craft.family === "community" ? "community" : "ArtCraft core"}
						</dd>
					</div>
					<div className="flex flex-col-reverse">
						<dt className="text-xs text-muted">accepted baseline</dt>
						<dd className={`font-mono ${craft.drift ? "text-amber-300" : ""}`}>
							{craft.baseline_version ?? "none yet"}
						</dd>
					</div>
				</dl>
				{craft.gaps.length > 0 && (
					<div className="md:col-span-2">
						<p className="text-xs text-muted">
							What we found missing (not a roadmap)
						</p>
						<ul className="mt-2 flex flex-wrap gap-2">
							{craft.gaps.map((g) => (
								<li
									key={g}
									data-testid="gap-chip"
									className="rounded-md border border-line px-2 py-1 text-xs text-muted"
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
						className={`rounded-md border px-3 py-1.5 text-sm transition-colors ${
							d.id === demo?.id
								? "border-accent bg-accent/10 text-paper"
								: "border-line text-muted hover:text-paper"
						}`}
					>
						{d.title.replace(/^Demo \d+: /, "")}
						{isNew(d.added) && (
							<span className="ml-2 rounded-md bg-accent/20 px-1 text-[10px] font-semibold text-accent">
								new
							</span>
						)}
					</button>
				))}
			</div>

			{demo && (
				<div
					key={demo.id}
					className="mt-5 rounded-lg border border-line bg-surface p-5"
				>
					<h2 className="text-lg font-medium">
						{demo.title.replace(/^Demo \d+: /, "")}
					</h2>
					<p className="mt-1 max-w-[72ch] text-sm leading-relaxed text-muted">
						{demo.blurb}
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
								className="rounded-md bg-raised p-2"
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
								className="rounded-md bg-raised p-2"
							/>
						</div>
					)}
					<label className="mt-3 flex items-center gap-2 text-sm text-muted">
						<input
							type="checkbox"
							data-testid="watch-build"
							checked={watch}
							onChange={(e) => setWatch(e.target.checked)}
						/>
						Watch it build (stream each step)
					</label>
					<button
						type="button"
						data-testid="craft-run"
						onClick={() =>
							(watch ? runStream : run)(
								demo.id,
								topicCustom.trim() || topicPick,
							)
						}
						disabled={running || !craft.runnable}
						className="mt-4 rounded-md bg-accent px-4 py-2 text-sm font-semibold text-zinc-950 hover:bg-amber-400 disabled:opacity-40"
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

			{events.length > 0 && (
				<div
					data-testid="live-steps"
					className="mt-4 rounded-md border border-amber-900/50 bg-surface p-4 text-xs"
				>
					<div className="flex flex-wrap items-center justify-between gap-2">
						<p className="text-xs text-amber-400">
							{playing
								? "Building"
								: cursor >= events.length
									? "Finished"
									: "Paused"}
						</p>
						<div className="flex flex-wrap items-center gap-2">
							<button
								type="button"
								data-testid="playback-play"
								onClick={playback}
								className="rounded-md bg-accent px-2 py-1 font-semibold text-zinc-950"
							>
								Play
							</button>
							<button
								type="button"
								data-testid="playback-pause"
								onClick={() => setPlaying(false)}
								className="rounded-md bg-raised px-2 py-1"
							>
								Pause
							</button>
							<button
								type="button"
								data-testid="playback-stop"
								onClick={() => {
									setPlaying(false);
									setCursor(0);
									setResult(null);
								}}
								className="rounded-md bg-raised px-2 py-1"
							>
								Stop
							</button>
							<button
								type="button"
								data-testid="playback-rewind"
								onClick={() => {
									setResult(null);
									setCursor((c) => Math.max(0, c - 1));
								}}
								className="rounded-md bg-raised px-2 py-1"
							>
								Rewind
							</button>
							<button
								type="button"
								data-testid="playback-cancel"
								onClick={cancelJob}
								disabled={!jobId}
								className="rounded-md bg-raised px-2 py-1 disabled:opacity-40"
							>
								Cancel job
							</button>
							<label className="flex items-center gap-1">
								Speed
								<input
									type="range"
									data-testid="playback-speed"
									min={0.25}
									max={4}
									step={0.25}
									value={speed}
									onChange={(e) => setSpeed(Number(e.target.value))}
								/>
							</label>
							<span>{speed}x</span>
							<span className="text-muted">
								{cursor}/{events.length}
							</span>
						</div>
					</div>
					<ul className="mt-2 space-y-1 font-mono text-muted">
						{events.slice(0, cursor).map((e) => (
							<li key={e.id} className="break-all">
								{e.kind === "ai"
									? `AI ${e.skipped ? "skipped" : "ok"} (${e.model}, ${e.ms}ms)`
									: e.kind === "queued"
										? "queued"
										: e.kind === "start"
											? `start ${e.app}/${e.demo}`
											: e.kind === "focus"
												? focusLabel(e.focus)
												: `$ ${(e.argv ?? []).join(" ").slice(0, 120)} (rc=${e.returncode}, ${e.ms}ms)`}
								{(e.artifacts ?? []).slice(-3).map((a) => (
									<a
										key={a}
										href={`${apiBase()}/api/artifacts/${app}/${lastDemo}/${a}`}
										target="_blank"
										rel="noreferrer"
										className="ml-2 underline"
									>
										{a.split("/").pop()}
									</a>
								))}
							</li>
						))}
					</ul>
				</div>
			)}

			{!result &&
				!events.length &&
				latestForDemo &&
				latestForDemo.files.length > 0 && (
					<section data-testid="latest-output" className="mt-8">
						<h2 className="text-sm font-medium">
							Last run
							{latestForDemo.started && (
								<span className="ml-2 font-normal text-muted">
									{new Date(latestForDemo.started).toLocaleString()}
								</span>
							)}
						</h2>
						<div className="mt-3">
							<ArtifactGrid
								files={latestForDemo.files}
								urlFor={(f) =>
									`${apiBase()}/api/artifacts/${app}/${latestForDemo.demo}/${f}`
								}
							/>
						</div>
					</section>
				)}

			{toast && (
				<p
					data-testid="toast"
					className="mt-3 rounded-md bg-raised p-2 text-sm"
				>
					{toast}
				</p>
			)}
			{result && (
				<div
					data-testid="craft-artifacts"
					className="mt-4 rounded-md border border-line bg-surface p-4 text-sm"
				>
					<p>{result.message}</p>
					{result.focus && (
						<p data-testid="result-focus" className="text-muted">
							{focusLabel(result.focus)}
						</p>
					)}
					<p className="text-muted">
						AI step:{" "}
						{result.ai_step?.skipped
							? `skipped (${result.ai_step?.reason ?? result.ai_step?.model})`
							: `ok (${result.ai_step?.model}, ${result.ai_step?.ms}ms)`}
					</p>
					{result.ai_step?.text && (
						<pre className="mt-2 max-h-40 overflow-auto whitespace-pre-wrap text-xs text-muted">
							{result.ai_step.text}
						</pre>
					)}
					<p className="mt-3 font-medium">
						Artifacts ({result.artifacts?.length ?? 0})
					</p>
					<div className="mt-3">
						<ArtifactGrid
							files={relativeTo(result.artifacts ?? [], result.run_dir)}
							urlFor={(f) =>
								`${apiBase()}/api/artifacts/${app}/${lastDemo}/${f}`
							}
						/>
					</div>
					<details className="mt-2">
						<summary className="cursor-pointer">
							CLI steps ({result.cli_steps?.length ?? 0})
						</summary>
						{result.cli_steps?.map((s) => (
							<pre
								key={`${(s.argv ?? []).join(" ")}-${s.ms}`}
								className="mt-1 max-h-40 overflow-auto text-xs text-muted"
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
