import { Link } from "react-router-dom";
import { apiBase, type CraftApp, type GalleryTile } from "../lib/api";
import { appMeta } from "../lib/appMeta";

/** The latest real renders, framed like prints on a proof sheet. */
export default function ContactSheet({
	tiles,
	apps,
	dense = false,
}: {
	tiles: GalleryTile[];
	apps: CraftApp[];
	dense?: boolean;
}) {
	const name = (key: string) => apps.find((a) => a.key === key)?.name ?? key;
	return (
		<div
			data-testid="contact-sheet"
			className={`grid gap-x-3 gap-y-4 ${
				dense
					? "grid-cols-2 sm:grid-cols-3 lg:grid-cols-4"
					: "grid-cols-2 md:grid-cols-3 xl:grid-cols-4"
			}`}
		>
			{tiles.map((t) => {
				const meta = appMeta(t.app);
				return (
					<figure key={`${t.app}/${t.demo}`} className="group min-w-0">
						<Link
							to={`/craft/${t.app}?demo=${t.demo}`}
							className="print block aspect-[4/3] overflow-hidden"
							style={{ borderTopColor: meta.hue, borderTopWidth: 2 }}
							aria-label={`${name(t.app)}: ${t.title}`}
						>
							<img
								src={`${apiBase()}${t.url}`}
								alt={`${name(t.app)} ${t.demo} render`}
								loading="lazy"
								className="transition-transform duration-300 group-hover:scale-[1.02]"
							/>
						</Link>
						<figcaption className="mt-1.5 flex items-baseline justify-between gap-2 text-xs">
							<span className="truncate text-paper">
								{name(t.app)}
								<span className="text-muted"> / {t.demo}</span>
							</span>
							{t.images > 1 && (
								<span className="shrink-0 text-muted">{t.images} images</span>
							)}
						</figcaption>
					</figure>
				);
			})}
		</div>
	);
}
