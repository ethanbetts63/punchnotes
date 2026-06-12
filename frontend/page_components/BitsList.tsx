"use client";

import Link from "next/link";
import type { BitListItem } from "@/lib/serverApi";
import { useUrlPagination } from "@/lib/useUrlPagination";
import { Badge } from "@/components/ui/badge";
import Paginator from "@/components/Paginator";
import { buildBitSetHref } from "@/lib/bitLinks";

const PAGE_SIZE = 20;

type Props = { bits: BitListItem[]; filterKey?: string };

export default function BitsList({ bits }: Props) {
  const { page, totalPages, setPage } = useUrlPagination(bits.length, PAGE_SIZE);
  const pageItems = bits.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  if (bits.length === 0) {
    return (
      <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
        <p className="text-stone-500">No jokes found.</p>
      </div>
    );
  }

  return (
    <>
      <div className="space-y-3">
        {pageItems.map((bit) => (
          <Link
            key={bit.id}
            href={buildBitSetHref(bit)}
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
            </div>

            {(bit.summary ?? bit.beats_summary[0]?.premise) && (
              <p className="mb-3 text-sm italic text-stone-500">
                &ldquo;{bit.summary ?? bit.beats_summary[0]?.premise}&rdquo;
              </p>
            )}
          </Link>
        ))}
      </div>
      <Paginator page={page} totalPages={totalPages} onPage={setPage} />
    </>
  );
}
