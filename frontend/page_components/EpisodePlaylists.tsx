import Link from "next/link";
import type { Episode } from "@/lib/serverApi";
import { EPISODE_LISTS } from "@/lib/playlists";
import YoutubeThumbnail from "@/components/YoutubeThumbnail";

function fmtDate(date: string | null): string {
  if (!date) return "";
  return new Date(date).toLocaleDateString("en-AU", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

type Props = { episodes: Episode[] };

export default function EpisodePlaylists({ episodes }: Props) {
  const byId = new Map(episodes.map((ep) => [ep.id, ep]));
  const byNumber = new Map(episodes.map((ep) => [ep.number, ep]));

  const lists = EPISODE_LISTS.map((list) => ({
    ...list,
    items: list.ids
      .map((id) => (list.matchBy === "number" ? byNumber : byId).get(id))
      .filter(Boolean) as Episode[],
  })).filter((list) => list.items.length > 0);

  if (lists.length === 0) return null;

  return (
    <div className="space-y-8">
      {lists.map((list) => (
        <section key={list.id}>
          <div className="mb-3">
            <h2 className="text-sm font-bold text-stone-950">{list.title}</h2>
            <p className="mt-0.5 text-xs text-stone-500">{list.description}</p>
          </div>
          <div className="flex gap-3 overflow-x-auto pb-2">
            {list.items.map((ep) => (
              <Link
                key={ep.id}
                href={`/killtony/episodes/${ep.id}`}
                className="group w-52 shrink-0 overflow-hidden rounded-lg border border-stone-200 bg-white transition-colors hover:border-primary/40 hover:shadow-sm"
              >
                <YoutubeThumbnail
                  videoId={ep.youtube_id}
                  alt={ep.title || `Kill Tony #${ep.number}`}
                  className="aspect-video w-full bg-stone-950"
                />
                <div className="p-2.5">
                  <p className="text-[11px] font-bold uppercase tracking-wide text-primary">
                    Episode {ep.number}
                  </p>
                  <p className="mt-1 truncate font-bold leading-tight text-stone-950 transition-colors group-hover:text-primary">
                    {ep.title || `Kill Tony #${ep.number}`}
                  </p>
                  <p className="mt-1 truncate text-xs text-stone-500">{fmtDate(ep.date)}</p>
                </div>
              </Link>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
