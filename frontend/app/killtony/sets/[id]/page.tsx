import { notFound } from "next/navigation";
import Link from "next/link";
import { getServerSet } from "@/lib/serverApi";
import SetTranscript from "@/components/SetTranscript";
import SetImage from "@/components/SetImage";
import VideoEmbed from "@/components/VideoEmbed";
import { darkJokeBookBadge, fmt2, getJokeBookSize, jokeBookLabel } from "@/lib/killTonyDisplay";
import { ATTRIBUTE_LABELS } from "@/lib/attributes";

type Props = {
  params: Promise<{ id: string }>;
};

export async function generateMetadata({ params }: Props) {
  const { id } = await params;
  const set = await getServerSet(id);
  if (!set) return { title: "Set Not Found | PunchNotes" };
  return { title: `${set.comedian.name} - Ep ${set.episode.number} | PunchNotes` };
}

function fmtSeconds(s: number): string {
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = Math.floor(s % 60);
  if (h > 0) return `${h}:${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")}`;
  return `${m}:${String(sec).padStart(2, "0")}`;
}

export default async function SetDetailPage({ params }: Props) {
  const { id } = await params;
  const set = await getServerSet(id);
  if (!set) notFound();

  const { comedian } = set;
  const bitCount = set.bits.length;
  const beatCount = set.bits.reduce((sum, bit) => sum + bit.beats.length, 0);
  return (
    <div className="min-h-screen bg-white">
      <div className="bg-stone-900 text-white">
        <div className="mx-auto max-w-5xl px-6 py-10">
          <div className="flex items-start gap-8">
            {(set.image_url || set.episode.youtube_id) && (
              <div className="hidden w-36 shrink-0 sm:block md:w-48">
                <Link
                  href={`/killtony/episodes/${set.episode.id}`}
                  className="block overflow-hidden rounded-lg shadow-xl ring-1 ring-white/10 transition-all hover:ring-white/30"
                >
                  <SetImage
                    imageUrl={set.image_url}
                    fallbackVideoId={set.episode.youtube_id}
                    alt={`${set.comedian.name} set image`}
                    className="aspect-video w-full"
                  />
                </Link>
                <div className="mt-2 space-y-0.5">
                  <p className="text-xs leading-snug text-stone-300">
                    <Link
                      href={`/killtony/episodes/${set.episode.id}`}
                      className="transition-colors hover:text-white"
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

            <div className="min-w-0 flex-1">
              <p className="mb-1 text-xs font-medium uppercase tracking-wide text-stone-400">
                Set {set.set_number} · <Link href={`/killtony/episodes/${set.episode.id}`} className="transition-colors hover:text-stone-200">Episode {set.episode.number}</Link>
              </p>

              <h1 className="mb-1 text-3xl font-bold text-white md:text-4xl">
                <Link
                  href={`/killtony/comedians/${comedian.slug}`}
                  className="transition-colors hover:text-yellow-300"
                >
                  {comedian.name}
                </Link>
              </h1>

              <div className="mb-5 flex flex-wrap gap-1.5">
                {comedian.attributes
                  .filter((attr) => attr in ATTRIBUTE_LABELS)
                  .map((attr) => (
                    <span key={attr} className="rounded-full bg-stone-700 px-2.5 py-0.5 text-xs font-medium text-stone-300">
                      {ATTRIBUTE_LABELS[attr]}
                    </span>
                  ))}
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

              <div className="space-y-1.5 text-sm text-stone-400">
                <p>
                  <span className="font-medium text-stone-500">Career avg</span>
                  <span className="mx-2 text-stone-700">·</span>
                  <span className="text-white">{fmt2(comedian.avg_bits_per_set)}</span> bits/set
                  <span className="mx-2 text-stone-700">·</span>
                  <span className="text-white">{fmt2(comedian.avg_beats_per_set)}</span> beats/set
                  <span className="mx-2 text-stone-700">·</span>
                  <span className="text-white">{fmt2(comedian.avg_hit_ratio)}</span> setup/punch
                  <span className="mx-2 text-stone-700">·</span>
                  <span className="text-white">{fmt2(comedian.avg_punchline_tag_ratio)}</span> punch/tag
                  <span className="mx-2 text-stone-700">·</span>
                  {comedian.set_count} set{comedian.set_count !== 1 ? "s" : ""}
                </p>
                <p>
                  <span className="font-medium text-stone-500">This set</span>
                  <span className="mx-2 text-stone-700">·</span>
                  <span className="text-white">{bitCount}</span> bit{bitCount !== 1 ? "s" : ""}
                  <span className="mx-2 text-stone-700">·</span>
                  <span className="text-white">{beatCount}</span> beat{beatCount !== 1 ? "s" : ""}
                  <span className="mx-2 text-stone-700">·</span>
                  <span className="text-white">{fmt2(set.hit_ratio)}</span> setup/punch
                  <span className="mx-2 text-stone-700">·</span>
                  <span className="text-white">{fmt2(set.punchline_tag_ratio)}</span> punch/tag
                  {(() => { const jb = getJokeBookSize(set.attributes); return jb ? (<><span className="mx-2 text-stone-700">·</span><span className={`rounded-full px-2 py-0.5 text-[10px] font-semibold ${darkJokeBookBadge[jb]}`}>{jokeBookLabel[jb]}</span></>) : null; })()}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {set.episode.youtube_id && (
        <div className="bg-stone-950">
          <div className="mx-auto max-w-5xl px-6 py-8">
            <div className="mb-3 flex items-baseline justify-between">
              <p className="text-sm font-medium text-white">Watch {comedian.name}&rsquo;s set</p>
              <p className="text-xs text-stone-400">Skips to {fmtSeconds(Math.max(0, set.start_seconds - 20))} in the episode</p>
            </div>
            <VideoEmbed
              youtubeId={set.episode.youtube_id}
              startSeconds={Math.max(0, set.start_seconds - 20)}
            />
          </div>
        </div>
      )}

      <SetTranscript bits={set.bits} />
    </div>
  );
}
