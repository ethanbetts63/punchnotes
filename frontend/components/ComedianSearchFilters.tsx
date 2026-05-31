"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { ATTRIBUTE_LABELS } from "@/lib/attributes";

const SEARCH_PATH = "/killtony/comedians/search";

const ALL_ATTRIBUTES = Object.entries(ATTRIBUTE_LABELS).map(([value, label]) => ({ value, label }));

const SORT_OPTIONS = [
  { key: "appearances",             label: "Appearances" },
  { key: "avg_hit_ratio",           label: "Hit ratio" },
  { key: "avg_punchline_tag_ratio", label: "Punch/tag ratio" },
  { key: "avg_bits_per_set",        label: "Bits per set" },
  { key: "avg_beats_per_set",       label: "Beats per set" },
];

export default function ComedianSearchFilters() {
  const router = useRouter();
  const sp = useSearchParams();
  const currentAttribute = sp.get("attribute") ?? "";
  const currentSort = sp.get("sort") ?? "";
  const currentAsc = sp.get("asc") === "1";
  const currentQ = sp.get("q") ?? "";

  function build(overrides: Record<string, string>) {
    const params = new URLSearchParams();
    if (currentQ) params.set("q", currentQ);
    if (currentAttribute) params.set("attribute", currentAttribute);
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
        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-stone-400">Filter</p>
        <div className="flex flex-wrap gap-2">
          {ALL_ATTRIBUTES.map(({ value, label }) => (
            <button
              key={value}
              onClick={() => router.push(build({ attribute: currentAttribute === value ? "" : value }))}
              className={chip(currentAttribute === value)}
            >
              {label}
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
