"use client";

import Link from "next/link";
import { useState, useMemo } from "react";
import type { Episode } from "@/lib/serverApi";

type SortKey = "date" | "like_count" | "view_count" | "set_count" | "guest_count" | "like_ratio";

const SORT_OPTIONS: { key: SortKey; label: string }[] = [
  { key: "date",        label: "Date" },
  { key: "like_count",  label: "Like count" },
  { key: "view_count",  label: "View count" },
  { key: "set_count",   label: "Set count" },
  { key: "guest_count", label: "Guest count" },
  { key: "like_ratio",  label: "Like ratio" },
];

function getValue(ep: Episode, key: SortKey): number {
  switch (key) {
    case "date":        return ep.number;
    case "like_count":  return ep.like_count ?? 0;
    case "view_count":  return ep.view_count ?? 0;
    case "set_count":   return ep.set_count;
    case "guest_count": return ep.guest_count ?? 0;
    case "like_ratio":
      return ep.view_count ? (ep.like_count ?? 0) / ep.view_count : 0;
  }
}

function fmt(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

type Props = { episodes: Episode[] };

export default function EpisodeControls({ episodes }: Props) {
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState<SortKey>("date");
  const [asc, setAsc] = useState(false);

  const results = useMemo(() => {
    const q = query.trim().toLowerCase();
    const list = q
      ? episodes.filter((ep) =>
          (ep.title || `Kill Tony #${ep.number}`).toLowerCase().includes(q)
        )
      : episodes;
    return [...list].sort((a, b) => {
      const diff = getValue(b, sort) - getValue(a, sort);
      return asc ? -diff : diff;
    });
  }, [episodes, query, sort, asc]);

  return (
    <div>
      {/* Search */}
      <div className="mb-4 flex items-center gap-2 rounded-xl border border-stone-200 px-3 py-2 focus-within:border-stone-400 transition-colors">
        <svg
          className="h-3.5 w-3.5 shrink-0 text-stone-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z"
          />
        </svg>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={`Search ${episodes.length} episodes…`}
          className="flex-1 bg-transparent text-sm text-stone-900 placeholder-stone-400 focus:outline-none"
        />
        {query && (
          <button
            onClick={() => setQuery("")}
            className="text-xs text-stone-400 hover:text-stone-600 transition-colors"
          >
            Clear ×
          </button>
        )}
      </div>

      {/* Direction toggle + sort chips */}
      <div className="mb-6 flex flex-wrap items-center gap-2">
        <button
          onClick={() => setAsc((v) => !v)}
          title={asc ? "Ascending — click to switch to descending" : "Descending — click to switch to ascending"}
          className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-stone-200 bg-white text-stone-500 hover:border-stone-400 hover:text-stone-800 transition-colors"
        >
          <svg
            className="h-3.5 w-3.5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            style={{ transform: asc ? "scaleY(-1)" : undefined }}
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4M17 8v12m0 0l4-4m-4 4l-4-4" />
          </svg>
        </button>

        {SORT_OPTIONS.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setSort(key)}
            className={`rounded-full px-3 py-1 text-xs font-medium border transition-colors ${
              sort === key
                ? "bg-stone-900 text-white border-stone-900"
                : "bg-white text-stone-600 border-stone-200 hover:border-stone-400"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Result count when searching */}
      {query && (
        <p className="mb-3 text-sm text-stone-400">
          {results.length} result{results.length !== 1 ? "s" : ""}
        </p>
      )}

      {/* List */}
      {results.length === 0 ? (
        <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
          <p className="text-stone-500">No episodes match.</p>
        </div>
      ) : (
        <div className="divide-y divide-stone-100 rounded-xl border border-stone-200">
          {results.map((ep) => (
            <Link
              key={ep.id}
              href={`/killtony/episodes/${ep.id}`}
              className="flex items-center justify-between px-5 py-4 hover:bg-stone-50 transition-colors"
            >
              <div>
                <span className="text-xs font-medium text-stone-400 uppercase tracking-wide">
                  Episode {ep.number}
                </span>
                <p className="mt-0.5 font-medium text-stone-900">
                  {ep.title || `Kill Tony #${ep.number}`}
                </p>
                <p className="text-sm text-stone-400">{ep.date}</p>
              </div>
              <div className="flex shrink-0 items-center gap-3 text-sm text-stone-400">
                {ep.view_count != null && (
                  <span>{fmt(ep.view_count)} views</span>
                )}
                {ep.like_count != null && ep.view_count != null && ep.view_count > 0 && (
                  <span>{((ep.like_count / ep.view_count) * 100).toFixed(1)}% liked</span>
                )}
                <span>{ep.set_count} sets →</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
