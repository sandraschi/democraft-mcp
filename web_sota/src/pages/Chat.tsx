import { useEffect, useState } from "react";
import { useLlm } from "../store/llm";

interface Msg {
	role: string;
	text: string;
}

export default function Chat() {
	const { model, setModel, chat, refresh, providers } = useLlm();
	const [input, setInput] = useState("");
	const [hist, setHist] = useState<Msg[]>(() => {
		try {
			return JSON.parse(localStorage.getItem("democraft-chat") ?? "[]");
		} catch {
			return [];
		}
	});
	const [busy, setBusy] = useState(false);
	useEffect(() => {
		refresh();
	}, [refresh]);
	useEffect(() => {
		localStorage.setItem("democraft-chat", JSON.stringify(hist.slice(-50)));
	}, [hist]);
	const models = providers.find((p) => p.id === "ollama")?.models ?? [];

	async function send() {
		if (!input.trim() || busy) return;
		setBusy(true);
		const h = [...hist, { role: "you", text: input }];
		setHist(h);
		setInput("");
		try {
			const r = await chat(h[h.length - 1].text);
			setHist([
				...h,
				{
					role: "democraft",
					text: r.skipped
						? `(model unavailable: ${r.error ?? r.model})`
						: (r.text ?? ""),
				},
			]);
		} catch (e) {
			setHist([...h, { role: "democraft", text: `chat failed: ${e}` }]);
		} finally {
			setBusy(false);
		}
	}

	return (
		<div>
			<h1 className="text-2xl font-bold">Chat</h1>
			<div className="mt-2 flex items-center gap-2 text-sm">
				<label htmlFor="chat-model">Model</label>
				<select
					id="chat-model"
					data-testid="chat-model"
					value={model}
					onChange={(e) => setModel(e.target.value)}
					className="rounded bg-slate-800 p-1"
				>
					{[model, ...models.filter((m) => m !== model)].map((m) => (
						<option key={m} value={m}>
							{m}
						</option>
					))}
				</select>
			</div>
			<div className="mt-3 flex max-h-[50vh] flex-col gap-2 overflow-auto">
				{hist.map((m) => (
					<p
						key={`${m.role}-${m.text.slice(0, 32)}`}
						className={`rounded p-2 text-sm ${m.role === "you" ? "bg-slate-800" : "bg-slate-900"}`}
					>
						<b>{m.role}:</b> {m.text}
					</p>
				))}
			</div>
			<div className="mt-3 flex gap-2">
				<input
					data-testid="chat-input"
					value={input}
					onChange={(e) => setInput(e.target.value)}
					onKeyDown={(e) => e.key === "Enter" && send()}
					placeholder="Ask about a demo..."
					className="flex-1 rounded bg-slate-800 p-2"
				/>
				<button
					type="button"
					data-testid="chat-send"
					onClick={send}
					disabled={busy}
					className="rounded bg-amber-500 px-4 py-2 font-semibold text-slate-950 disabled:opacity-40"
				>
					Send
				</button>
			</div>
		</div>
	);
}
