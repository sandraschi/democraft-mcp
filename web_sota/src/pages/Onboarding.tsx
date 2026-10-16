import { Link } from "react-router-dom";
import { MockBadge } from "../components/AppLayout";
import { useBackend } from "../store/backend";

export default function Onboarding() {
	const { missing } = useBackend();
	return (
		<div data-testid="onboarding-page">
			<h1 className="text-2xl font-bold">Onboarding</h1>
			<ol className="mt-3 flex list-decimal flex-col gap-3 pl-5 text-sm">
				<li>
					Install the Craft apps from getartcraft.com/apps (default paths).{" "}
					{missing.length > 0 ? (
						<>
							Still missing: {missing.join(", ")} <MockBadge />
						</>
					) : (
						"All detected."
					)}
				</li>
				<li>Install Ollama and pull gemma4:e4b (or set DEMOCRAFT_MODEL).</li>
				<li>
					Run the CAD house-plan demo. MOCK badges clear by successful runs
					only.
				</li>
			</ol>
			<p className="mt-3 text-sm text-slate-300">
				Full narrative: docs/ONBOARDING.md.{" "}
				<Link to="/" className="underline">
					Back to Dashboard
				</Link>
			</p>
		</div>
	);
}
