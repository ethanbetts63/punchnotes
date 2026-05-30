"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import type { ComedianAttribute, SetListItem } from "@/lib/serverApi";
import Paginator from "@/components/Paginator";
import SetImage from "@/components/SetImage";

const PAGE_SIZE = 20;

type SortKey =
  | "episode"
  | "comedian"
  | "bit_count"
  | "hit_ratio"
  | "punchline_tag_ratio"
  | "start_seconds";

const SORT_OPTIONS: { key: SortKey; label: string }[] = [
  { key: "episode", label: "Episode" },
  { key: "comedian", label: "Comedian" },
  { key: "bit_count", label: "Bits" },
  { key: "hit_ratio", label: "Setup/punch ratio" },
  { key: "punchline_tag_ratio", label: "Punch/tag ratio" },
  { key: "start_seconds", label: "Start time" },
];

const TYPE_OPTIONS: { value: ComedianAttribute | ""; label: string }[] = [
  { value: "", label: "All types" },
  { value: "bucket_pull", label: "Bucket Pull" },
  { value: "regular", label: "Regular" },
  { value: "golden_ticket", label: "Golden Ticket" },
  { value: "special", label: "Special" },
];

const ATTRIBUTE_OPTIONS: { value: ComedianAttribute; label: string }[] = [
  { value: "bucket_pull", label: "Bucket Pull" },
  { value: "regular", label: "Regular" },
  { value: "golden_ticket", label: "Golden Ticket" },
  { value: "special", label: "Special" },
  { value: "gay", label: "Gay" },
  { value: "lesbian", label: "Lesbian" },
  { value: "bisexual", label: "Bisexual" },
  { value: "man", label: "Man" },
  { value: "woman", label: "Woman" },
  { value: "trans", label: "Trans" },
  { value: "white", label: "White" },
  { value: "black", label: "Black" },
  { value: "asian", label: "Asian" },
  { value: "latino", label: "Latino" },
  { value: "middle_eastern", label: "Middle Eastern" },
  { value: "disabled", label: "Disabled" },
  { value: "old", label: "Old" },
  { value: "young", label: "Young" },
  { value: "middle-age", label: "Middle-Age" },
];

const ATTRIBUTE_LABELS = new Map(ATTRIBUTE_OPTIONS.map(({ value, label }) => [value, label]));

const JOKE_BOOK_OPTIONS: { value: "small" | "medium" | "large"; label: string }[] = [
  { value: "small", label: "Small Joke Book" },
  { value: "medium", label: "Medium Joke Book" },
  { value: "large", label: "Large Joke Book" },
];

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
    case "episode":
      return set.episode.number;
    case "comedian":
      return set.comedian.name.toLowerCase();
    case "bit_count":
      return set.bit_count;
    case "hit_ratio":
      return set.hit_ratio ?? -1;
    case "punchline_tag_ratio":
      return set.punchline_tag_ratio ?? -1;
    case "start_seconds":
      return set.start_seconds;
  }
}

type Props = {
  sets: SetListItem[];
  initialQuery?: string;
  hideSearch?: boolean;
  children?: React.ReactNode;
};

