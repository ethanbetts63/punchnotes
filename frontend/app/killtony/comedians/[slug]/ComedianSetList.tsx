"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import type { SetInComedian } from "@/lib/serverApi";
import { fmt2, getJokeBookSize, jokeBookLabel } from "@/lib/killTonyDisplay";
import Paginator from "@/components/Paginator";
import SetImage from "@/components/SetImage";

const PAGE_SIZE = 12;

type Props = { sets: SetInComedian[] };

export default function ComedianSetList({ sets }: Props) {
  const searchParams = useSearchParams();
  const totalPages = Math.max(1, Math.ceil(sets.length / PAGE_SIZE));
  const rawPage = parseInt(searchParams.get("page") ?? "1", 10) || 1;
  const page = Math.min(Math.max(rawPage, 1), totalPages);
  const pageItems = sets.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

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
              fallbackVideoId={set.video.youtube_id}
              alt={`Set ${set.set_number} image`}
              className="hidden w-32 shrink-0 bg-stone-950 sm:block"
            />
            <div className="min-w-0 flex-1 p-4">
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <p className="text-xs font-bold uppercase tracking-wide text-stone-400">
                    KT #{set.video.number} / Set {set.set_number}
                    {set.video.date && (
                      <span className="ml-2 normal-case font-normal">{set.video.date}</span>
                    )}
                  </p>
                  <p className="mt-1 truncate text-base font-semibold leading-tight text-stone-900 transition-colors group-hover:text-primary">
                    {set.video.title?.replace(/^KT\s*#\d+\s*[-–]\s*/i, "") ?? ""}
                  </p>
                </div>
                {(() => { const jb = getJokeBookSize(set.attributes); return jb ? (<span className="shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium bg-amber-100 text-amber-700">{jokeBookLabel[jb]}</span>) : null; })()}
              </div>
              <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-stone-500">
                <span>
                  Setup/punch{" "}
                  <span className="font-bold text-stone-800">{fmt2(set.hit_ratio)}</span>
                </span>
                <span>
                  Punch/tag{" "}
                  <span className="font-bold text-stone-800">{fmt2(set.punchline_tag_ratio)}</span>
                </span>
              </div>
            </div>
          </Link>
        ))}
      </div>
      <Paginator page={page} totalPages={totalPages} />
    </>
  );
}
