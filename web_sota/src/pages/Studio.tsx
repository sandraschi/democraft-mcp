import { useEffect, useRef, useState } from "react";

const SAMPLE = [
	"Month,Revenue,Cost",
	"Jan,120,80",
	"Feb,145,88",
	"Mar,160,95",
	"Apr,152,91",
	"May,178,104",
	"Jun,195,110",
].join("\n");

interface BridgeMessage {
	type?: string;
	name?: string;
	bytes?: ArrayBuffer;
	dirty?: boolean;
	error?: string;
	version?: string;
}

export default function Studio() {
	const frame = useRef<HTMLIFrameElement>(null);
	const [status, setStatus] = useState("loading the GridCraft web build...");
	const [dirty, setDirty] = useState(false);
	const [lastSave, setLastSave] = useState("");
	const origin = window.location.origin;

	function post(message: Record<string, unknown>) {
		frame.current?.contentWindow?.postMessage(message, origin);
	}

	function sendSample() {
		const bytes = new TextEncoder().encode(SAMPLE).buffer;
		post({ type: "gridcraft:open", name: "studio-sample.csv", bytes });
		setStatus("handed studio-sample.csv to GridCraft");
	}

	useEffect(() => {
		function onMessage(event: MessageEvent) {
			if (event.origin !== origin) return;
			if (frame.current && event.source !== frame.current.contentWindow) return;
			const data = event.data as BridgeMessage;
			switch (data?.type) {
				case "gridcraft:ready":
					setStatus(`GridCraft ${data.version ?? ""} ready - sending sample`);
					sendSample();
					break;
				case "gridcraft:save": {
					const name = data.name ?? "gridcraft-save.xlsx";
					if (data.bytes) {
						const url = URL.createObjectURL(new Blob([data.bytes]));
						const link = document.createElement("a");
						link.href = url;
						link.download = name;
						link.click();
						URL.revokeObjectURL(url);
						setLastSave(`${name} (${data.bytes.byteLength} bytes)`);
						setStatus("saved - handed to the parent page");
					}
					break;
				}
				case "gridcraft:dirty":
					setDirty(Boolean(data.dirty));
					break;
				case "gridcraft:failed":
					setStatus(`GridCraft failed to start: ${data.error}`);
					break;
				default:
					break;
			}
		}
		window.addEventListener("message", onMessage);
		return () => window.removeEventListener("message", onMessage);
	});

	return (
		<div data-testid="studio-page">
			<div className="flex flex-wrap items-start justify-between gap-3">
				<div>
					<h1 className="text-2xl font-bold">Studio</h1>
					<p className="mt-1 max-w-3xl text-sm text-slate-400">
						GridCraft's web build embedded in this page through the same-origin{" "}
						<code>?host=parent</code> bridge. The host hands it a CSV and
						receives whatever it saves. No control channel, no second window, no
						MCP - the sheet is a pane here.
					</p>
				</div>
				<div className="flex gap-2 text-sm">
					<button
						type="button"
						onClick={sendSample}
						className="rounded bg-amber-500 px-4 py-2 font-semibold text-slate-950"
					>
						Send sample CSV
					</button>
					<button
						type="button"
						onClick={() => {
							frame.current?.contentWindow?.location.reload();
						}}
						className="rounded bg-slate-800 px-4 py-2"
					>
						Reload sheet
					</button>
				</div>
			</div>

			<div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-slate-300">
				<span>{status}</span>
				{dirty && (
					<span className="rounded bg-amber-500/20 px-2 py-0.5 text-amber-300">
						unsaved changes
					</span>
				)}
				{lastSave && (
					<span className="text-slate-400">last save: {lastSave}</span>
				)}
			</div>

			<iframe
				ref={frame}
				title="GridCraft embedded"
				data-testid="studio-frame"
				src="/gridcraft-web/index.html?host=parent&author=Sandra"
				className="mt-3 h-[72vh] w-full rounded border border-slate-800 bg-slate-950"
			/>

			<p className="mt-2 text-xs text-slate-500">
				The wasm bundle is generated and gitignored. Fetch it with{" "}
				<code>pwsh scripts/fetch-gridcraft-web.ps1</code>. Same-origin only: the
				parent bridge refuses messages from other origins, and the web build has
				no TCP control channel.
			</p>
		</div>
	);
}
