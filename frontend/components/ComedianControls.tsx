"use client";

import Link from "next/link";
import { useState, useMemo } from "react";
import type { Comedian, ComedianType } from "@/lib/serverApi";
import Paginator from "@/components/Paginator";

const PAGE_SIZE = 24;

type SortKey = "name" | "set_count" | "avg_bits_per_set" | "avg_beats_per_set" | "avg_hit_ratio" | "avg_punchline_tag_ratio";

const SORT_OPTIONS: { key: SortKey; label: string }[] = [
  { key: "name",                    label: "Name" },
  { key: "set_count",               label: "Sets" },
  { key: "avg_bits_per_set",        label: "Bits/set" },
  { key: "avg_beats_per_set",       label: "Beats/set" },
  { key: "avg_hit_ratio",           label: "Setup/punch ratio" },
  { key: "avg_punchline_tag_ratio", label: "Punch/tag ratio" },
];

const TYPE_OPTIONS: { value: ComedianType | ""; label: string }[] = [
  { value: "",               label: "All types" },
  { value: "bucket_pull",    label: "Bucket Pull" },
  { value: "regular",        label: "Regular" },
  { value: "golden_ticket",  label: "Golden Ticket" },
  { value: "special",        label: "Special" },
];

const JOKE_BOOK_OPTIONS: { key: "has_small_joke_book" | "has_medium_joke_book" | "has_large_joke_book"; label: string }[] = [
  { key: "has_small_joke_book",  label: "Small Joke Book" },
  { key: "has_medium_joke_book", label: "Medium Joke Book" },
  { key: "has_large_joke_book",  label: "Large Joke Book" },
];

function getSortValue(c: Comedian, key: SortKey): number | string {
  switch (key) {
    case "name":                    return c.name.toLowerCase();
    case "set_count":               return c.set_count;
    case "avg_bits_per_set":        return c.avg_bits_per_set ?? -1;
    case "avg_beats_per_set":       return c.avg_beats_per_set ?? -1;
    case "avg_hit_ratio":           return c.avg_hit_ratio ?? -1;
    case "avg_punchline_tag_ratio": return c.avg_punchline_tag_ratio ?? -1;
  }
}

function fmt2(n: number | null): string {
  if (n == null) return "—";
  return n.toFixed(2);
}

type Props = { comedians: Comedian[] };

