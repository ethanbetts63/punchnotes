"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

type Props = { placeholder: string };

export default function BrowseSearchBar({ placeholder }: Props) {
  const router = useRouter();
  const sp = useSearchParams();
  const urlQuery = sp.get("q") ?? "";
  const [value, setValue] = useState(urlQuery);

  useEffect(() => { setValue(urlQuery); }, [urlQuery]);

  function navigate(q: string) {
    const params = new URLSearchParams(sp.toString());
    if (q.trim()) params.set("q", q.trim());
    else params.delete("q");
    const qs = params.toString();
    router.push(`${window.location.pathname}${qs ? `?${qs}` : ""}`);
  }

  return (
    <form
      onSubmit={(e) => { e.preventDefault(); navigate(value); }}
      className="mb-8 flex items-center gap-2 rounded-xl border border-stone-200 px-3 py-2.5 transition-colors focus-within:border-stone-400"
    >
      <svg className="h-3.5 w-3.5 shrink-0 text-stone-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
      </svg>
      <input
        type="search"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder={placeholder}
        className="flex-1 bg-transparent text-sm text-stone-900 placeholder-stone-400 focus:outline-none"
      />
      {urlQuery && (
        <button
          type="button"
          onClick={() => { setValue(""); navigate(""); }}
          className="text-xs text-stone-400 transition-colors hover:text-stone-600"
        >
          Clear ×
        </button>
      )}
    </form>
  );
}
