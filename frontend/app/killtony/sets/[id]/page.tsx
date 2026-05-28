import { notFound } from "next/navigation";
import Link from "next/link";
import { getServerSet } from "@/lib/serverApi";
import type { ComedianType } from "@/lib/serverApi";
import SetTranscript from "@/components/SetTranscript";

type Props = { params: Promise<{ id: string }> };

export async function generateMetadata({ params }: Props) {
  const { id } = await params;
  const set = await getServerSet(id);
  if (!set) return { title: "Set Not Found | JokeScore" };
  return { title: `${set.comedian.name} — Ep ${set.episode.number} | JokeScore` };
}

function fmt2(n: number | null): string {
  return n == null ? "—" : n.toFixed(2);
}

const jokeBookLabel: Record<string, string> = {
  small:  "Small Joke Book",
  medium: "Medium Joke Book",
  large:  "Large Joke Book",
};

const comedianTypeLabel: Record<ComedianType, string> = {
  bucket_pull:   "Bucket Pull",
  regular:       "Regular",
  golden_ticket: "Golden Ticket",
  special:       "Special",
};

const comedianTypeBadge: Record<ComedianType, string> = {
  bucket_pull:   "bg-stone-700 text-stone-300",
  regular:       "bg-blue-900/60 text-blue-200",
  golden_ticket: "bg-yellow-800/60 text-yellow-200",
  special:       "bg-purple-900/60 text-purple-200",
};

const jokeBookBadge: Record<string, string> = {
  small:  "bg-stone-700 text-stone-200",
  medium: "bg-amber-800/70 text-amber-200",
  large:  "bg-red-900/70 text-red-200",
};

export default async function SetDetailPage({ params }: Props) {
  const { id } = await params;
  const set = await getServerSet(id);
  if (!set) notFound();

  const { comedian } = set;
  const ct = comedian.comedian_type as ComedianType | "";

  const bitCount = set.bits.length;
  const beatCount = set.bits.reduce((sum, bit) => sum + bit.beats.length, 0);

  return (
    <div className="bg-white min-h-screen">
      {/* Genius-style dark header */}
      <div className="bg-stone-900 text-white">
        <div className="mx-auto max-w-5xl px-6 py-10">
          <div className="flex gap-6 items-start">
            {/* YouTube thumbnail — links to video at set timestamp */}
            {set.episode.youtube_id && (
              <a
                href={`https://www.youtube.com/watch?v=${set.episode.youtube_id}&t=${Math.max(0, set.start_seconds - 10)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="hidden sm:block w-36 md:w-48 shrink-0 rounded-lg overflow-hidden shadow-xl ring-1 ring-white/10 hover:ring-yellow-400/50 transition-all group relative"
              >
                <img
                  src={`https://img.youtube.com/vi/${set.episode.youtube_id}/hqdefault.jpg`}
                  alt={`Episode ${set.episode.number} thumbnail`}
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
            )}

            {/* Info */}
            <div className="flex-1 min-w-0">
              <div className="mb-2 text-sm">
                <Link
                  href={`/killtony/episodes/${set.episode.id}`}
                  className="text-stone-400 hover:text-white transition-colors"
                >
                  ← Episode {set.episode.number}
                </Link>
              </div>

              <div className="flex flex-wrap items-center gap-2.5 mb-1">
                <h1 className="text-3xl md:text-4xl font-bold text-white">
                  <Link
                    href={`/killtony/comedians/${comedian.slug}`}
                    className="hover:text-yellow-300 transition-colors"
                  >
                    {comedian.name}
                  </Link>
                </h1>
                {ct && (
                  <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${comedianTypeBadge[ct]}`}>
                    {comedianTypeLabel[ct]}
                  </span>
                )}
              </div>

              <p className="text-stone-400 text-sm mb-3">
                Episode {set.episode.number}
                {set.episode.date ? ` · ${set.episode.date}` : ""}
              </p>

              {/* Joke book badges */}
              {(comedian.has_small_joke_book || comedian.has_medium_joke_book || comedian.has_large_joke_book || set.joke_book_award) && (
                <div className="flex flex-wrap gap-1.5 mb-3">
                  {comedian.has_small_joke_book && (
                    <span className="rounded-full bg-stone-700 px-2.5 py-0.5 text-xs font-medium text-stone-300">
                      Small Joke Book
                    </span>
                  )}
                  {comedian.has_medium_joke_book && (
                    <span className="rounded-full bg-amber-900/60 px-2.5 py-0.5 text-xs font-medium text-amber-300">
                      Medium Joke Book
                    </span>
                  )}
                  {comedian.has_large_joke_book && (
                    <span className="rounded-full bg-red-900/60 px-2.5 py-0.5 text-xs font-medium text-red-300">
                      Large Joke Book
                    </span>
                  )}
                  {set.joke_book_award && (
                    <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${jokeBookBadge[set.joke_book_award]}`}>
                      {jokeBookLabel[set.joke_book_award]} — This Set
                    </span>
                  )}
                </div>
              )}

              {/* Stats row */}
              <div className="flex flex-wrap gap-x-5 gap-y-1 text-sm text-stone-300">
                <span>{comedian.appearances} appearance{comedian.appearances !== 1 ? "s" : ""}</span>
                <span>{bitCount} bit{bitCount !== 1 ? "s" : ""}</span>
                <span>{beatCount} beat{beatCount !== 1 ? "s" : ""}</span>
                {set.hit_ratio != null && (
                  <span>Setup/punch ratio: {fmt2(set.hit_ratio)}</span>
                )}
                {set.punchline_tag_ratio != null && (
                  <span>Punch/tag ratio: {fmt2(set.punchline_tag_ratio)}</span>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Transcript */}
      <SetTranscript bits={set.bits} />
    </div>
  );
}