export default function ComedianControls({ comedians }: Props) {
  const [query, setQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState<ComedianType | "">("");
  const [jokeBooks, setJokeBooks] = useState<Set<string>>(new Set());
  const [sort, setSort] = useState<SortKey>("name");
  const [asc, setAsc] = useState(true);
  const [page, setPage] = useState(1);

  function handleQuery(q: string) { setQuery(q); setPage(1); }
  function handleType(v: ComedianType | "") { setTypeFilter(v); setPage(1); }
  function handleSort(key: SortKey) {
    if (key === sort) { setAsc((v) => !v); }
    else { setSort(key); setAsc(key === "name"); }
    setPage(1);
  }
  function toggleJokeBook(key: string) {
    setJokeBooks((prev) => {
      const next = new Set(prev);
      next.has(key) ? next.delete(key) : next.add(key);
      return next;
    });
    setPage(1);
  }

  const results = useMemo(() => {
    let list = comedians;

    if (typeFilter) list = list.filter((c) => c.comedian_type === typeFilter);

    if (jokeBooks.size > 0) {
      list = list.filter((c) =>
        [...jokeBooks].some((k) => c[k as keyof Comedian] === true)
      );
    }

    if (query.trim()) {
      const q = query.trim().toLowerCase();
      list = list.filter((c) => c.name.toLowerCase().includes(q));
    }

    return [...list].sort((a, b) => {
      const va = getSortValue(a, sort);
      const vb = getSortValue(b, sort);
      const cmp = typeof va === "string"
        ? va.localeCompare(vb as string)
        : (va as number) - (vb as number);
      return asc ? cmp : -cmp;
    });
  }, [comedians, query, typeFilter, jokeBooks, sort, asc]);

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
      {/* Search */}
      <div className="mb-4 flex items-center gap-2 rounded-xl border border-stone-200 px-3 py-2 transition-colors focus-within:border-stone-400">
        <svg className="h-3.5 w-3.5 shrink-0 text-stone-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
        </svg>
        <input
          type="text"
          value={query}
          onChange={(e) => handleQuery(e.target.value)}
          placeholder={`Search ${comedians.length} comedians…`}
          className="flex-1 bg-transparent text-sm text-stone-900 placeholder-stone-400 focus:outline-none"
        />
        {query && (
          <button onClick={() => handleQuery("")} className="text-xs text-stone-400 transition-colors hover:text-stone-600">
            Clear ×
          </button>
        )}
      </div>

      {/* Comedian type filter */}
      <div className="mb-3 flex flex-wrap gap-2">
        {TYPE_OPTIONS.map(({ value, label }) => (
          <button key={value} onClick={() => handleType(value)} className={chip(typeFilter === value)}>
            {label}
          </button>
        ))}
      </div>

      {/* Joke book filter */}
      <div className="mb-4 flex flex-wrap gap-2">
        {JOKE_BOOK_OPTIONS.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => toggleJokeBook(key)}
            className={chip(jokeBooks.has(key))}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Sort */}
      <div className="mb-6 flex flex-wrap items-center gap-2">
        <button
          onClick={() => setAsc((v) => !v)}
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

      {query.trim() && (
        <p className="mb-3 text-sm text-stone-400">
          {results.length} result{results.length !== 1 ? "s" : ""}
        </p>
      )}

      {results.length === 0 ? (
        <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
          <p className="text-stone-500">No comedians match.</p>
        </div>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2">
            {pageItems.map((c) => (
              <Link
                key={c.id}
                href={`/killtony/comedians/${c.slug}`}
                className="group rounded-xl border border-stone-200 bg-white p-5 transition-all hover:border-primary/40 hover:shadow-sm"
              >
                <p className="font-semibold text-stone-900 transition-colors group-hover:text-primary truncate">
                  {c.name}
                </p>
                <p className="mt-1 text-sm text-stone-400">
                  {c.appearances} ep{c.appearances !== 1 ? "s" : ""} · {c.set_count} set{c.set_count !== 1 ? "s" : ""}
                  {c.avg_bits_per_set != null && <> · <span className="font-medium">{fmt2(c.avg_bits_per_set)}</span> bits/set</>}
                  {c.avg_beats_per_set != null && <> · <span className="font-medium">{fmt2(c.avg_beats_per_set)}</span> beats/set</>}
                </p>
                {(c.avg_hit_ratio != null || c.avg_punchline_tag_ratio != null) && (
                  <p className="mt-1 text-xs text-stone-400">
                    {c.avg_hit_ratio != null && <>Setup/punch: <span className="font-medium text-stone-600">{fmt2(c.avg_hit_ratio)}</span></>}
                    {c.avg_hit_ratio != null && c.avg_punchline_tag_ratio != null && <span className="mx-1.5 text-stone-300">·</span>}
                    {c.avg_punchline_tag_ratio != null && <>Punch/tag: <span className="font-medium text-stone-600">{fmt2(c.avg_punchline_tag_ratio)}</span></>}
                  </p>
                )}
                {(c.has_small_joke_book || c.has_medium_joke_book || c.has_large_joke_book) && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {c.has_small_joke_book && <span className="rounded-full bg-stone-100 px-2 py-0.5 text-[10px] font-medium text-stone-500">Small Joke Book</span>}
                    {c.has_medium_joke_book && <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-medium text-amber-700">Medium Joke Book</span>}
                    {c.has_large_joke_book && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-primary">Large Joke Book</span>}
                  </div>
                )}
              </Link>
            ))}
          </div>
          <Paginator page={page} totalPages={totalPages} onPage={setPage} />
        </>
      )}
    </div>
  );
}
