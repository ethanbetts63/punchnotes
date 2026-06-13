"use client";

import { useRouter, useSearchParams } from "next/navigation";
import type { ReactNode } from "react";

type FilterParams = Record<string, string>;

export type ListPageFilterOption = {
  value: string;
  label: string;
};

type UseListPageFilterRouterOptions = {
  searchPath: string;
  trackedParams: string[];
};

export function useListPageFilterRouter({ searchPath, trackedParams }: UseListPageFilterRouterOptions) {
  const router = useRouter();
  const searchParams = useSearchParams();

  function getParam(name: string, fallback = ""): string {
    return searchParams.get(name) ?? fallback;
  }

  function push(overrides: FilterParams) {
    const params = new URLSearchParams();
    const query = getParam("q").trim();
    if (query) params.set("q", query);

    for (const param of trackedParams) {
      const value = getParam(param);
      if (value) params.set(param, value);
    }

    for (const [key, value] of Object.entries(overrides)) {
      if (value) params.set(key, value);
      else params.delete(key);
    }

    const qs = params.toString();
    router.push(`${searchPath}${qs ? `?${qs}` : ""}`);
  }

  return { getParam, push };
}

function chipClass(active: boolean): string {
  return `rounded-full border px-3 py-1.5 text-xs font-medium text-center transition-colors ${
    active
      ? "border-stone-900 bg-stone-900 text-white"
      : "border-stone-200 bg-white text-stone-600 hover:border-stone-400"
  }`;
}

export function ListPageFilterSection({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div>
      <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-stone-400">{title}</p>
      {children}
    </div>
  );
}

export function ListPageFilterChipGrid({
  options,
  currentValue,
  onSelect,
}: {
  options: ListPageFilterOption[];
  currentValue: string;
  onSelect: (value: string) => void;
}) {
  return (
    <div className="grid gap-2 [grid-template-columns:repeat(auto-fit,minmax(150px,1fr))]">
      {options.map(({ value, label }) => (
        <button
          key={value}
          onClick={() => onSelect(value)}
          className={chipClass(currentValue === value)}
        >
          {label}
        </button>
      ))}
    </div>
  );
}

export function ListPageSortChipGrid({
  options,
  currentValue,
  onSelect,
  currentAsc,
  onToggleAsc,
}: {
  options: ListPageFilterOption[];
  currentValue: string;
  onSelect: (value: string) => void;
  currentAsc: boolean;
  onToggleAsc: () => void;
}) {
  return (
    <div className="flex items-start gap-2">
      <button
        onClick={onToggleAsc}
        title={currentAsc ? "Ascending - click for descending" : "Descending - click for ascending"}
        className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-stone-200 bg-white text-stone-500 transition-colors hover:border-stone-400 hover:text-stone-800"
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
      <div className="grid flex-1 gap-2 [grid-template-columns:repeat(auto-fit,minmax(150px,1fr))]">
        {options.map(({ value, label }) => (
          <button
            key={value}
            onClick={() => onSelect(value)}
            className={chipClass(currentValue === value)}
          >
            {label}
          </button>
        ))}
      </div>
    </div>
  );
}
