import { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function Skills() {
	const [skills, setSkills] = useState<
		{ name: string; path: string; preview: string }[]
	>([]);
	const [loading, setLoading] = useState(true);
	const [failed, setFailed] = useState(false);
	useEffect(() => {
		api<{ skills: typeof skills }>("/api/skills")
			.then((j) => {
				setSkills(j.skills);
				setLoading(false);
			})
			.catch(() => {
				setFailed(true);
				setLoading(false);
			});
	}, []);
	return (
		<div data-testid="skills-page">
			<h1 className="text-2xl font-bold">Skills</h1>
			{loading && <p className="mt-2 text-sm text-muted">Loading skills...</p>}
			{failed && (
				<p className="mt-2 text-sm text-amber-300">
					Backend unreachable - start it and retry.
				</p>
			)}
			{skills.map((s) => (
				<details
					key={s.name}
					className="mt-3 rounded-md border border-line bg-surface p-3"
				>
					<summary className="cursor-pointer font-mono">
						{s.name} <span className="text-sm text-muted">{s.path}</span>
					</summary>
					<pre className="mt-2 whitespace-pre-wrap text-sm text-muted">
						{s.preview}
					</pre>
				</details>
			))}
			{!skills.length && (
				<p className="mt-2 text-muted">No skills registered.</p>
			)}
		</div>
	);
}
