"use client";

import Link from "next/link";
import type { Comedian } from "@/lib/serverApi";
import { ATTRIBUTE_LABELS } from "@/lib/attributes";
import { fmt2 } from "@/lib/killTonyDisplay";
import { useUrlPagination } from "@/lib/useUrlPagination";
import Paginator from "@/components/Paginator";
import ComedianImage from "@/components/ComedianImage";

const PAGE_SIZE = 24;

export default function ComedianSearchResults({ comedians }: { comedians: Comedian[] }) {
  const { page, totalPages, setPage } = useUrlPagination(comedians.length, PAGE_SIZE);
  const pageItems = comedians.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  return (
    <>
      <div className="grid gap-4 sm:grid-cols-2">
        {pageItems.map((c) => (
          <Link
            key={c.id}
            href={`/killtony/comedians/${c.slug}`}
            className="group flex overflow-hidden rounded-xl border border-stone-200 bg-white transition-all hover:border-primary/40 hover:shadow-sm"
          >
            <ComedianImage imageUrl={c.image_url} name={c.name} className="w-28 shrink-0" />
            <div className="min-w-0 flex-1 p-5">
              <p className="truncate font-semibold text-stone-900 transition-colors group-hover:text-primary">
                {c.name}
              </p>
              <p className="mt-1 text-sm text-stone-400">
                {c.set_count} set{c.set_count !== 1 ? "s" : ""}
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
              {c.attributes.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {(c.attributes as string[])
                    .filter((attr) => attr in ATTRIBUTE_LABELS)
                    .map((attr) => (
                      <span key={attr} className="rounded-full bg-stone-100 px-2 py-0.5 text-[10px] font-medium text-stone-500">
                        {ATTRIBUTE_LABELS[attr]}
                      </span>
                    ))}
                </div>
              )}
            </div>
          </Link>
        ))}
      </div>
      <Paginator page={page} totalPages={totalPages} onPage={setPage} />
    </>
  );
}
