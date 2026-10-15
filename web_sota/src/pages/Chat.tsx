import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { useLlm } from "../store/llm";

interface Msg {
	role: string;
	text: string;
}

const PERSONALITIES = [
	{
		id: "operator",
		label: "Operator",
		system: "Answer tersely with exact commands and paths.",
	},
	{
		id: "explainer",
		label: "Explainer",
		system: "Explain like the reader is smart but new to this repo.",
	},
	{
		id: "debugger",
		label: "Debugger",
		system: "Focus on the likeliest failure and how to prove it.",
	},
	{ id: "custom", label: "Custom", system: "" },
];

const EXAMPLE_PROMPTS = [
	"Which wrappees are installed?",
	"Run the CAD house-plan demo and summarize the artifacts.",
	"What does the film EDL contain?",
	"Compare the two pelican pipelines.",
	"Why did a demo step fail and what fixes it?",
	"Draft a CURShapes tatami script for later.",
];

const HIST_KEY = "democraft-chat";
const HIST_CAP = 100;

export default function Chat() {
	const { model, setModel, chat, refresh, providers, models } = useLlm();
	const [input, setInput] = useState("");
	const [personality, setPersonality] = useState("operator");
	const [customSystem, setCustomSystem] = useState("");
	const [skills, setSkills] = useState<{ name: string; preview: string }[]>([]);
	const [skill, setSkill] = useState("");
	const [hist, setHist] = useState<Msg[]>(() => {
		try {
			return JSON.parse(localStorage.getItem(HIST_KEY) ?? "[]");
		} catch {
			return [];
		}
	});
	const [busy, setBusy] = useState(false);
	useEffect(() => {
		refresh();
		api<{ skills: { name: string; preview: string }[] }>("/api/skills")
			.then((j) => setSkills(j.skills))
			.catch(() => {});
	}, [refresh]);
	useEffect(() => {
		try {
			localStorage.setItem(HIST_KEY, JSON.stringify(hist.slice(-HIST_CAP)));
		} catch {
			/* storage full or private mode */
		}
	}, [hist]);
	const llmOk = providers.some((p) => p.ok);

	function composed(text: string): string {
		const parts: string[] = [];
		const pers = PERSONALITIES.find((p) => p.id === personality);
		const sys = personality === "custom" ? customSystem : (pers?.system ?? "");
		if (sys) parts.push(`[style: ${sys}]`);
		const sk = skills.find((s) => s.name === skill);
		if (sk) parts.push(`[skill ${sk.name}: ${sk.preview.slice(0, 800)}]`);
		parts.push(text);
		return parts.join("\n");
	}

	async function sendText(text: string) {
		if (!text.trim() || busy || !llmOk) return;
		setBusy(true);
		const h = [...hist, { role: "you", text }];
		setHist(h);
		try {
			const r = await chat(composed(text));
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

	function send() {
		sendText(input);
		setInput("");
	}

	function exportTxt() {
		const blob = new Blob(
			[hist.map((m) => `${m.role}: ${m.text}`).join("\n\n")],
			{ type: "text/plain" },
		);
		const a = document.createElement("a");
		a.href = URL.createObjectURL(blob);
		a.download = "democraft-chat.txt";
		a.click();
		URL.revokeObjectURL(a.href);
	}

	function clear() {
		setHist([]);
		try {
			localStorage.removeItem(HIST_KEY);
		} catch {
			/* ignore */
		}
	}

	return (
		<div data-testid="chat-page">
			<h1 className="text-2xl font-bold">Chat</h1>
			<div
				data-testid="chat-controls"
				className="mt-2 flex flex-wrap items-center gap-2 text-sm"
			>
				<span
					className={`inline-block h-2 w-2 rounded-full ${llmOk ? "bg-emerald-400" : "bg-red-400"}`}
				/>
				<label htmlFor="personality-select">Personality</label>
				<select
					id="personality-select"
					data-testid="personality-select"
					value={personality}
					onChange={(e) => setPersonality(e.target.value)}
					className="rounded bg-slate-800 p-1"
				>
					{PERSONALITIES.map((p) => (
						<option key={p.id} value={p.id}>
							{p.label}
						</option>
					))}
				</select>
				{personality === "custom" && (
					<input
						value={customSystem}
						onChange={(e) => setCustomSystem(e.target.value)}
						placeholder="Custom style..."
						className="rounded bg-slate-800 p-1"
					/>
				)}
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
				<label htmlFor="chat-skill">Skill</label>
				<select
					id="chat-skill"
					data-testid="chat-skill"
					value={skill}
					onChange={(e) => setSkill(e.target.value)}
					className="rounded bg-slate-800 p-1"
				>
					<option value="">none</option>
					{skills.map((s) => (
						<option key={s.name} value={s.name}>
							{s.name}
						</option>
					))}
				</select>
				<button
					type="button"
					data-testid="chat-export"
					onClick={exportTxt}
					disabled={!hist.length}
					className="rounded border border-slate-700 px-2 py-1 disabled:opacity-40"
				>
					Export
				</button>
				<button
					type="button"
					data-testid="chat-clear"
					onClick={clear}
					disabled={!hist.length}
					className="rounded border border-slate-700 px-2 py-1 disabled:opacity-40"
				>
					Clear
				</button>
			</div>
			{!llmOk && (
				<p className="mt-2 text-sm text-amber-300">
					No LLM detected - chat is disabled until a provider appears (see
					Settings).
				</p>
			)}
			<div data-testid="example-prompts" className="mt-2 flex flex-wrap gap-2">
				{EXAMPLE_PROMPTS.map((p) => (
					<button
						key={p}
						type="button"
						onClick={() => sendText(p)}
						disabled={busy || !llmOk}
						className="rounded border border-slate-700 px-2 py-1 text-sm disabled:opacity-40"
					>
						{p}
					</button>
				))}
			</div>
			<div
				data-testid="chat-messages"
				className="mt-3 flex max-h-[50vh] flex-col gap-2 overflow-auto"
			>
				{!hist.length && (
					<p className="text-sm text-slate-300">
						Ask about any demo - e.g. which wrappees are installed, or what the
						film EDL contains.
					</p>
				)}
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
					disabled={!llmOk}
					className="flex-1 rounded bg-slate-800 p-2 disabled:opacity-40"
				/>
				<button
					type="button"
					data-testid="chat-send"
					onClick={send}
					disabled={busy || !llmOk}
					className="rounded bg-amber-500 px-4 py-2 font-semibold text-slate-950 disabled:opacity-40"
				>
					Send
				</button>
			</div>
		</div>
	);
}
