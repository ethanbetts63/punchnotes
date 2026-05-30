"use client";

import Link from "next/link";
import type { ComedianAttribute, SetListItem } from "@/lib/serverApi";
import SetImage from "@/components/SetImage";

type Playlist = {
  title: string;
  label: string;
  description: string;
  attribute: ComedianAttribute;
};

const PLAYLISTS: Playlist[] = [
  {
    title: "First regular sets",
    label: "First regular set",
    description: "Earliest indexed set from each regular.",
    attribute: "regular",
  },
  {
    title: "Golden ticket origins",
    label: "Golden ticket winner",
    description: "Earliest indexed set from each golden ticket winner.",
    attribute: "golden_ticket",
  },
];

function fmtSeconds(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  return `${m}:${String(s).padStart(2, "0")}`;
}

function firstSetsFor(sets: SetListItem[], attribute: ComedianAttribute): SetListItem[] {
  const firstByComedian = new Map<number, SetListItem>();

  for (const set of sets) {
    if (!set.comedian.attributes.includes(attribute)) continue;
    const current = firstByComedian.get(set.comedian.id);
    if (
      !current ||
      set.episode.number < current.episode.number ||
      (set.episode.number === current.episode.number && set.start_seconds < current.start_seconds)
    ) {
      firstByComedian.set(set.comedian.id, set);
    }
  }

  return [...firstByComedian.values()]
    .sort((a, b) => a.episode.number - b.episode.number || a.start_seconds - b.start_seconds)
    .slice(0, 8);
}

type Props = {
  sets: SetListItem[];
};

export default function SetPlaylistsOverview({ sets }: Props) {
  const playlists = PLAYLISTS.map((playlist) => ({
    ...playlist,
    items: firstSetsFor(sets, playlist.attribute),
  })).filter((playlist) => playlist.items.length > 0);

  if (playlists.length === 0) return null;

  return (
    <section className="mb-6 border-b border-stone-200 pb-6">
      <div className="mb-3">
        <p className="text-xs font-bold uppercase tracking-wide text-primary">Playlists</p>
        <h2 className="mt-1 text-lg font-bold tracking-tight text-stone-950">Curated ways into the set archive</h2>
      </div>

      <div className="space-y-4">
        {playlists.map((playlist) => (
          <div key={playlist.title}>
            <div className="mb-2 flex items-end justify-between gap-3">
              <div>
                <h3 className="text-sm font-bold text-stone-950">{playlist.title}</h3>
                <p className="mt-0.5 text-xs text-stone-500">{playlist.description}</p>
              </div>
              <span className="shrink-0 text-xs font-bold text-stone-400">{playlist.items.length}</span>
            </div>

            <div className="flex gap-3 overflow-x-auto pb-1">
              {playlist.items.map((set) => (
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
                    <p className="text-[11px] font-bold uppercase tracking-wide text-primary">{playlist.label}</p>
                    <p className="mt-1 truncate font-bold leading-tight text-stone-950 transition-colors group-hover:text-primary">
                      {set.comedian.name}
                    </p>
                    <p className="mt-1 truncate text-xs text-stone-500">
                      KT #{set.episode.number} / Set {set.set_number} / {fmtSeconds(set.start_seconds)}
                    </p>
                    <div className="mt-1.5 flex flex-wrap gap-1.5">
                      <span className="rounded-full bg-stone-100 px-2 py-0.5 text-[10px] font-bold text-stone-700">
                        {set.bit_count} bit{set.bit_count === 1 ? "" : "s"}
                      </span>
                      {set.joke_book_award && (
                        <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-bold text-amber-700">
                          {set.joke_book_award} joke book
                        </span>
                      )}
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
