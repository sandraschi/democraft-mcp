import { useEffect } from "react";
import { useBackend } from "../store/backend";
import { useLlm } from "../store/llm";

export default function Settings() {
	const {
		providers,
		provider,
		model,
		models,
		gpu,
		probing,
		setProvider,
		setModel,
		refresh,
	} = useLlm();
	const { health, refresh: refreshBe } = useBackend();
	useEffect(() => {
		refresh();
		refreshBe();
	}, [refresh, refreshBe]);
	const anyOk = providers.some((p) => p.ok);
	return (
		<div data-testid="settings-page">
			<h1 className="text-2xl font-bold">Settings</h1>
			<div
				data-testid="backend-health"
				className="mt-3 rounded border border-slate-800 bg-slate-900 p-3 text-sm"
			>
				<p>
					Backend:{" "}
					{health
						? `${health.status} - ${health.installed}/${health.apps} wrappees installed`
						: "unreachable"}
				</p>
			</div>
			<h2 className="mt-4 font-semibold">Local LLM providers</h2>
			{probing && (
				<p className="text-sm text-slate-300">Probing providers...</p>
			)}
			{!probing && (
				<div className="mt-2 flex flex-col gap-2">
					{providers.map((p) => (
						<div
							key={p.id}
							data-testid={`llm-provider-card-${p.id}`}
							className="flex items-center gap-2 rounded border border-slate-800 bg-slate-900 p-2 text-sm"
						>
							<span
								className={`inline-block h-2 w-2 rounded-full ${p.ok ? "bg-emerald-400" : "bg-slate-600"}`}
							/>
							<span>{p.id}</span>
							<span className="text-slate-300">
								{p.ok ? "detected" : "not found"}
							</span>
						</div>
					))}
					{gpu && (
						<p className="text-sm text-slate-300">
							GPU present. No local LLM detected - install Ollama to use Chat
							and AI demo steps.
						</p>
					)}
					{!anyOk && (
						<p className="text-sm text-amber-300">
							No LLM detected. Chat and AI steps are disabled until a provider
							appears.
						</p>
					)}
				</div>
			)}
			<div className="mt-3 flex flex-col gap-2 text-sm">
				<label htmlFor="llm-provider-select">Provider</label>
				<select
					id="llm-provider-select"
					data-testid="llm-provider-select"
					value={provider}
					onChange={(e) => setProvider(e.target.value)}
					className="rounded bg-slate-800 p-2"
				>
					{providers.map((p) => (
						<option key={p.id} value={p.id}>
							{p.id}
							{p.ok ? "" : " (not detected)"}
						</option>
					))}
				</select>
				<label htmlFor="llm-model-select">Model</label>
				<select
					id="llm-model-select"
					data-testid="llm-model-select"
					value={model}
					onChange={(e) => setModel(e.target.value)}
					disabled={!anyOk}
					className="rounded bg-slate-800 p-2 disabled:opacity-40"
				>
					{[model, ...models.filter((m) => m !== model)].map((m) => (
						<option key={m} value={m}>
							{m}
						</option>
					))}
				</select>
			</div>
		</div>
	);
}
