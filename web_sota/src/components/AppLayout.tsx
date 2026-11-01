import {
	Archive,
	ChevronLeft,
	ChevronRight,
	CircleHelp,
	ExternalLink,
	LayoutDashboard,
	LayoutGrid,
	MessagesSquare,
	PlayCircle,
	ScrollText,
	Search,
	Settings,
	Table2,
	Terminal,
	Workflow,
	Wrench,
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import {
	Link,
	NavLink,
	Outlet,
	useLocation,
	useNavigate,
} from "react-router-dom";
import { api } from "../lib/api";
import { appMeta } from "../lib/appMeta";
import { useBackend } from "../store/backend";

const BENCH = [
	{
		to: "/",
		label: "Dashboard",
		icon: LayoutDashboard,
		testid: "nav-dashboard",
	},
	{
		to: "/hands-in",
		label: "Hands-in",
		icon: PlayCircle,
		testid: "nav-hands-in",
	},
	{ to: "/flows", label: "Flows", icon: Workflow, testid: "nav-flows" },
	{ to: "/studio", label: "Studio", icon: Table2, testid: "nav-studio" },
	{ to: "/depot", label: "Depot", icon: Archive, testid: "nav-depot" },
	{ to: "/apps", label: "Builds", icon: LayoutGrid, testid: "nav-apps" },
];
const SYSTEM = [
	{ to: "/tools", label: "Tools", icon: Wrench, testid: "nav-tools" },
	{ to: "/skills", label: "Skills", icon: ScrollText, testid: "nav-skills" },
	{ to: "/chat", label: "Chat", icon: MessagesSquare, testid: "nav-chat" },
	{
		to: "/settings",
		label: "Settings",
		icon: Settings,
		testid: "nav-settings",
	},
	{ to: "/help", label: "Help", icon: CircleHelp, testid: "nav-help" },
	{ to: "/logs", label: "Logs", icon: Terminal, testid: "nav-logs" },
];
const TITLES: Record<string, string> = Object.fromEntries(
	[...BENCH, ...SYSTEM].map((n) => [n.to, n.label]),
);

export function MockBadge() {
	return (
		<span
			data-testid="mock-badge"
			title="Not installed on this machine: install it to run the demos"
			className="rounded bg-amber-500/15 px-1.5 py-0.5 text-[11px] font-semibold text-amber-300"
		>
			MOCK
		</span>
	);
}

function navClass({ isActive }: { isActive: boolean }) {
	return `flex items-center gap-2.5 rounded-md px-2 py-1.5 text-sm transition-colors ${
		isActive
			? "bg-raised text-paper"
			: "text-muted hover:bg-raised/60 hover:text-paper"
	}`;
}

interface Hit {
	label: string;
	hint: string;
	to: string;
}

export default function AppLayout() {
	const [collapsed, setCollapsed] = useState(false);
	const [logsOpen, setLogsOpen] = useState(false);
	const [paletteOpen, setPaletteOpen] = useState(false);
	const [query, setQuery] = useState("");
	const [logs, setLogs] = useState<
		{ ts: string; source: string; message: string }[]
	>([]);
	const { apps, health, refresh } = useBackend();
	const loc = useLocation();
	const nav = useNavigate();
	const inputRef = useRef<HTMLInputElement>(null);

	useEffect(() => {
		refresh();
	}, [refresh]);
	useEffect(() => {
		const onKey = (e: KeyboardEvent) => {
			if (e.ctrlKey && e.key === "l") {
				e.preventDefault();
				setLogsOpen((v) => !v);
			}
			if ((e.ctrlKey || e.metaKey) && e.key === "k") {
				e.preventDefault();
				setPaletteOpen(true);
			}
			if (e.key === "Escape") setPaletteOpen(false);
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
	useEffect(() => {
		if (paletteOpen) {
			setQuery("");
			window.setTimeout(() => inputRef.current?.focus(), 0);
		}
	}, [paletteOpen]);

	const hits = useMemo<Hit[]>(() => {
		const all: Hit[] = [
			...[...BENCH, ...SYSTEM].map((n) => ({
				label: n.label,
				hint: "page",
				to: n.to,
			})),
			...apps.map((a) => ({
				label: a.name,
				hint: a.clone_of,
				to: `/craft/${a.key}`,
			})),
			...apps.flatMap((a) =>
				a.demos.map((d) => ({
					label: d.title.replace(/^Demo \d+: /, ""),
					hint: a.name,
					to: `/craft/${a.key}?demo=${d.id}`,
				})),
			),
		];
		const q = query.trim().toLowerCase();
		return (
			q
				? all.filter((h) => `${h.label} ${h.hint}`.toLowerCase().includes(q))
				: all
		).slice(0, 12);
	}, [apps, query]);

	const craftKey = loc.pathname.startsWith("/craft/")
		? loc.pathname.split("/")[2]
		: "";
	const title =
		TITLES[loc.pathname] ??
		apps.find((a) => a.key === craftKey)?.name ??
		(loc.pathname.startsWith("/flows") ? "Flows" : "democraft");
	const core = apps.filter((a) => a.family !== "community");
	const community = apps.filter((a) => a.family === "community");

	const appLink = (a: (typeof apps)[number]) => {
		const meta = appMeta(a.key);
		return (
			<NavLink
				key={a.key}
				to={`/craft/${a.key}`}
				data-testid={`nav-craft-${a.key}`}
				title={collapsed ? a.name : undefined}
				className={({ isActive }) =>
					`flex items-center gap-2.5 rounded-md px-2 py-1 text-sm transition-colors ${
						isActive ? "bg-raised text-paper" : "text-muted hover:text-paper"
					}`
				}
			>
				<meta.icon size={15} style={{ color: meta.hue }} className="shrink-0" />
				{!collapsed && (
					<>
						<span className="truncate">{a.name}</span>
						<span className="ml-auto font-mono text-[11px] text-muted/70">
							{a.installed ? (a.version ?? "") : "-"}
						</span>
					</>
				)}
			</NavLink>
		);
	};

	return (
		<div className="flex min-h-screen">
			<aside
				className={`sticky top-0 flex h-screen shrink-0 flex-col border-r border-line bg-surface/80 backdrop-blur ${
					collapsed ? "w-14" : "w-60"
				}`}
			>
				<div className="flex items-center justify-between px-3 pt-3 pb-2">
					{!collapsed && (
						<Link to="/" className="leading-tight">
							<span className="text-[15px] font-semibold tracking-tight">
								democraft
							</span>
							<span className="ml-1.5 font-mono text-[11px] text-muted">
								{health?.version ?? ""}
							</span>
						</Link>
					)}
					<button
						type="button"
						data-testid="sidebar-toggle"
						aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
						onClick={() => setCollapsed((v) => !v)}
						className="rounded-md p-1 text-muted hover:bg-raised hover:text-paper"
					>
						{collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
					</button>
				</div>
				<div className="flex items-center gap-2 px-3 pb-3 text-xs text-muted">
					<span
						data-testid="backend-dot"
						className={`inline-block h-1.5 w-1.5 rounded-full ${
							health ? "bg-emerald-400" : "bg-red-400"
						}`}
					/>
					{!collapsed &&
						(health
							? `${health.installed} of ${health.apps} apps installed`
							: "backend not reachable")}
				</div>
				<nav className="flex-1 space-y-4 overflow-y-auto px-2 pb-4">
					<div className="space-y-0.5">
						{BENCH.map((n) => (
							<NavLink
								key={n.to}
								to={n.to}
								end={n.to === "/"}
								data-testid={n.testid}
								className={navClass}
							>
								<n.icon size={16} className="shrink-0" />
								{!collapsed && n.label}
							</NavLink>
						))}
					</div>
					{apps.length > 0 && (
						<div className="space-y-0.5 border-t border-line pt-3">
							{!collapsed && (
								<p className="px-2 pb-1 text-xs text-muted">
									Storytold ArtCraft
								</p>
							)}
							{core.map(appLink)}
							{community.length > 0 && (
								<>
									{!collapsed && (
										<p className="px-2 pt-3 pb-1 text-xs text-muted">
											Community
										</p>
									)}
									{community.map(appLink)}
								</>
							)}
						</div>
					)}
					<div className="space-y-0.5 border-t border-line pt-3">
						{SYSTEM.map((n) => (
							<NavLink
								key={n.to}
								to={n.to}
								data-testid={n.testid}
								className={navClass}
							>
								<n.icon size={16} className="shrink-0" />
								{!collapsed && n.label}
							</NavLink>
						))}
					</div>
				</nav>
			</aside>
			<div className="flex min-w-0 flex-1 flex-col">
				<header
					className="sticky top-0 z-20 flex items-center gap-3 border-b border-line bg-bench/85 px-5 py-2.5 backdrop-blur"
					data-testid="topbar"
				>
					<span
						data-testid="topbar-title"
						className="truncate text-sm font-medium"
					>
						{title}
					</span>
					<button
						type="button"
						data-testid="topbar-search"
						onClick={() => setPaletteOpen(true)}
						className="ml-auto flex w-56 items-center gap-2 rounded-md border border-line bg-surface px-2.5 py-1.5 text-left text-xs text-muted hover:border-zinc-600 max-md:w-auto"
					>
						<Search size={14} />
						<span className="max-md:hidden">Jump to app or demo</span>
						<kbd className="ml-auto font-mono text-[10px] max-md:hidden">
							Ctrl K
						</kbd>
					</button>
					<button
						type="button"
						data-testid="topbar-logs"
						aria-label="Logs (Ctrl+L)"
						onClick={() => setLogsOpen((v) => !v)}
						className="rounded-md p-1.5 text-muted hover:bg-raised hover:text-paper"
					>
						<Terminal size={16} />
					</button>
					<Link
						data-testid="topbar-help"
						to="/help"
						aria-label="Help"
						className="rounded-md p-1.5 text-muted hover:bg-raised hover:text-paper"
					>
						<CircleHelp size={16} />
					</Link>
					<a
						data-testid="topbar-popout"
						aria-label="Open this page in a new window"
						href={`${loc.pathname}${loc.search}`}
						target="_blank"
						rel="noreferrer"
						className="rounded-md p-1.5 text-muted hover:bg-raised hover:text-paper"
					>
						<ExternalLink size={16} />
					</a>
				</header>
				<main className="mx-auto w-full max-w-6xl flex-1 px-6 py-8">
					<Outlet />
				</main>
				<footer className="border-t border-line px-6 py-3 text-xs text-muted">
					democraft - every Craft app, run for real on this machine. Vienna.
				</footer>
			</div>

			{paletteOpen && (
				<div className="fixed inset-0 z-40 flex items-start justify-center pt-[14vh]">
					<button
						type="button"
						aria-label="Close"
						onClick={() => setPaletteOpen(false)}
						className="absolute inset-0 cursor-default bg-black/60 backdrop-blur-sm"
					/>
					<div
						data-testid="palette"
						role="dialog"
						aria-label="Jump to"
						className="relative w-[min(560px,92vw)] overflow-hidden rounded-lg border border-line bg-surface shadow-2xl"
					>
						<input
							ref={inputRef}
							value={query}
							onChange={(e) => setQuery(e.target.value)}
							onKeyDown={(e) => {
								if (e.key === "Enter" && hits[0]) {
									nav(hits[0].to);
									setPaletteOpen(false);
								}
							}}
							placeholder="SolidCraft, bookmarks, macro..."
							className="w-full border-b border-line bg-transparent px-4 py-3 text-sm outline-none placeholder:text-muted"
						/>
						<ul className="max-h-80 overflow-y-auto py-1">
							{hits.map((h) => (
								<li key={`${h.to}-${h.label}`}>
									<button
										type="button"
										onClick={() => {
											nav(h.to);
											setPaletteOpen(false);
										}}
										className="flex w-full items-baseline justify-between gap-3 px-4 py-2 text-left text-sm hover:bg-raised"
									>
										<span className="truncate">{h.label}</span>
										<span className="shrink-0 text-xs text-muted">
											{h.hint}
										</span>
									</button>
								</li>
							))}
							{!hits.length && (
								<li className="px-4 py-3 text-sm text-muted">
									Nothing matches "{query}".
								</li>
							)}
						</ul>
					</div>
				</div>
			)}

			{logsOpen && (
				<div
					data-testid="logs-modal"
					className="fixed right-4 top-14 z-30 max-h-[70vh] w-[440px] overflow-auto rounded-lg border border-line bg-surface/95 p-3 text-sm shadow-2xl backdrop-blur"
				>
					<p className="mb-2 font-medium">Logs</p>
					{logs.map((l) => (
						<p
							key={`${l.ts}-${l.source}-${l.message.slice(0, 32)}`}
							className="font-mono text-xs text-muted"
						>
							[{l.ts}] {l.source}: {l.message}
						</p>
					))}
					{!logs.length && <p className="text-muted">No log entries yet.</p>}
				</div>
			)}
		</div>
	);
}
