import { notFound } from "next/navigation";
import Link from "next/link";
import { getServerSet } from "@/lib/serverApi";
import type { ComedianType } from "@/lib/serverApi";
import { Badge } from "@/components/ui/badge";
import VideoEmbed from "@/components/VideoEmbed";

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

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex flex-col items-center rounded-md border border-stone-100 bg-stone-50 px-3 py-2 text-center">
      <span className="text-sm font-semibold leading-tight tabular-nums text-stone-800">{value}</span>
      <span className="mt-0.5 whitespace-nowrap text-[11px] leading-tight text-stone-400">{label}</span>
    </div>
  );
}

const jokeBookLabel: Record<string, string> = {
  small: "Small Joke Book",
  medium: "Medium Joke Book",
  large: "Large Joke Book",
};

const jokeBookVariant: Record<string, "stone" | "amber" | "red"> = {
  small: "stone",
  medium: "amber",
  large: "red",
};

const comedianTypeLabel: Record<ComedianType, string> = {
  bucket_pull: "Bucket Pull",
  regular: "Regular",
  golden_ticket: "Golden Ticket",
  special: "Special",
};

const comedianTypeColor: Record<ComedianType, string> = {
  bucket_pull: "bg-stone-100 text-stone-500",
  regular: "bg-blue-50 text-blue-600",
  golden_ticket: "bg-amber-100 text-amber-700",
  special: "bg-purple-50 text-purple-600",
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
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <div className="mb-2 text-sm text-stone-400">
          <Link href={`/killtony/episodes/${set.episode.id}`} className="hover:text-stone-600 transition-colors">
            ← Episode {set.episode.number}
          </Link>
        </div>

        {/* Comedian header */}
        <div className="mb-6">
          <div className="flex flex-wrap items-center gap-2 mb-1">
            <h1 className="text-3xl font-bold text-stone-900">
              <Link href={`/killtony/comedians/${comedian.slug}`} className="hover:text-primary transition-colors">
                {comedian.name}
              </Link>
            </h1>
            {ct && (
              <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${comedianTypeColor[ct]}`}>
                {comedianTypeLabel[ct]}
              </span>
            )}
          </div>
          <p className="text-stone-400 text-sm">
            Episode {set.episode.number} · {set.episode.date ?? "Date unknown"}
          </p>

          {/* Comedian joke book badges */}
          {(comedian.has_small_joke_book || comedian.has_medium_joke_book || comedian.has_large_joke_book) && (
            <div className="mt-2 flex flex-wrap gap-1.5">
              {comedian.has_small_joke_book && (
                <span className="rounded-full bg-stone-100 px-2.5 py-0.5 text-xs font-medium text-stone-500">Small Joke Book</span>
              )}
              {comedian.has_medium_joke_book && (
                <span className="rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-medium text-amber-700">Medium Joke Book</span>
              )}
              {comedian.has_large_joke_book && (
                <span className="rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-primary">Large Joke Book</span>
              )}
            </div>
          )}
        </div>

        {/* Comedian career stats */}
        <div className="mb-8 flex flex-wrap gap-2">
          <Stat label="Appearances" value={comedian.appearances} />
          <Stat label="Sets" value={comedian.set_count} />
          {comedian.avg_bits_per_set != null && (
            <Stat label="Avg bits/set" value={fmt2(comedian.avg_bits_per_set)} />
          )}
          {comedian.avg_beats_per_set != null && (
            <Stat label="Avg beats/set" value={fmt2(comedian.avg_beats_per_set)} />
          )}
          {comedian.avg_hit_ratio != null && (
            <Stat label="Setup/punch ratio" value={fmt2(comedian.avg_hit_ratio)} />
          )}
          {comedian.avg_punchline_tag_ratio != null && (
            <Stat label="Punch/tag ratio" value={fmt2(comedian.avg_punchline_tag_ratio)} />
          )}
        </div>

        {/* Video + set stats */}
        <div className="mb-10 flex flex-col gap-6 sm:flex-row sm:items-start">
          <div className="sm:w-72 shrink-0">
            <VideoEmbed
              youtubeId={set.episode.youtube_id}
              startSeconds={Math.max(0, set.start_seconds - 10)}
            />
          </div>

          <div className="flex flex-col gap-3">
            <p className="text-xs font-semibold uppercase tracking-wide text-stone-400">This set</p>

            {set.joke_book_award && (
              <Badge variant={jokeBookVariant[set.joke_book_award]}>
                {jokeBookLabel[set.joke_book_award]}
              </Badge>
            )}

            <div className="flex flex-wrap gap-2">
              <Stat label="Bits" value={bitCount} />
              <Stat label="Beats" value={beatCount} />
              {set.hit_ratio != null && (
                <Stat label="Setup/punch ratio" value={fmt2(set.hit_ratio)} />
              )}
              {set.punchline_tag_ratio != null && (
                <Stat label="Punch/tag ratio" value={fmt2(set.punchline_tag_ratio)} />
              )}
            </div>
          </div>
        </div>

        {/* Bits */}
        {set.bits.length === 0 ? (
          <div className="rounded-xl border border-stone-200 bg-stone-50 p-8 text-center">
            <p className="text-stone-500">No beats annotated yet.</p>
          </div>
        ) : (
          <div className="space-y-8">
            {set.bits.map((bit, bi) => (
              <div key={bit.id} className="rounded-xl border border-stone-200 overflow-hidden">
                <div className="bg-stone-50 px-5 py-3 border-b border-stone-200">
                  <span className="text-xs font-medium text-stone-400 uppercase tracking-wide">
                    Bit {bi + 1}
                  </span>
                  {bit.premise && (
                    <span className="ml-3 text-sm text-stone-500 italic">"{bit.premise}"</span>
                  )}
                </div>
                <div className="divide-y divide-stone-100">
                  {bit.beats.map((beat, bti) => (
                    <div key={beat.id} className="px-5 py-5">
                      <div className="mb-3 flex flex-wrap items-center gap-2">
                        <span className="text-xs font-medium text-stone-400 uppercase tracking-wide">
                          Beat {bti + 1}
                        </span>
                        {beat.joke_type && <Badge variant="default">{beat.joke_type}</Badge>}
                        {beat.topics.map((t) => (
                          <Badge key={t} variant="stone">{t}</Badge>
                        ))}
                      </div>
                      {beat.premise && (
                        <p className="mb-3 text-sm italic text-stone-500">"{beat.premise}"</p>
                      )}
                      <p className="text-stone-700 leading-relaxed">
                        {beat.lines.map((l) => l.text).join(" ")}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
