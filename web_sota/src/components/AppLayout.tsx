import {
	Archive,
	ChevronLeft,
	ChevronRight,
	ExternalLink,
	LayoutDashboard,
	LayoutGrid,
	MessagesSquare,
	Minimize2,
	PlayCircle,
	ScrollText,
	Settings,
	Table2,
	Terminal,
	Workflow,
	Wrench,
} from "lucide-react";
import { useEffect, useState } from "react";
import { Link, Outlet, useLocation } from "react-router-dom";
import { api } from "../lib/api";
import { useBackend } from "../store/backend";

const NAV = [
	{
		to: "/",
		label: "Dashboard",
		icon: LayoutDashboard,
		testid: "nav-dashboard",
	},
	{ to: "/apps", label: "Apps", icon: LayoutGrid, testid: "nav-apps" },
	{
		to: "/hands-in",
		label: "Hands-in",
		icon: PlayCircle,
		testid: "nav-hands-in",
	},
	{ to: "/flows", label: "Flows", icon: Workflow, testid: "nav-flows" },
	{ to: "/studio", label: "Studio", icon: Table2, testid: "nav-studio" },
	{ to: "/depot", label: "Depot", icon: Archive, testid: "nav-depot" },
	{ to: "/tools", label: "Tools", icon: Wrench, testid: "nav-tools" },
	{ to: "/skills", label: "Skills", icon: ScrollText, testid: "nav-skills" },
	{ to: "/chat", label: "Chat", icon: MessagesSquare, testid: "nav-chat" },
	{
		to: "/settings",
		label: "Settings",
		icon: Settings,
		testid: "nav-settings",
	},
	{ to: "/help", label: "Help", icon: ScrollText, testid: "nav-help" },
	{ to: "/logs", label: "Logs", icon: Terminal, testid: "nav-logs" },
];

export function MockBadge() {
	return (
		<span
			data-testid="mock-badge"
			className="rounded bg-amber-500/20 px-2 py-0.5 text-sm font-semibold text-amber-300"
		>
			MOCK
		</span>
	);
}

export default function AppLayout() {
	const [collapsed, setCollapsed] = useState(false);
	const [logsOpen, setLogsOpen] = useState(false);
	const [logs, setLogs] = useState<
		{ ts: string; source: string; message: string }[]
	>([]);
	const { apps, health, refresh } = useBackend();
	const loc = useLocation();

	useEffect(() => {
		refresh();
	}, [refresh]);
	useEffect(() => {
		const onKey = (e: KeyboardEvent) => {
			if (e.ctrlKey && e.key === "l") {
				e.preventDefault();
				setLogsOpen((v) => !v);
			}
		};
		window.addEventListener("keydown", onKey);
		return () => window.removeEventListener("keydown", onKey);
	}, []);
	useEffect(() => {
		if (logsOpen)
			api<{ logs: { ts: string; source: string; message: string }[] }>(
				"/api/logs?limit=100",
			)
				.then((j) => setLogs(j.logs ?? []))
				.catch(() => {});
	}, [logsOpen]);

	return (
		<div className="flex min-h-screen">
			<aside
				className={`border-r border-slate-800 bg-slate-900 ${collapsed ? "w-14" : "w-56"}`}
			>
				<div className="flex items-center justify-between p-3">
					{!collapsed && (
						<span className="font-bold">
							democraft{" "}
							<span className="text-sm text-slate-300">
								{health?.version ?? ""}
							</span>
						</span>
					)}
					<button
						type="button"
						data-testid="sidebar-toggle"
						aria-label="collapse"
						onClick={() => setCollapsed((v) => !v)}
						className="rounded p-1 hover:bg-slate-800"
					>
						{collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
					</button>
				</div>
				<div className="flex items-center gap-2 px-3 pb-2 text-sm text-slate-300">
					<span
						data-testid="backend-dot"
						className={`inline-block h-2 w-2 rounded-full ${health ? "bg-emerald-400" : "bg-red-400"}`}
					/>
					{!collapsed && <span>{health ? "backend ok" : "backend down"}</span>}
				</div>
				<nav className="flex flex-col gap-1 p-2">
					{NAV.map((n) => (
						<Link
							key={n.to}
							to={n.to}
							data-testid={n.testid}
							className="flex items-center gap-2 rounded px-2 py-1.5 text-sm hover:bg-slate-800"
						>
							<n.icon size={16} /> {!collapsed && n.label}
						</Link>
					))}
				</nav>
				{!collapsed && (
					<div className="p-2">
						<p className="px-2 text-sm uppercase text-slate-300">Craft apps</p>
						{apps.map((a) => (
							<Link
								key={a.key}
								to={`/craft/${a.key}`}
								data-testid={`nav-craft-${a.key}`}
								className="flex items-center justify-between rounded px-2 py-1 text-sm hover:bg-slate-800"
							>
								<span>{a.name}</span>
								{!a.installed && <MockBadge />}
							</Link>
						))}
					</div>
				)}
			</aside>
			<div className="flex flex-1 flex-col">
				<header
					className="flex items-center gap-2 border-b border-slate-800 bg-slate-900 px-4 py-2"
					data-testid="topbar"
				>
					<span data-testid="topbar-title" className="font-semibold">
						democraft-mcp
					</span>
					<div className="ml-auto flex items-center gap-2">
						<button
							type="button"
							data-testid="topbar-logs"
							aria-label="logs"
							onClick={() => setLogsOpen((v) => !v)}
							className="rounded p-1 hover:bg-slate-800"
						>
							<Terminal size={16} />
						</button>
						<Link
							data-testid="topbar-help"
							to="/help"
							aria-label="help"
							className="rounded p-1 hover:bg-slate-800"
						>
							<ScrollText size={16} />
						</Link>
						<button
							type="button"
							data-testid="topbar-companion"
							aria-label="companion"
							className="rounded p-1 hover:bg-slate-800"
						>
							<Minimize2 size={16} />
						</button>
						<a
							data-testid="topbar-popout"
							aria-label="pop out"
							href={loc.pathname}
							target="_blank"
							rel="noreferrer"
							className="rounded p-1 hover:bg-slate-800"
						>
							<ExternalLink size={16} />
						</a>
					</div>
				</header>
				<main className="mx-auto w-full max-w-5xl flex-1 p-6">
					<Outlet />
				</main>
				<footer className="border-t border-slate-800 px-6 py-3 text-sm text-slate-300">
					democraft-mcp - real headless demos for the Craft family. Vienna.
				</footer>
			</div>
			{logsOpen && (
				<div
					data-testid="logs-modal"
					className="fixed right-4 top-14 max-h-[70vh] w-[420px] overflow-auto rounded border border-slate-700 bg-slate-900 p-3 text-sm"
				>
					<p className="mb-2 font-semibold">Logs (Ctrl+L)</p>
					{logs.map((l) => (
						<p
							key={`${l.ts}-${l.source}-${l.message.slice(0, 32)}`}
							className="font-mono text-slate-300"
						>
							[{l.ts}] {l.source}: {l.message}
						</p>
					))}
					{!logs.length && (
						<p className="text-slate-300">No log entries yet.</p>
					)}
				</div>
			)}
		</div>
	);
}
