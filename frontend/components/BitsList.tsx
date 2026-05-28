"use client";

import Link from "next/link";
import { useState } from "react";
import type { BitListItem } from "@/lib/serverApi";
import { Badge } from "@/components/ui/badge";
import Paginator from "@/components/Paginator";

const PAGE_SIZE = 20;

type Props = { bits: BitListItem[]; filterKey?: string };

export default function BitsList({ bits, filterKey }: Props) {
  const [page, setPage] = useState(1);

  const [prevKey, setPrevKey] = useState(filterKey);
  if (filterKey !== prevKey) { setPrevKey(filterKey); setPage(1); }

  const totalPages = Math.ceil(bits.length / PAGE_SIZE);
  const pageItems = bits.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  if (bits.length === 0) {
    return (
      <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
        <p className="text-stone-500">No bits found.</p>
      </div>
    );
  }

  return (
    <>
      <div className="space-y-3">
        {pageItems.map((bit) => (
          <Link
            key={bit.id}
            href={`/killtony/sets/${bit.set_id}`}
            className="group block rounded-xl border border-stone-200 bg-white p-5 transition-all hover:border-primary/40 hover:shadow-sm"
          >
            <div className="mb-3 flex flex-wrap items-center gap-2">
              <span className="text-sm font-semibold text-stone-900 transition-colors group-hover:text-primary">
                {bit.comedian}
              </span>
              <span className="text-stone-300">·</span>
              <span className="text-xs text-stone-400">Ep {bit.episode_number}</span>
              {bit.joke_types.map((jt) => (
                <Badge key={jt} variant="default">{jt}</Badge>
              ))}
              {bit.topics.map((t) => (
                <Badge key={t} variant="stone">{t}</Badge>
              ))}
            </div>

            {bit.premise && (
              <p className="mb-3 text-sm italic text-stone-500">"{bit.premise}"</p>
            )}

            {bit.beats_summary.length > 0 && (
              <div className="space-y-1">
                {bit.beats_summary.map((beat, i) => (
                  <p key={i} className="text-sm text-stone-600">"{beat.premise}"</p>
                ))}
              </div>
            )}
          </Link>
        ))}
      </div>
      <Paginator page={page} totalPages={totalPages} onPage={setPage} />
    </>
  );
}
