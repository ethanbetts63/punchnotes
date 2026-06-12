"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";

const JOKE_TYPES = [
  "misdirect", "reframe", "phonetic-match", "double-meaning",
  "contradiction", "analogy", "hyperbole", "elephant-in-the-room",
];

export default function JokesFilters() {
  const router = useRouter();
  const sp = useSearchParams();
  const currentType = sp.get("joke_type") ?? "";
  const currentQuery = sp.get("q") ?? "";
  const [query, setQuery] = useState(currentQuery);

  function navigate(type: string, nextQuery = currentQuery) {
    const params = new URLSearchParams();
    if (nextQuery.trim()) params.set("q", nextQuery.trim());
    if (type) params.set("joke_type", type);
    const qs = params.toString();
    router.push(`/killtony/jokes${qs ? `?${qs}` : ""}`);
  }

  return (
    <div className="mb-6 space-y-4">
      <form
        onSubmit={(event) => {
          event.preventDefault();
          navigate(currentType, query);
        }}
        className="flex items-center gap-2 rounded-xl border border-stone-200 px-3 py-2 transition-colors focus-within:border-stone-400"
      >
        <svg className="h-3.5 w-3.5 shrink-0 text-stone-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
        </svg>
        <input
          type="search"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search jokes..."
          className="flex-1 bg-transparent text-sm text-stone-900 placeholder-stone-400 focus:outline-none"
        />
        {currentQuery && (
          <button
            type="button"
            onClick={() => {
              setQuery("");
              navigate(currentType, "");
            }}
            className="text-xs text-stone-400 transition-colors hover:text-stone-600"
          >
            Clear x
          </button>
        )}
      </form>

      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => navigate("")}
          className={`rounded-full px-3 py-1 text-xs font-medium border transition-colors ${
            !currentType
              ? "bg-stone-900 text-white border-stone-900"
              : "bg-white text-stone-600 border-stone-200 hover:border-stone-400"
          }`}
        >
          All types
        </button>
        {JOKE_TYPES.map((jt) => (
          <button
            key={jt}
            onClick={() => navigate(jt)}
            className={`rounded-full px-3 py-1 text-xs font-medium border transition-colors ${
              currentType === jt
                ? "bg-primary text-white border-primary"
                : "bg-white text-stone-600 border-stone-200 hover:border-stone-400"
            }`}
          >
            {jt}
          </button>
        ))}
      </div>
    </div>
  );
}
