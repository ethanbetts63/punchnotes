"use client";

import { useRouter, useSearchParams } from "next/navigation";

const SEARCH_PATH = "/killtony/bits/search";

const JOKE_TYPE_OPTIONS = [
  "misdirect", "reframe", "phonetic-match", "double-meaning", "contradiction", "what-if",
  "analogy", "hyperbole", "act-out", "elephant-in-the-room", "prop",
];

const SORT_OPTIONS = [
  { key: "hit_ratio",           label: "Hit ratio" },
  { key: "punchline_tag_ratio", label: "Punch/tag ratio" },
];

export default function BitSearchFilters() {
  const router = useRouter();
  const sp = useSearchParams();
  const currentType = sp.get("joke_type") ?? "";
  const currentSort = sp.get("sort") ?? "";
  const currentAsc = sp.get("asc") === "1";
  const currentQ = sp.get("q") ?? "";

  function build(overrides: Record<string, string>) {
    const params = new URLSearchParams();
    if (currentQ) params.set("q", currentQ);
    if (currentType) params.set("joke_type", currentType);
    if (currentSort) params.set("sort", currentSort);
    if (currentAsc) params.set("asc", "1");
    for (const [k, v] of Object.entries(overrides)) {
      if (v) params.set(k, v);
      else params.delete(k);
    }
    return `${SEARCH_PATH}?${params.toString()}`;
  }

  const chip = (active: boolean) =>
    `rounded-full border px-3 py-1 text-xs font-medium transition-colors ${
      active
        ? "border-stone-900 bg-stone-900 text-white"
        : "border-stone-200 bg-white text-stone-600 hover:border-stone-400"
    }`;

  return (
    <div className="mb-6 space-y-4">
      <div>
        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-stone-400">Filter by joke type</p>
        <div className="flex flex-wrap gap-2">
          {JOKE_TYPE_OPTIONS.map((jt) => (
            <button
              key={jt}
              onClick={() => router.push(build({ joke_type: currentType === jt ? "" : jt }))}
              className={chip(currentType === jt)}
            >
              {jt}
            </button>
          ))}
        </div>
      </div>
      <div>
        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-stone-400">Sort</p>
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => router.push(build({ asc: currentAsc ? "" : "1" }))}
            title={currentAsc ? "Ascending — click for descending" : "Descending — click for ascending"}
            className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-stone-200 bg-white text-stone-500 transition-colors hover:border-stone-400 hover:text-stone-800"
          >
            <svg
              className="h-3.5 w-3.5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              style={{ transform: currentAsc ? "scaleY(-1)" : undefined }}
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V4m0 0L3 8m4-4l4 4M17 8v12m0 0l4-4m-4 4l-4-4" />
            </svg>
          </button>
          {SORT_OPTIONS.map(({ key, label }) => (
            <button
              key={key}
              onClick={() => router.push(build({ sort: currentSort === key ? "" : key }))}
              className={chip(currentSort === key)}
            >
              {label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
