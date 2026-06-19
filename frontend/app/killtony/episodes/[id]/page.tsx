import { notFound } from "next/navigation";
import Link from "next/link";
import { getServerVideo } from "@/lib/serverApi";
import type { SetInVideo } from "@/lib/serverApi";
import { fmtSeconds, fmtDuration, fmtCompact, getJokeBookSize, jokeBookLabel } from "@/lib/killTonyDisplay";
import { ATTRIBUTE_LABELS } from "@/lib/attributes";

type Props = { params: Promise<{ id: string }> };

export async function generateMetadata({ params }: Props) {
  const { id } = await params;
  const episode = await getServerVideo(id);
  if (!episode) return { title: "Episode Not Found | PunchNotes" };
  return { title: `KT #${episode.number} — Kill Tony | PunchNotes` };
}

function SetTile({ set, duration }: { set: SetInVideo; duration: number | null }) {
  const attributes = set.comedian.attributes.filter((attr) => attr in ATTRIBUTE_LABELS);

  return (
    <Link
      href={`/killtony/sets/${set.id}`}
      className="group flex flex-col gap-3 rounded-xl border border-stone-200 bg-white p-5 hover:border-primary/40 hover:shadow-sm transition-all"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs font-medium text-stone-400 uppercase tracking-wide mb-1">
            Set {set.set_number}
          </p>
          <p className="text-lg font-bold text-stone-900 group-hover:text-primary transition-colors leading-tight truncate">
            {set.comedian.name}
          </p>
          {attributes.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1">
              {attributes.map((attr) => (
                <span key={attr} className="rounded-full bg-stone-100 px-2 py-0.5 text-[10px] font-medium text-stone-500">
                  {ATTRIBUTE_LABELS[attr]}
                </span>
              ))}
            </div>
          )}
        </div>
        <div className="flex shrink-0 flex-col items-end gap-1.5">
          {(() => { const jb = getJokeBookSize(set.attributes); return jb ? (<span className="rounded-full px-2.5 py-0.5 text-xs font-medium bg-amber-100 text-amber-700">{jokeBookLabel[jb]}</span>) : null; })()}
        </div>
      </div>

      <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-stone-500">
        <span>
          <span className="text-stone-400">Start</span>{" "}
          <span className="font-medium tabular-nums">{fmtSeconds(set.start_seconds)}</span>
        </span>
        {set.interview_end_seconds != null && (
          <span>
            <span className="text-stone-400">End</span>{" "}
            <span className="font-medium tabular-nums">{fmtSeconds(set.interview_end_seconds)}</span>
          </span>
        )}
        {duration != null && (
          <span>
            <span className="text-stone-400">~</span>
            <span className="font-medium tabular-nums">{fmtSeconds(duration)}</span>
          </span>
        )}
      </div>

      <p className="text-sm text-stone-400">
        {set.bit_count === 0
          ? "No bits annotated"
          : `${set.bit_count} bit${set.bit_count === 1 ? "" : "s"}`}
      </p>
    </Link>
  );
}

export default async function EpisodeDetailPage({ params }: Props) {
  const { id } = await params;
  const episode = await getServerVideo(id);
  if (!episode) notFound();

  const sets = episode.sets ?? [];
  const viewLikeRatio =
    episode.view_like_ratio != null
      ? episode.view_like_ratio.toFixed(1)
      : null;

  return (
    <div className="bg-white min-h-screen">
      {/* Dark hero */}
      <div className="bg-stone-900 text-white">
        <div className="mx-auto max-w-5xl px-6 py-10">
          <div className="flex gap-8 items-start">

            {/* YouTube thumbnail */}
            {episode.youtube_id && (
              <div className="hidden sm:block w-36 md:w-48 shrink-0">
                <a
                  href={`https://www.youtube.com/watch?v=${episode.youtube_id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block rounded-lg overflow-hidden shadow-xl ring-1 ring-white/10 hover:ring-yellow-400/50 transition-all group relative"
                >
                  <img
                    src={`https://img.youtube.com/vi/${episode.youtube_id}/hqdefault.jpg`}
                    alt={`Episode ${episode.number} thumbnail`}
                    className="w-full aspect-video object-cover"
                  />
                  <div className="absolute inset-0 flex items-center justify-center bg-black/30 opacity-0 group-hover:opacity-100 transition-opacity">
                    <div className="w-10 h-10 rounded-full bg-white/90 flex items-center justify-center">
                      <svg className="w-4 h-4 text-stone-900 ml-0.5" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M6.3 2.841A1.5 1.5 0 004 4.11v11.78a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.841z" />
                      </svg>
                    </div>
                  </div>
                </a>
                {episode.date && (
                  <p className="mt-2 text-xs text-stone-500">{episode.date}</p>
                )}
              </div>
            )}

            {/* Info */}
            <div className="flex-1 min-w-0">
              <h1 className="text-3xl md:text-4xl font-bold text-white mb-1">
                {episode.title || `Kill Tony #${episode.number}`}
              </h1>

              <p className="text-stone-400 text-sm mb-5">
                Episode {episode.number}
                {episode.date ? ` · ${episode.date}` : ""}
              </p>

              <p className="text-sm text-stone-400">
                <span className="text-white">{sets.length}</span> set{sets.length !== 1 ? "s" : ""}
                <span className="mx-2 text-stone-700">·</span>
                <span className="text-white">{fmtDuration(episode.duration_seconds)}</span>
                <span className="mx-2 text-stone-700">·</span>
                <span className="text-white">{episode.bucket_pull_count}</span> bucket pull{episode.bucket_pull_count !== 1 ? "s" : ""}
                <span className="mx-2 text-stone-700">·</span>
                <span className="text-white">{episode.golden_ticket_count}</span> golden ticket{episode.golden_ticket_count !== 1 ? "s" : ""}
                <span className="mx-2 text-stone-700">·</span>
                <span className="text-white">{episode.regular_count}</span> regular{episode.regular_count !== 1 ? "s" : ""}
                <span className="mx-2 text-stone-700">·</span>
                <span className="text-white">{episode.large_joke_book_count}</span> big joke book{episode.large_joke_book_count !== 1 ? "s" : ""}
                {episode.view_count != null && (
                  <>
                    <span className="mx-2 text-stone-700">·</span>
                    <span className="text-white">{fmtCompact(episode.view_count)}</span> views
                  </>
                )}
                {episode.like_count != null && (
                  <>
                    <span className="mx-2 text-stone-700">·</span>
                    <span className="text-white">{fmtCompact(episode.like_count)}</span> likes
                  </>
                )}
                {episode.comment_count != null && (
                  <>
                    <span className="mx-2 text-stone-700">·</span>
                    <span className="text-white">{fmtCompact(episode.comment_count)}</span> comments
                  </>
                )}
                {viewLikeRatio && (
                  <>
                    <span className="mx-2 text-stone-700">·</span>
                    <span className="text-white">{viewLikeRatio}</span> views/like
                  </>
                )}
              </p>
            </div>

          </div>
        </div>
      </div>

      {/* Sets grid */}
      <div className="mx-auto max-w-5xl px-6 py-10">
        {sets.length === 0 ? (
          <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
            <p className="text-stone-500">No sets indexed for this episode yet.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {sets.map((set, i) => {
              const nextStart = sets[i + 1]?.start_seconds ?? null;
              const duration = nextStart != null ? nextStart - set.start_seconds : null;
              return <SetTile key={set.id} set={set} duration={duration} />;
            })}
          </div>
        )}
      </div>
    </div>
  );
}
