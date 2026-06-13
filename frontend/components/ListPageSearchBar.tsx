"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";

type Props = { placeholder: string; searchPath?: string };

export default function ListPageSearchBar({ placeholder, searchPath }: Props) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const urlQuery = searchParams.get("q") ?? "";
  const [value, setValue] = useState(urlQuery);

  function navigate(query: string) {
    if (searchPath) {
      const params = new URLSearchParams();
      if (query.trim()) params.set("q", query.trim());
      const qs = params.toString();
      router.push(`${searchPath}${qs ? `?${qs}` : ""}`);
      return;
    }

    const params = new URLSearchParams(searchParams.toString());
    if (query.trim()) params.set("q", query.trim());
    else params.delete("q");
    const qs = params.toString();
    router.push(`${window.location.pathname}${qs ? `?${qs}` : ""}`);
  }

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        navigate(value);
      }}
      className="mb-6 flex items-center gap-2 rounded-xl border border-stone-200 px-3 py-2.5 transition-colors focus-within:border-stone-400"
    >
      <svg className="h-3.5 w-3.5 shrink-0 text-stone-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z"
        />
      </svg>
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder={placeholder}
        className="flex-1 bg-transparent text-sm text-stone-900 placeholder-stone-400 focus:outline-none"
      />
    </form>
  );
}
