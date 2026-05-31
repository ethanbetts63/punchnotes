import Link from "next/link";
import type { SetListItem } from "@/lib/serverApi";
import { SET_LISTS } from "@/lib/playlists";
import SetImage from "@/components/SetImage";

function fmtSeconds(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  return `${m}:${String(s).padStart(2, "0")}`;
}

type Props = { sets: SetListItem[] };

export default function SetPlaylists({ sets }: Props) {
  const byId = new Map(sets.map((s) => [s.id, s]));

  const lists = SET_LISTS.map((list) => ({
    ...list,
    items: list.ids.map((id) => byId.get(id)).filter(Boolean) as SetListItem[],
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
            {list.items.map((set) => (
              <Link
                key={set.id}
                href={`/killtony/sets/${set.id}`}
                className="group w-52 shrink-0 overflow-hidden rounded-lg border border-stone-200 bg-white transition-colors hover:border-primary/40 hover:shadow-sm"
              >
                <SetImage
                  imageUrl={set.image_url}
                  fallbackVideoId={set.episode.youtube_id}
                  alt={`${set.comedian.name} set image`}
                  className="h-24 w-full bg-stone-950"
                />
                <div className="p-2.5">
                  <p className="truncate font-bold leading-tight text-stone-950 transition-colors group-hover:text-primary">
                    {set.comedian.name}
                  </p>
                  <p className="mt-1 truncate text-xs text-stone-500">
                    KT #{set.episode.number} / Set {set.set_number} / {fmtSeconds(set.start_seconds)}
                  </p>
                  {set.joke_book_award && (
                    <span className="mt-1.5 inline-block rounded-full bg-stone-100 px-2 py-0.5 text-[10px] font-bold text-stone-700">
                      {set.joke_book_award} joke book
                    </span>
                  )}
                </div>
              </Link>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
