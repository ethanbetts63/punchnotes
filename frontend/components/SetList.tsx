"use client";

import Link from "next/link";
import { useState, useMemo } from "react";
import type { ComedianAttribute, SetListItem } from "@/lib/serverApi";
import Paginator from "@/components/Paginator";
import SetImage from "@/components/SetImage";

const PAGE_SIZE = 20;

type SortKey = "episode" | "comedian" | "bit_count" | "hit_ratio" | "punchline_tag_ratio" | "start_seconds";

const SORT_OPTIONS: { key: SortKey; label: string }[] = [
  { key: "episode",             label: "Episode" },
  { key: "comedian",            label: "Comedian" },
  { key: "bit_count",           label: "Bits" },
  { key: "hit_ratio",           label: "Setup/punch ratio" },
  { key: "punchline_tag_ratio", label: "Punch/tag ratio" },
  { key: "start_seconds",       label: "Start time" },
];

const ATTRIBUTE_LABELS: Record<string, string> = {
  bucket_pull: "Bucket Pull", regular: "Regular", golden_ticket: "Golden Ticket",
  special: "Special", gay: "Gay", lesbian: "Lesbian", bisexual: "Bisexual",
  man: "Man", woman: "Woman", trans: "Trans", white: "White", black: "Black",
  asian: "Asian", latino: "Latino", middle_eastern: "Middle Eastern",
  disabled: "Disabled", old: "Old", young: "Young", "middle-age": "Middle-Age",
};

const jokeBookColor: Record<string, string> = {
  small: "bg-stone-100 text-stone-600",
  medium: "bg-amber-100 text-amber-700",
  large: "bg-red-100 text-primary",
};

const jokeBookLabel: Record<string, string> = {
  small: "Small Joke Book",
  medium: "Medium Joke Book",
  large: "Large Joke Book",
};

function fmt2(n: number | null): string {
  return n == null ? "-" : n.toFixed(2);
}

function fmtSeconds(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  return `${m}:${String(s).padStart(2, "0")}`;
}

function getSortValue(set: SetListItem, key: SortKey): number | string {
  switch (key) {
    case "episode":             return set.episode.number;
    case "comedian":            return set.comedian.name.toLowerCase();
    case "bit_count":           return set.bit_count;
    case "hit_ratio":           return set.hit_ratio ?? -1;
    case "punchline_tag_ratio": return set.punchline_tag_ratio ?? -1;
    case "start_seconds":       return set.start_seconds;
  }
}

type Props = { sets: SetListItem[]; filterKey?: string };

export default function SetList({ sets, filterKey }: Props) {
  const [sort, setSort] = useState<SortKey>("episode");
  const [asc, setAsc] = useState(false);
  const [page, setPage] = useState(1);

  const [prevKey, setPrevKey] = useState(filterKey);
  if (filterKey !== prevKey) { setPrevKey(filterKey); setPage(1); }

  function handleSort(key: SortKey) {
    if (key === sort) setAsc((v) => !v);
    else { setSort(key); setAsc(key === "comedian" || key === "start_seconds"); }
    setPage(1);
  }

  const sorted = useMemo(() => (
    [...sets].sort((a, b) => {
      const va = getSortValue(a, sort);
      const vb = getSortValue(b, sort);
      const cmp = typeof va === "string" ? va.localeCompare(vb as string) : (va as number) - (vb as number);
      return asc ? cmp : -cmp;
    })
  ), [sets, sort, asc]);

  const totalPages = Math.ceil(sorted.length / PAGE_SIZE);
  const pageItems = sorted.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  const chip = (active: boolean) =>
    `rounded-full border px-3 py-1 text-xs font-medium transition-colors ${
      active
        ? "border-stone-900 bg-stone-900 text-white"
        : "border-stone-200 bg-white text-stone-600 hover:border-stone-400"
    }`;

  return (
    <>
      <div className="mb-6 flex flex-wrap items-center gap-2">
        <button
          onClick={() => { setAsc((v) => !v); setPage(1); }}
          title={asc ? "Ascending" : "Descending"}
          className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-stone-200 bg-white text-stone-500 transition-colors hover:border-stone-400 hover:text-stone-800"
        >
          <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" style={{ transform: asc ? "scaleY(-1)" : undefined }}>
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4M17 8v12m0 0l4-4m-4 4l-4-4" />
          </svg>
        </button>
        {SORT_OPTIONS.map(({ key, label }) => (
          <button key={key} onClick={() => handleSort(key)} className={chip(sort === key)}>
            {label}
          </button>
        ))}
      </div>

      <div className="flex flex-col gap-3">
        {pageItems.map((set) => (
          <Link
            key={set.id}
            href={`/killtony/sets/${set.id}`}
            className="group flex overflow-hidden rounded-xl border border-stone-200 bg-white transition-colors hover:border-primary/40 hover:shadow-sm"
          >
            <SetImage
              imageUrl={set.image_url}
              fallbackVideoId={set.episode.youtube_id}
              alt={`${set.comedian.name} set image`}
              className="hidden w-32 shrink-0 bg-stone-950 sm:block"
            />
            <div className="min-w-0 flex-1 p-4">
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <p className="text-xs font-bold uppercase tracking-wide text-stone-400">
                    KT #{set.episode.number} / Set {set.set_number} / {fmtSeconds(set.start_seconds)}
                  </p>
                  <p className="mt-1 truncate text-lg font-bold leading-tight text-stone-900 transition-colors group-hover:text-primary">
                    {set.comedian.name}
                  </p>
                  <p className="mt-1 truncate text-sm text-stone-500">{set.episode.title}</p>
                </div>
                {set.joke_book_award && (
                  <span className={`shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium ${jokeBookColor[set.joke_book_award]}`}>
                    {jokeBookLabel[set.joke_book_award]}
                  </span>
                )}
              </div>
              <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-stone-500">
                <span><span className="font-bold text-stone-800">{set.bit_count}</span> bits</span>
                <span>Setup/punch <span className="font-bold text-stone-800">{fmt2(set.hit_ratio)}</span></span>
                <span>Punch/tag <span className="font-bold text-stone-800">{fmt2(set.punchline_tag_ratio)}</span></span>
              </div>
              {set.comedian.attributes.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {(set.comedian.attributes as string[])
                    .filter((attr) => attr in ATTRIBUTE_LABELS)
                    .map((attr) => (
                      <span key={attr} className="rounded-full bg-stone-100 px-2 py-0.5 text-[10px] font-medium text-stone-500">
                        {ATTRIBUTE_LABELS[attr]}
                      </span>
                    ))}
                </div>
              )}
            </div>
          </Link>
        ))}
      </div>
      <Paginator page={page} totalPages={totalPages} onPage={setPage} />
    </>
  );
}
