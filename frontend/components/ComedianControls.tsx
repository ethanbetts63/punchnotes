"use client";

import Link from "next/link";
import { useState, useMemo } from "react";
import type { Comedian } from "@/lib/serverApi";
import Paginator from "@/components/Paginator";

const PAGE_SIZE = 24;

type Props = { comedians: Comedian[] };

export default function ComedianControls({ comedians }: Props) {
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(1);

  const results = useMemo(() => {
    const q = query.trim().toLowerCase();
    return q ? comedians.filter((c) => c.name.toLowerCase().includes(q)) : comedians;
  }, [comedians, query]);

  const totalPages = Math.ceil(results.length / PAGE_SIZE);
  const pageItems = results.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  function handleQuery(q: string) { setQuery(q); setPage(1); }

  return (
    <div>
      <div className="mb-6 flex items-center gap-2 rounded-xl border border-stone-200 px-3 py-2 transition-colors focus-within:border-stone-400">
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

      {query && (
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
                <p className="font-semibold text-stone-900 transition-colors group-hover:text-primary">
                  {c.name}
                </p>
                <p className="mt-1 text-sm text-stone-400">
                  {c.appearances} appearance{c.appearances !== 1 ? "s" : ""} · {c.set_count} set{c.set_count !== 1 ? "s" : ""}
                </p>
              </Link>
            ))}
          </div>
          <Paginator page={page} totalPages={totalPages} onPage={setPage} />
        </>
      )}
    </div>
  );
}
