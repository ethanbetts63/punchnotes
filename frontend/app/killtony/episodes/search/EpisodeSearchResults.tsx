"use client";

import Link from "next/link";
import { useMemo } from "react";
import { useSearchParams } from "next/navigation";
import type { Video } from "@/lib/serverApi";
import { fmtDate, fmtDuration, fmtCompact, getVideoGuestLabel } from "@/lib/killTonyDisplay";
import { useUrlPagination } from "@/lib/useUrlPagination";
import Paginator from "@/components/Paginator";
import YoutubeThumbnail from "@/components/YoutubeThumbnail";

const PAGE_SIZE = 20;

type SortKey =
  | "date"
  | "duration"
  | "set_count"
  | "bucket_pulls"
  | "golden_tickets"
  | "large_joke_books"
  | "regulars"
  | "view_count"
  | "like_count"
  | "like_ratio";

function getValue(ep: Video, key: SortKey): number {
  switch (key) {
    case "date":
      return ep.number;
    case "duration":
      return ep.duration_seconds ?? 0;
    case "set_count":
      return ep.set_count;
    case "bucket_pulls":
      return ep.bucket_pull_count;
    case "golden_tickets":
      return ep.golden_ticket_count;
    case "large_joke_books":
      return ep.large_joke_book_count;
    case "regulars":
      return ep.regular_count;
    case "view_count":
      return ep.view_count ?? 0;
    case "like_count":
      return ep.like_count ?? 0;
    case "like_ratio":
      return ep.view_count ? (ep.like_count ?? 0) / ep.view_count : 0;
  }
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex flex-col items-center rounded-md border border-stone-100 bg-stone-50 px-2.5 py-1.5 text-center">
      <span className="text-xs font-semibold leading-tight tabular-nums text-stone-800">{value}</span>
      <span className="mt-0.5 whitespace-nowrap text-[10px] leading-tight text-stone-400">{label}</span>
    </div>
  );
}

export default function VideoSearchResults({ episodes }: { episodes: Video[] }) {
  const sp = useSearchParams();
  const sort = (sp.get("sort") ?? "date") as SortKey;
  const asc = sp.get("asc") === "1";

  const sorted = useMemo(
    () =>
      [...episodes].sort((a, b) => {
        const diff = getValue(b, sort) - getValue(a, sort);
        return asc ? -diff : diff;
      }),
    [episodes, sort, asc]
  );

  const { page, totalPages, setPage } = useUrlPagination(sorted.length, PAGE_SIZE);
  const pageItems = sorted.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  return (
    <>
      <div className="flex flex-col gap-3">
        {pageItems.map((ep) => {
          const likeRatio =
            ep.view_count && ep.like_count != null && ep.view_count > 0
              ? `${((ep.like_count / ep.view_count) * 100).toFixed(1)}%`
              : null;
          const guestLabel = getVideoGuestLabel(ep, `Kill Tony #${ep.number}`);

          return (
            <Link
              key={ep.id}
              href={`/killtony/episodes/${ep.id}`}
              className="group flex items-center overflow-hidden rounded-xl border border-stone-200 bg-white transition-colors hover:border-stone-400"
            >
              <YoutubeThumbnail
                videoId={ep.youtube_id}
                alt={`Video ${ep.number} - ${guestLabel}`}
                className="aspect-video w-36 shrink-0 sm:w-52"
              />
              <div className="min-w-0 flex-1 px-4 py-3">
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0">
                    <span className="text-[11px] font-medium uppercase tracking-wide text-stone-400">
                      Video {ep.number}
                    </span>
                    <p className="mt-0.5 truncate font-semibold leading-snug text-stone-900">
                      {guestLabel}
                    </p>
                    <p className="mt-0.5 text-xs text-stone-400">{fmtDate(ep.date) || "-"}</p>
                  </div>
                  <svg
                    className="mt-1 h-4 w-4 shrink-0 text-stone-300 transition-colors group-hover:text-stone-500"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  <Stat label="Duration" value={fmtDuration(ep.duration_seconds)} />
                  <Stat label="Sets" value={ep.set_count} />
                  <Stat label="Bucket pulls" value={ep.bucket_pull_count} />
                  <Stat label="Golden tickets" value={ep.golden_ticket_count} />
                  <Stat label="Big joke books" value={ep.large_joke_book_count} />
                  <Stat label="Regulars" value={ep.regular_count} />
                  {ep.view_count != null && <Stat label="Views" value={fmtCompact(ep.view_count)} />}
                  {ep.like_count != null && <Stat label="Likes" value={fmtCompact(ep.like_count)} />}
                  {ep.comment_count != null && <Stat label="Comments" value={fmtCompact(ep.comment_count)} />}
                  {likeRatio && <Stat label="View/like ratio" value={likeRatio} />}
                </div>
              </div>
            </Link>
          );
        })}
      </div>
      <Paginator page={page} totalPages={totalPages} onPage={setPage} />
    </>
  );
}
