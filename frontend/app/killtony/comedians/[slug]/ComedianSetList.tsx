"use client";

import { useSearchParams } from "next/navigation";
import type { SetInComedian } from "@/lib/serverApi";
import { fmt2, fmtSeconds, getJokeBookSize, jokeBookLabel } from "@/lib/killTonyDisplay";
import Paginator from "@/components/Paginator";
import SetImage from "@/components/SetImage";
import SearchResultTile from "@/components/SearchResultTile";

const PAGE_SIZE = 12;

type Props = { sets: SetInComedian[] };

function formatEpisodeTitle(title: string | null | undefined, fallback: string): string {
  return title?.replace(/^KT\s*#\d+\s*[-–]\s*/i, "") || fallback;
}

export default function ComedianSetList({ sets }: Props) {
  const searchParams = useSearchParams();
  const totalPages = Math.max(1, Math.ceil(sets.length / PAGE_SIZE));
  const rawPage = parseInt(searchParams.get("page") ?? "1", 10) || 1;
  const page = Math.min(Math.max(rawPage, 1), totalPages);
  const pageItems = sets.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  return (
    <>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {pageItems.map((set) => {
          const jokeBook = getJokeBookSize(set.attributes);

          return (
            <SearchResultTile
              key={set.id}
              href={`/killtony/sets/${set.slug}`}
              eyebrow={`KT #${set.video.number}`}
              title={formatEpisodeTitle(set.video.title, `Set ${set.set_number}`)}
              subtitle={set.video.date ?? undefined}
              image={
                <SetImage
                  imageUrl={set.image_url}
                  fallbackVideoId={set.video.youtube_id}
                  alt={`Set ${set.set_number} image`}
                  className="absolute inset-0 h-full w-full"
                />
              }
              meta={<>Set {set.set_number} / {fmtSeconds(set.start_seconds)}</>}
              stats={[
                { label: "Bits", value: set.bit_count },
                { label: "Punch density", value: fmt2(set.punch_density) },
                { label: "Tag density", value: fmt2(set.tag_density) },
              ]}
              badges={
                jokeBook ? (
                  <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-bold text-amber-700">
                    {jokeBookLabel[jokeBook]}
                  </span>
                ) : undefined
              }
            />
          );
        })}
      </div>
      <Paginator page={page} totalPages={totalPages} />
    </>
  );
}