export default function SetControls({ sets, initialQuery = "", hideSearch = false, children }: Props) {
  const [query, setQuery] = useState(initialQuery);
  const [typeFilter, setTypeFilter] = useState<ComedianAttribute | "">("");
  const [attributeFilters, setAttributeFilters] = useState<Set<ComedianAttribute>>(new Set());
  const [jokeBooks, setJokeBooks] = useState<Set<string>>(new Set());
  const [sort, setSort] = useState<SortKey>("episode");
  const [asc, setAsc] = useState(false);
  const [page, setPage] = useState(1);

  function handleQuery(q: string) {
    setQuery(q);
    setPage(1);
  }

  function handleType(v: ComedianAttribute | "") {
    setTypeFilter(v);
    setPage(1);
  }

  function handleSort(key: SortKey) {
    if (key === sort) setAsc((value) => !value);
    else {
      setSort(key);
      setAsc(key === "comedian" || key === "start_seconds");
    }
    setPage(1);
  }

  function toggleAttribute(value: ComedianAttribute) {
    setAttributeFilters((prev) => {
      const next = new Set(prev);
      if (next.has(value)) next.delete(value);
      else next.add(value);
      return next;
    });
    setPage(1);
  }

  function toggleJokeBook(value: string) {
    setJokeBooks((prev) => {
      const next = new Set(prev);
      if (next.has(value)) next.delete(value);
      else next.add(value);
      return next;
    });
    setPage(1);
  }

  const results = useMemo(() => {
    let list = sets;

    if (typeFilter) list = list.filter((set) => set.comedian.attributes.includes(typeFilter));

    if (attributeFilters.size > 0) {
      list = list.filter((set) =>
        [...attributeFilters].every((attr) => set.comedian.attributes.includes(attr))
      );
    }

    if (jokeBooks.size > 0) {
      list = list.filter((set) => set.joke_book_award != null && jokeBooks.has(set.joke_book_award));
    }

    if (query.trim()) {
      const q = query.trim().toLowerCase();
      list = list.filter((set) =>
        set.comedian.name.toLowerCase().includes(q) ||
        set.episode.title.toLowerCase().includes(q) ||
        String(set.episode.number).includes(q)
      );
    }

    return [...list].sort((a, b) => {
      const va = getSortValue(a, sort);
      const vb = getSortValue(b, sort);
      const cmp = typeof va === "string"
        ? va.localeCompare(vb as string)
        : (va as number) - (vb as number);
      return asc ? cmp : -cmp;
    });
  }, [sets, query, typeFilter, attributeFilters, jokeBooks, sort, asc]);

  const totalPages = Math.ceil(results.length / PAGE_SIZE);
  const pageItems = results.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  const chip = (active: boolean) =>
    `rounded-full border px-3 py-1 text-xs font-medium transition-colors ${
      active
        ? "border-stone-900 bg-stone-900 text-white"
        : "border-stone-200 bg-white text-stone-600 hover:border-stone-400"
    }`;

  return (
    <div>
      {!hideSearch && (
        <div className="mb-4 flex items-center gap-2 rounded-xl border border-stone-200 px-3 py-2 transition-colors focus-within:border-stone-400">
          <svg className="h-3.5 w-3.5 shrink-0 text-stone-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
          </svg>
          <input
            type="text"
            value={query}
            onChange={(event) => handleQuery(event.target.value)}
            placeholder={`Search ${sets.length} sets...`}
            className="flex-1 bg-transparent text-sm text-stone-900 placeholder-stone-400 focus:outline-none"
          />
          {query && (
            <button onClick={() => handleQuery("")} className="text-xs text-stone-400 transition-colors hover:text-stone-600">
              Clear x
            </button>
          )}
        </div>
      )}

      <div className="mb-3 flex flex-wrap gap-2">
        {TYPE_OPTIONS.map(({ value, label }) => (
          <button key={value} onClick={() => handleType(value)} className={chip(typeFilter === value)}>
            {label}
          </button>
        ))}
      </div>

      <div className="mb-3 flex flex-wrap gap-2">
        {ATTRIBUTE_OPTIONS.map(({ value, label }) => (
          <button key={value} onClick={() => toggleAttribute(value)} className={chip(attributeFilters.has(value))}>
            {label}
          </button>
        ))}
      </div>

      <div className="mb-4 flex flex-wrap gap-2">
        {JOKE_BOOK_OPTIONS.map(({ value, label }) => (
          <button key={value} onClick={() => toggleJokeBook(value)} className={chip(jokeBooks.has(value))}>
            {label}
          </button>
        ))}
      </div>

      <div className="mb-6 flex flex-wrap items-center gap-2">
        <button
          onClick={() => setAsc((value) => !value)}
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

      {query.trim() ? (
        <>
          <p className="mb-3 text-sm text-stone-400">
            {results.length} result{results.length !== 1 ? "s" : ""}
          </p>
          {results.length === 0 ? (
            <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
              <p className="text-stone-500">No sets match.</p>
            </div>
          ) : (
            <>
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
                      {set.comedian.attributes
                        .filter((attr): attr is ComedianAttribute => ATTRIBUTE_LABELS.has(attr as ComedianAttribute))
                        .map((attr) => (
                          <span key={attr} className="rounded-full bg-stone-100 px-2 py-0.5 text-[10px] font-medium text-stone-500">
                            {ATTRIBUTE_LABELS.get(attr)}
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
          )}
        </>
      ) : (
        children
      )}
    </div>
  );
}
