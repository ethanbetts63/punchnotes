"use client";

import Link from "next/link";
import { Play } from "lucide-react";
import { useMemo, useState } from "react";
import type { ComedianAttribute, SetListItem } from "@/lib/serverApi";
import YoutubeThumbnail from "@/components/YoutubeThumbnail";

type PlaylistKey = "regulars" | "golden_tickets";

type Playlist = {
  key: PlaylistKey;
  title: string;
  label: string;
  description: string;
  attribute: ComedianAttribute;
};

const PLAYLISTS: Playlist[] = [
  {
    key: "regulars",
    title: "First regular sets",
    label: "First regular set",
    description: "The earliest indexed set from comedians who became regulars.",
    attribute: "regular",
  },
  {
    key: "golden_tickets",
    title: "Golden ticket origins",
    label: "Golden ticket winner",
    description: "The earliest indexed set from golden ticket winners.",
    attribute: "golden_ticket",
  },
];

const jokeBookLabel: Record<string, string> = {
  small: "Small Joke Book",
  medium: "Medium Joke Book",
  large: "Large Joke Book",
};

const jokeBookClassName: Record<string, string> = {
  small: "bg-stone-100 text-stone-600",
  medium: "bg-amber-100 text-amber-700",
  large: "bg-red-100 text-primary",
};

function fmtSeconds(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  return `${m}:${String(s).padStart(2, "0")}`;
}

function fmt2(value: number | null): string {
  return value == null ? "-" : value.toFixed(2);
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
    .slice(0, 6);
}

type Props = {
  sets: SetListItem[];
};

export default function CuratedSetsSection({ sets }: Props) {
  const [activeKey, setActiveKey] = useState<PlaylistKey>("regulars");
  const playlists = useMemo(
    () => PLAYLISTS.map((playlist) => ({
      ...playlist,
      items: firstSetsFor(sets, playlist.attribute),
    })),
    [sets]
  );

  const active = playlists.find((playlist) => playlist.key === activeKey) ?? playlists[0];
  if (!active || active.items.length === 0) return null;

  return (
    <section className="border-b border-stone-200 bg-white px-4 py-10">
      <div className="mx-auto max-w-6xl">
        <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-wide text-primary">Essential sets</p>
            <h2 className="mt-1 text-xl font-bold tracking-tight text-stone-950">
              Watch the archive by story
            </h2>
            <p className="mt-1 text-sm text-stone-500">{active.description}</p>
          </div>
          <Link
            href="/killtony/sets"
            className="text-sm font-bold text-stone-500 transition-colors hover:text-stone-950"
          >
            Browse all sets
          </Link>
        </div>

        <div className="mb-4 flex gap-2 overflow-x-auto pb-1">
          {playlists.map((playlist) => (
            <button
              key={playlist.key}
              type="button"
              onClick={() => setActiveKey(playlist.key)}
              className={`shrink-0 rounded-md border px-3 py-1.5 text-xs font-bold transition-colors ${
                playlist.key === active.key
                  ? "border-stone-950 bg-stone-950 text-white"
                  : "border-stone-200 bg-white text-stone-600 hover:border-stone-400 hover:text-stone-950"
              }`}
            >
              {playlist.title}
            </button>
          ))}
        </div>

        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {active.items.map((set) => (
            <Link
              key={set.id}
              href={`/killtony/sets/${set.id}`}
              className="group flex overflow-hidden rounded-lg border border-stone-200 bg-white transition-colors hover:border-primary/40 hover:shadow-sm"
            >
              <YoutubeThumbnail
                videoId={set.episode.youtube_id}
                alt={set.episode.title}
                className="w-28 shrink-0 bg-stone-950"
                fit="cover"
              />
              <div className="min-w-0 flex-1 p-3">
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0">
                    <p className="text-[11px] font-bold uppercase tracking-wide text-primary">
                      {active.label}
                    </p>
                    <p className="mt-1 truncate font-bold leading-tight text-stone-950 transition-colors group-hover:text-primary">
                      {set.comedian.name}
                    </p>
                  </div>
                  <Play className="mt-0.5 h-4 w-4 shrink-0 text-stone-300 transition-colors group-hover:text-stone-600" />
                </div>
                <p className="mt-1 truncate text-xs text-stone-500">
                  KT #{set.episode.number} / Set {set.set_number} / {fmtSeconds(set.start_seconds)}
                </p>
                <div className="mt-2 flex flex-wrap items-center gap-1.5">
                  <span className="rounded-full bg-stone-100 px-2 py-0.5 text-[10px] font-bold text-stone-700">
                    {set.bit_count} bit{set.bit_count === 1 ? "" : "s"}
                  </span>
                  <span className="rounded-full bg-stone-100 px-2 py-0.5 text-[10px] font-bold text-stone-700">
                    Setup/punch {fmt2(set.hit_ratio)}
                  </span>
                  {set.joke_book_award && (
                    <span className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${jokeBookClassName[set.joke_book_award]}`}>
                      {jokeBookLabel[set.joke_book_award]}
                    </span>
                  )}
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
