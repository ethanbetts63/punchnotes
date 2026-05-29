import { notFound } from "next/navigation";
import Link from "next/link";
import { getServerSet } from "@/lib/serverApi";
import type { ComedianAttribute } from "@/lib/serverApi";
import SetTranscript from "@/components/SetTranscript";

type Props = { params: Promise<{ id: string }> };

export async function generateMetadata({ params }: Props) {
  const { id } = await params;
  const set = await getServerSet(id);
  if (!set) return { title: "Set Not Found | PunchPedia" };
  return { title: `${set.comedian.name} — Ep ${set.episode.number} | PunchPedia` };
}

function fmt2(n: number | null): string {
  return n == null ? "—" : n.toFixed(2);
}

const jokeBookLabel: Record<string, string> = {
  small:  "Small Joke Book",
  medium: "Medium Joke Book",
  large:  "Large Joke Book",
};

type AppearanceAttribute = "bucket_pull" | "regular" | "golden_ticket" | "special";

const appearanceAttributes: AppearanceAttribute[] = ["bucket_pull", "regular", "golden_ticket", "special"];

const comedianTypeLabel: Record<AppearanceAttribute, string> = {
  bucket_pull:   "Bucket Pull",
  regular:       "Regular",
  golden_ticket: "Golden Ticket",
  special:       "Special",
};

const comedianTypeBadge: Record<AppearanceAttribute, string> = {
  bucket_pull:   "bg-stone-700 text-stone-300",
  regular:       "bg-blue-900/60 text-blue-200",
  golden_ticket: "bg-yellow-800/60 text-yellow-200",
  special:       "bg-purple-900/60 text-purple-200",
};

function getAppearanceType(attributes: readonly ComedianAttribute[]): AppearanceAttribute | null {
  return appearanceAttributes.find((attr) => attributes.includes(attr)) ?? null;
}

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
  const ct = getAppearanceType(comedian.attributes);

  const bitCount = set.bits.length;
  const beatCount = set.bits.reduce((sum, bit) => sum + bit.beats.length, 0);

  return (
    <div className="bg-white min-h-screen">
      <div className="bg-stone-900 text-white">
        <div className="mx-auto max-w-5xl px-6 py-10">
          <div className="flex gap-8 items-start">

            {/* YouTube thumbnail + episode info beneath */}
            {set.episode.youtube_id && (
              <div className="hidden sm:block w-36 md:w-48 shrink-0">
                <a
                  href={`https://www.youtube.com/watch?v=${set.episode.youtube_id}&t=${Math.max(0, set.start_seconds - 10)}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block rounded-lg overflow-hidden shadow-xl ring-1 ring-white/10 hover:ring-yellow-400/50 transition-all group relative"
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
                <div className="mt-2 space-y-0.5">
                  <p className="text-xs text-stone-300 leading-snug">
                    <Link
                      href={`/killtony/episodes/${set.episode.id}`}
                      className="hover:text-white transition-colors"
                    >
                      {set.episode.title}
                    </Link>
                  </p>
                  {set.episode.date && (
                    <p className="text-xs text-stone-500">{set.episode.date}</p>
                  )}
                </div>
              </div>
            )}

            {/* Info */}
            <div className="flex-1 min-w-0">

              {/* Comedian name */}
              <h1 className="text-3xl md:text-4xl font-bold text-white mb-1">
                <Link
                  href={`/killtony/comedians/${comedian.slug}`}
                  className="hover:text-yellow-300 transition-colors"
                >
                  {comedian.name}
                </Link>
              </h1>

              {/* Type + joke book badges on one row */}
              <div className="flex flex-wrap gap-1.5 mb-5">
                {ct && (
                  <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${comedianTypeBadge[ct]}`}>
                    {comedianTypeLabel[ct]}
                  </span>
                )}
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
              </div>

              {/* Stats */}
              <div className="space-y-1.5 text-sm text-stone-400">
                <p>
                  <span className="text-stone-500 font-medium">Career avg</span>
                  <span className="mx-2 text-stone-700">·</span>
                  <span className="text-white">{fmt2(comedian.avg_bits_per_set)}</span> bits/set
                  <span className="mx-2 text-stone-700">·</span>
                  <span className="text-white">{fmt2(comedian.avg_beats_per_set)}</span> beats/set
                  <span className="mx-2 text-stone-700">·</span>
                  <span className="text-white">{fmt2(comedian.avg_hit_ratio)}</span> setup/punch
                  <span className="mx-2 text-stone-700">·</span>
                  <span className="text-white">{fmt2(comedian.avg_punchline_tag_ratio)}</span> punch/tag
                  <span className="mx-2 text-stone-700">·</span>
                  {comedian.appearances} appearance{comedian.appearances !== 1 ? "s" : ""}
                </p>
                <p>
                  <span className="text-stone-500 font-medium">This set</span>
                  <span className="mx-2 text-stone-700">·</span>
                  <span className="text-white">{bitCount}</span> bit{bitCount !== 1 ? "s" : ""}
                  <span className="mx-2 text-stone-700">·</span>
                  <span className="text-white">{beatCount}</span> beat{beatCount !== 1 ? "s" : ""}
                  <span className="mx-2 text-stone-700">·</span>
                  <span className="text-white">{fmt2(set.hit_ratio)}</span> setup/punch
                  <span className="mx-2 text-stone-700">·</span>
                  <span className="text-white">{fmt2(set.punchline_tag_ratio)}</span> punch/tag
                  {set.joke_book_award && (
                    <>
                      <span className="mx-2 text-stone-700">·</span>
                      <span className={`rounded-full px-2 py-0.5 text-[10px] font-semibold ${jokeBookBadge[set.joke_book_award]}`}>
                        {jokeBookLabel[set.joke_book_award]}
                      </span>
                    </>
                  )}
                </p>
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
