"use client";

import Link from "next/link";
import { useState, useMemo } from "react";
import type { Episode } from "@/lib/serverApi";
import Paginator from "@/components/Paginator";
import YoutubeThumbnail from "@/components/YoutubeThumbnail";

const PAGE_SIZE = 20;

type SortKey =
  | "date"
  | "duration"
  | "set_count"
  | "bucket_pulls"
  | "golden_tickets"
  | "large_joke_books"
  | "regulars"
  | "view_count"
  | "like_count"
  | "like_ratio";

const SORT_OPTIONS: { key: SortKey; label: string }[] = [
  { key: "date",             label: "Date" },
  { key: "duration",         label: "Duration" },
  { key: "set_count",        label: "Set count" },
  { key: "bucket_pulls",     label: "Bucket pulls" },
  { key: "golden_tickets",   label: "Golden tickets" },
  { key: "large_joke_books", label: "Big joke books" },
  { key: "regulars",         label: "Regulars" },
  { key: "view_count",       label: "View count" },
  { key: "like_count",       label: "Like count" },
  { key: "like_ratio",       label: "View/like ratio" },
];

function getValue(ep: Episode, key: SortKey): number {
  switch (key) {
    case "date":             return ep.number;
    case "duration":         return ep.duration_seconds ?? 0;
    case "set_count":        return ep.set_count;
    case "bucket_pulls":     return ep.bucket_pull_count;
    case "golden_tickets":   return ep.golden_ticket_count;
    case "large_joke_books": return ep.large_joke_book_count;
    case "regulars":         return ep.regular_count;
    case "view_count":       return ep.view_count ?? 0;
    case "like_count":       return ep.like_count ?? 0;
    case "like_ratio":
      return ep.view_count ? (ep.like_count ?? 0) / ep.view_count : 0;
  }
}

function fmt(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

function fmtDuration(seconds: number | null): string {
  if (!seconds) return "—";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  return h > 0 ? `${h}h ${m}m` : `${m}m`;
}

function fmtDate(date: string | null): string {
  if (!date) return "—";
  return new Date(date).toLocaleDateString("en-AU", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex flex-col items-center rounded-md border border-stone-100 bg-stone-50 px-2.5 py-1.5 text-center">
      <span className="text-xs font-semibold leading-tight tabular-nums text-stone-800">{value}</span>
      <span className="mt-0.5 whitespace-nowrap text-[10px] leading-tight text-stone-400">{label}</span>
    </div>
  );
}

type Props = { episodes: Episode[]; initialQuery?: string };

export default function EpisodeControls({ episodes, initialQuery = "" }: Props) {
  const [query, setQuery] = useState(initialQuery);
  const [sort, setSort] = useState<SortKey>("date");
  const [asc, setAsc] = useState(false);
  const [page, setPage] = useState(1);

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

  const totalPages = Math.ceil(results.length / PAGE_SIZE);
  const pageItems = results.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  function handleQuery(q: string) { setQuery(q); setPage(1); }
  function handleSort(key: SortKey) { setSort(key); setPage(1); }
  function handleAsc() { setAsc((v) => !v); setPage(1); }

  return (
    <div>
      {/* Search */}
      <div className="mb-4 flex items-center gap-2 rounded-xl border border-stone-200 px-3 py-2 transition-colors focus-within:border-stone-400">
        <svg className="h-3.5 w-3.5 shrink-0 text-stone-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
        </svg>
        <input
          type="text"
          value={query}
          onChange={(e) => handleQuery(e.target.value)}
          placeholder={`Search ${episodes.length} episodes…`}
          className="flex-1 bg-transparent text-sm text-stone-900 placeholder-stone-400 focus:outline-none"
        />
        {query && (
          <button onClick={() => handleQuery("")} className="text-xs text-stone-400 transition-colors hover:text-stone-600">
            Clear ×
          </button>
        )}
      </div>

      {/* Sort controls */}
      <div className="mb-6 flex flex-wrap items-center gap-2">
        <button
          onClick={handleAsc}
          title={asc ? "Ascending — click to switch to descending" : "Descending — click to switch to ascending"}
          className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-stone-200 bg-white text-stone-500 transition-colors hover:border-stone-400 hover:text-stone-800"
        >
          <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" style={{ transform: asc ? "scaleY(-1)" : undefined }}>
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4M17 8v12m0 0l4-4m-4 4l-4-4" />
          </svg>
        </button>
        {SORT_OPTIONS.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => handleSort(key)}
            className={`rounded-full border px-3 py-1 text-xs font-medium transition-colors ${
              sort === key
                ? "border-stone-900 bg-stone-900 text-white"
                : "border-stone-200 bg-white text-stone-600 hover:border-stone-400"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Result count */}
      {query && (
        <p className="mb-3 text-sm text-stone-400">
          {results.length} result{results.length !== 1 ? "s" : ""}
        </p>
      )}

      {/* Cards */}
      {results.length === 0 ? (
        <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
          <p className="text-stone-500">No episodes match.</p>
        </div>
      ) : (
        <>
          <div className="flex flex-col gap-3">
            {pageItems.map((ep) => {
              const likeRatio =
                ep.view_count && ep.like_count != null && ep.view_count > 0
                  ? ((ep.like_count / ep.view_count) * 100).toFixed(1) + "%"
                  : null;
              return (
                <Link
                  key={ep.id}
                  href={`/killtony/episodes/${ep.id}`}
                  className="group flex items-center overflow-hidden rounded-xl border border-stone-200 bg-white transition-colors hover:border-stone-400"
                >
                  <YoutubeThumbnail
                    videoId={ep.youtube_id}
                    alt={ep.title || `Kill Tony #${ep.number}`}
                    className="w-36 shrink-0 aspect-video sm:w-52"
                  />
                  <div className="min-w-0 flex-1 px-4 py-3">
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0">
                        <span className="text-[11px] font-medium uppercase tracking-wide text-stone-400">
                          Episode {ep.number}
                        </span>
                        <p className="mt-0.5 truncate font-semibold leading-snug text-stone-900">
                          {ep.title || `Kill Tony #${ep.number}`}
                        </p>
                        <p className="mt-0.5 text-xs text-stone-400">{fmtDate(ep.date)}</p>
                      </div>
                      <svg
                        className="mt-1 h-4 w-4 shrink-0 text-stone-300 transition-colors group-hover:text-stone-500"
                        fill="none" stroke="currentColor" viewBox="0 0 24 24"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                    <div className="mt-3 flex flex-wrap gap-1.5">
                      <Stat label="Duration" value={fmtDuration(ep.duration_seconds)} />
                      <Stat label="Sets" value={ep.set_count} />
                      <Stat label="Bucket pulls" value={ep.bucket_pull_count} />
                      <Stat label="Golden tickets" value={ep.golden_ticket_count} />
                      <Stat label="Big joke books" value={ep.large_joke_book_count} />
                      <Stat label="Regulars" value={ep.regular_count} />
                      {ep.view_count != null && <Stat label="Views" value={fmt(ep.view_count)} />}
                      {ep.like_count != null && <Stat label="Likes" value={fmt(ep.like_count)} />}
                      {ep.comment_count != null && <Stat label="Comments" value={fmt(ep.comment_count)} />}
                      {likeRatio && <Stat label="View/like ratio" value={likeRatio} />}
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
          <Paginator page={page} totalPages={totalPages} onPage={setPage} />
        </>
      )}
    </div>
  );
}
