import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api, type Flow, type FlowStep } from "../lib/api";
import { useBackend } from "../store/backend";

const EMPTY: Flow = {
	id: "",
	name: "",
	description: "",
	status: "ready",
	blocked_reason: "",
	steps: [],
};

const SLUG = /^[a-z0-9][a-z0-9-]{1,48}$/;

export default function FlowEditor() {
	const { id } = useParams();
	const editing = Boolean(id && id !== "new");
	const navigate = useNavigate();
	const { apps } = useBackend();
	const [flow, setFlow] = useState<Flow>(EMPTY);
	const [toast, setToast] = useState("");
	const [busy, setBusy] = useState(false);

	useEffect(() => {
		if (!editing || !id) return;
		api<{ flow: Flow }>(`/api/flows/${id}`)
			.then((j) =>
				setFlow({
					...j.flow,
					steps: j.flow.steps.map((step) => ({
						...step,
						_key: crypto.randomUUID(),
					})),
				}),
			)
			.catch(() => setToast("Flow not found."));
	}, [editing, id]);

	function demosFor(appKey: string) {
		return apps.find((a) => a.key === appKey)?.demos ?? [];
	}

	function addStep() {
		const app = apps[0];
		if (!app) return;
		const demo = app.demos[0]?.id ?? "";
		setFlow((f) => ({
			...f,
			steps: [
				...f.steps,
				{ app: app.key, demo, note: "", _key: crypto.randomUUID() },
			],
		}));
	}

	function updateStep(index: number, patch: Partial<FlowStep>) {
		setFlow((f) => ({
			...f,
			steps: f.steps.map((s, i) => (i === index ? { ...s, ...patch } : s)),
		}));
	}

	function changeApp(index: number, appKey: string) {
		const demo = demosFor(appKey)[0]?.id ?? "";
		updateStep(index, { app: appKey, demo });
	}

	function move(index: number, delta: number) {
		const target = index + delta;
		setFlow((f) => {
			if (target < 0 || target >= f.steps.length) return f;
			const steps = [...f.steps];
			[steps[index], steps[target]] = [steps[target], steps[index]];
			return { ...f, steps };
		});
	}

	async function save() {
		setToast("");
		if (!SLUG.test(flow.id)) {
			setToast("Id must be 2-49 chars: lowercase letters, digits, hyphens.");
			return;
		}
		if (!flow.name.trim()) {
			setToast("Name is required.");
			return;
		}
		if (!flow.steps.length) {
			setToast("Add at least one step.");
			return;
		}
		setBusy(true);
		try {
			const method = editing ? "PUT" : "POST";
			const path = editing ? `/api/flows/${flow.id}` : "/api/flows";
			const j = await api<{ success: boolean; flow?: Flow; message?: string }>(
				path,
				{
					method,
					body: JSON.stringify({
						...flow,
						steps: flow.steps.map((step) => ({
							app: step.app,
							demo: step.demo,
							note: step.note ?? "",
							topic: step.topic ?? "",
						})),
					}),
				},
			);
			if (!j.success || !j.flow) throw new Error(j.message ?? "save rejected");
			navigate(`/flows/${j.flow.id}`);
		} catch (e) {
			setToast(`${e}`);
		} finally {
			setBusy(false);
		}
	}

	async function remove() {
		if (!editing || !window.confirm(`Delete flow "${flow.name}"?`)) return;
		await api(`/api/flows/${flow.id}`, { method: "DELETE" });
		navigate("/flows");
	}

	return (
		<div data-testid="flow-editor">
			<Link
				to={editing ? `/flows/${flow.id}` : "/flows"}
				className="text-xs underline text-slate-400"
			>
				{editing ? "Back to flow" : "Flows"}
			</Link>
			<h1 className="mt-1 text-2xl font-bold">
				{editing ? "Edit flow" : "New flow"}
			</h1>

			<div className="mt-4 grid gap-3 md:grid-cols-2">
				<label className="text-sm">
					Id
					<input
						value={flow.id}
						disabled={editing}
						onChange={(e) => setFlow({ ...flow, id: e.target.value })}
						placeholder="cover-factory"
						className="mt-1 w-full rounded bg-slate-800 p-2 disabled:opacity-50"
					/>
				</label>
				<label className="text-sm">
					Name
					<input
						value={flow.name}
						onChange={(e) => setFlow({ ...flow, name: e.target.value })}
						className="mt-1 w-full rounded bg-slate-800 p-2"
					/>
				</label>
				<label className="text-sm md:col-span-2">
					Description
					<input
						value={flow.description}
						onChange={(e) => setFlow({ ...flow, description: e.target.value })}
						className="mt-1 w-full rounded bg-slate-800 p-2"
					/>
				</label>
				<label className="text-sm">
					Status
					<select
						value={flow.status}
						onChange={(e) => setFlow({ ...flow, status: e.target.value })}
						className="mt-1 w-full rounded bg-slate-800 p-2"
					>
						<option value="ready">ready</option>
						<option value="exploratory">exploratory</option>
						<option value="blocked">blocked</option>
					</select>
				</label>
				{flow.status === "blocked" && (
					<label className="text-sm">
						Blocked reason
						<input
							value={flow.blocked_reason}
							onChange={(e) =>
								setFlow({ ...flow, blocked_reason: e.target.value })
							}
							className="mt-1 w-full rounded bg-slate-800 p-2"
						/>
					</label>
				)}
			</div>

			<div className="mt-5 flex items-center justify-between">
				<h2 className="font-semibold">Steps</h2>
				<button
					type="button"
					onClick={addStep}
					className="rounded bg-slate-800 px-3 py-1 text-sm"
				>
					Add step
				</button>
			</div>

			<div className="mt-2 space-y-2">
				{flow.steps.map((step, index) => (
					<div
						key={step._key ?? `${step.app}-${step.demo}`}
						className="grid gap-2 rounded border border-slate-800 bg-slate-900 p-3 md:grid-cols-[2rem_1fr_1fr_2fr_auto]"
					>
						<span className="text-slate-400">{index + 1}</span>
						<select
							value={step.app}
							onChange={(e) => changeApp(index, e.target.value)}
							className="rounded bg-slate-800 p-2 text-sm"
						>
							{apps.map((a) => (
								<option key={a.key} value={a.key}>
									{a.key}
								</option>
							))}
						</select>
						<select
							value={step.demo}
							onChange={(e) => updateStep(index, { demo: e.target.value })}
							className="rounded bg-slate-800 p-2 text-sm"
						>
							{demosFor(step.app).map((d) => (
								<option key={d.id} value={d.id}>
									{d.id}
								</option>
							))}
						</select>
						<input
							value={step.note ?? ""}
							placeholder="note"
							onChange={(e) => updateStep(index, { note: e.target.value })}
							className="rounded bg-slate-800 p-2 text-sm"
						/>
						<div className="flex gap-1 text-xs">
							<button
								type="button"
								onClick={() => move(index, -1)}
								className="rounded bg-slate-800 px-2"
							>
								Up
							</button>
							<button
								type="button"
								onClick={() => move(index, 1)}
								className="rounded bg-slate-800 px-2"
							>
								Down
							</button>
							<button
								type="button"
								onClick={() =>
									setFlow((f) => ({
										...f,
										steps: f.steps.filter((_, i) => i !== index),
									}))
								}
								className="rounded bg-slate-800 px-2 text-red-300"
							>
								Remove
							</button>
						</div>
					</div>
				))}
			</div>

			{toast && <p className="mt-3 text-sm text-amber-300">{toast}</p>}

			<div className="mt-4 flex gap-2">
				<button
					type="button"
					onClick={save}
					disabled={busy}
					className="rounded bg-amber-500 px-4 py-2 text-sm font-semibold text-slate-950 disabled:opacity-40"
				>
					{busy ? "Saving..." : "Save"}
				</button>
				{editing && (
					<button
						type="button"
						onClick={remove}
						className="rounded bg-slate-800 px-4 py-2 text-sm text-red-300"
					>
						Delete
					</button>
				)}
			</div>
		</div>
	);
}
