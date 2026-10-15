import { useEffect } from "react";
import { useBackend } from "../store/backend";
import { useLlm } from "../store/llm";

export default function Settings() {
	const { providers, model, setModel, refresh } = useLlm();
	const { health, refresh: refreshBe } = useBackend();
	useEffect(() => {
		refresh();
		refreshBe();
	}, [refresh, refreshBe]);
	const ollama = providers.find((p) => p.id === "ollama");
	return (
		<div>
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
				<p>
					Ollama:{" "}
					{ollama
						? ollama.ok
							? `ok (${ollama.models?.length ?? 0} models)`
							: `down - ${ollama.error}`
						: "probing..."}
				</p>
			</div>
			<div className="mt-3">
				<label htmlFor="llm-model" className="text-sm">
					LLM model (DEMOCRAFT_MODEL default: gemma4:12b)
				</label>
				<input
					id="llm-model"
					data-testid="llm-model"
					value={model}
					onChange={(e) => setModel(e.target.value)}
					className="mt-1 block w-full rounded bg-slate-800 p-2 font-mono text-sm"
				/>
			</div>
		</div>
	);
}
