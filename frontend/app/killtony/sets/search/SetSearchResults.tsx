"use client";

import Link from "next/link";
import { useMemo } from "react";
import { useSearchParams } from "next/navigation";
import type { SetListItem } from "@/lib/serverApi";
import { ATTRIBUTE_LABELS } from "@/lib/attributes";
import { getJokeBookSize, jokeBookLabel } from "@/lib/killTonyDisplay";
import { useUrlPagination } from "@/lib/useUrlPagination";
import Paginator from "@/components/Paginator";
import SetImage from "@/components/SetImage";

const PAGE_SIZE = 20;

type SortKey = "episode" | "comedian" | "bit_count" | "hit_ratio" | "punchline_tag_ratio" | "start_seconds";


function fmt2(n: number | null): string {
  return n == null ? "-" : n.toFixed(2);
}

function fmtSeconds(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  return `${m}:${String(s).padStart(2, "0")}`;
}

function getSortValue(set: SetListItem, key: SortKey): number | string {
  switch (key) {
    case "episode":             return set.episode.number;
    case "comedian":            return set.comedian.name.toLowerCase();
    case "bit_count":           return set.bit_count;
    case "hit_ratio":           return set.hit_ratio ?? -1;
    case "punchline_tag_ratio": return set.punchline_tag_ratio ?? -1;
    case "start_seconds":       return set.start_seconds;
  }
}

export default function SetSearchResults({ sets }: { sets: SetListItem[] }) {
  const sp = useSearchParams();
  const sort = (sp.get("sort") ?? "episode") as SortKey;
  const asc = sp.get("asc") === "1";

  const sorted = useMemo(() => (
    [...sets].sort((a, b) => {
      const va = getSortValue(a, sort);
      const vb = getSortValue(b, sort);
      const cmp = typeof va === "string" ? va.localeCompare(vb as string) : (va as number) - (vb as number);
      return asc ? cmp : -cmp;
    })
  ), [sets, sort, asc]);

  const { page, totalPages, setPage } = useUrlPagination(sorted.length, PAGE_SIZE);
  const pageItems = sorted.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  return (
    <>
      <div className="flex flex-col gap-3">
        {pageItems.map((set) => (
          <Link
            key={set.id}
            href={`/killtony/sets/${set.id}`}
            className="group flex overflow-hidden rounded-xl border border-stone-200 bg-white transition-colors hover:border-primary/40 hover:shadow-sm"
          >
            <SetImage
              imageUrl={set.image_url}
              fallbackVideoId={set.episode.youtube_id}
              alt={`${set.comedian.name} set image`}
              className="hidden w-32 shrink-0 bg-stone-950 sm:block"
            />
            <div className="min-w-0 flex-1 p-4">
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <p className="text-xs font-bold uppercase tracking-wide text-stone-400">
                    KT #{set.episode.number} / Set {set.set_number} / {fmtSeconds(set.start_seconds)}
                  </p>
                  <p className="mt-1 truncate text-lg font-bold leading-tight text-stone-900 transition-colors group-hover:text-primary">
                    {set.comedian.name}
                  </p>
                  <p className="mt-1 truncate text-sm text-stone-500">{set.episode.title}</p>
                </div>
                {(() => { const jb = getJokeBookSize(set.attributes); return jb ? (<span className="shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium bg-amber-100 text-amber-700">{jokeBookLabel[jb]}</span>) : null; })()}
              </div>
              <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-stone-500">
                <span><span className="font-bold text-stone-800">{set.bit_count}</span> bits</span>
                <span>Setup/punch <span className="font-bold text-stone-800">{fmt2(set.hit_ratio)}</span></span>
                <span>Punch/tag <span className="font-bold text-stone-800">{fmt2(set.punchline_tag_ratio)}</span></span>
              </div>
              {set.comedian.attributes.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {(set.comedian.attributes as string[])
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
