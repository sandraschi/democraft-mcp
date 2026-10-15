import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { useBackend } from "../store/backend";

const FAQS = [
	[
		"Do demos need accounts?",
		"Demo #1s never do. Some advanced engine features need ArtCraft tokens and stay marked MOCK until configured.",
	],
	[
		"Ollama is down - do demos still run?",
		"Yes. You still get every demo output; only the AI-written caption is skipped.",
	],
	[
		"Where are my outputs?",
		"outbox/<app>/<demo>/ under the repo - see the Inbox page.",
	],
	[
		"A demo step failed - is that normal?",
		"It can be. The Craft page shows the engine's real error message - read it, fix what's named, retry.",
	],
];

export default function Help() {
	const { apps } = useBackend();
	const [apiPorts, setApiPorts] = useState("11246/11245");
	useEffect(() => {
		api("/api/health")
			.then(() => setApiPorts("11246/11245"))
			.catch(() => setApiPorts("backend unreachable"));
	}, []);
	return (
		<div data-testid="help-page">
			<h1 className="text-2xl font-bold">Help</h1>
			<h2 className="mt-4 font-semibold">First demo in 3 steps</h2>
			<ol className="mt-1 list-decimal pl-5 text-sm text-slate-300">
				<li>
					Check the backend line above reads 11246/11245 - if it says
					unreachable, start the backend.
				</li>
				<li>Open any installed Craft app in the sidebar (no MOCK badge).</li>
				<li>
					Press Run demo #1 and read the artifacts. Every attempt, including
					failures, lands in the Inbox.
				</li>
			</ol>
			<h2 className="mt-4 font-semibold">Wrappees (host apps)</h2>
			<table className="mt-2 w-full text-sm">
				<tbody>
					{apps.map((a) => (
						<tr key={a.key} className="border-t border-slate-800">
							<td className="py-1">{a.name}</td>
							<td>{a.installed ? "installed" : "MISSING - see onboarding"}</td>
						</tr>
					))}
				</tbody>
			</table>
			<h2 className="mt-4 font-semibold">API / ports</h2>
			<p className="text-sm text-slate-300">
				Backend :11246 (/api/*, /mcp), frontend :11245. CORS: localhost only.{" "}
				{apiPorts}.
			</p>
			<h2 className="mt-4 font-semibold">Error fix</h2>
			<p className="text-sm text-slate-300">
				wrappee_missing: install the app. needs_account: configure tokens.
				needs_input: follow the recovery path. timeout: split ranges. Full
				catalog: docs/TROUBLESHOOTING.md.
			</p>
			<h2 className="mt-4 font-semibold">FAQ</h2>
			{FAQS.map(([q, a]) => (
				<details
					key={q}
					className="mt-2 rounded border border-slate-800 p-2 text-sm"
				>
					<summary className="cursor-pointer">{q}</summary>
					<p className="mt-1 text-slate-300">{a}</p>
				</details>
			))}
		</div>
	);
}
