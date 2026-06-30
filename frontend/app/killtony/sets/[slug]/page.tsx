import { notFound } from "next/navigation";
import Link from "next/link";
import { getServerSet } from "@/lib/serverApi";
import SetTranscript from "@/components/SetTranscript";
import SetImage from "@/components/SetImage";
import VideoEmbed from "@/components/VideoEmbed";
import { fmt2, fmtSeconds, getJokeBookSize, jokeBookLabel } from "@/lib/killTonyDisplay";
import { ATTRIBUTE_LABELS } from "@/lib/attributes";

type Props = {
  params: Promise<{ slug: string }>;
};

export async function generateMetadata({ params }: Props) {
  const { slug } = await params;
  const set = await getServerSet(slug);
  if (!set) return { title: "Set Not Found | PunchNotes" };
  return {
    title: `${set.comedian.name} - Ep ${set.video.number} | PunchNotes`,
    robots: { index: false, follow: false },
  };
}

export default async function SetDetailPage({ params }: Props) {
  const { slug } = await params;
  const set = await getServerSet(slug);
  if (!set) notFound();

  const { comedian } = set;
  const bitCount = set.bits.length;
  const beatCount = set.bits.reduce((sum, bit) => sum + bit.beats.length, 0);
  const videoStartSeconds = Math.max(0, set.start_seconds - 20);
  const youtubeTimestampUrl = set.video.youtube_id
    ? `https://www.youtube.com/watch?v=${set.video.youtube_id}&t=${Math.floor(videoStartSeconds)}s`
    : null;

  return (
    <div className="min-h-screen bg-white">
      {set.video.youtube_id && (
        <div className="bg-stone-950">
          <div className="mx-auto max-w-5xl px-6 py-8">
            <div className="mb-3 flex items-baseline justify-between">
              <p className="text-sm font-medium text-white">Watch {comedian.name}&rsquo;s set</p>
              <p className="text-xs text-stone-400">Skips to {fmtSeconds(videoStartSeconds)} in the episode</p>
            </div>
            <VideoEmbed
              youtubeId={set.video.youtube_id}
              startSeconds={videoStartSeconds}
            />
            {youtubeTimestampUrl && (
              <p className="mt-3 text-sm text-stone-300">
                Having trouble with the embed?{" "}
                <a
                  href={youtubeTimestampUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-medium text-white underline decoration-stone-500 underline-offset-4 transition-colors hover:text-yellow-300 hover:decoration-yellow-300"
                >
                  Open on YouTube at {fmtSeconds(videoStartSeconds)}
                </a>
              </p>
            )}
          </div>
        </div>
      )}

      <div className="bg-stone-900 text-white">
        <div className="mx-auto max-w-5xl px-6 py-10">
          <div className="flex items-start gap-8">
            {(set.image_url || set.video.youtube_id) && (
              <div className="hidden w-36 shrink-0 sm:block md:w-48">
                <Link
                  href={`/killtony/episodes/${set.video.slug}`}
                  className="block overflow-hidden rounded-lg shadow-xl ring-1 ring-white/10 transition-all hover:ring-white/30"
                >
                  <SetImage
                    imageUrl={set.image_url}
                    fallbackVideoId={set.video.youtube_id}
                    alt={`${set.comedian.name} set image`}
                    className="aspect-video w-full"
                  />
                </Link>
                <div className="mt-2 space-y-0.5">
                  <p className="text-xs leading-snug text-stone-300">
                    <Link
                      href={`/killtony/episodes/${set.video.slug}`}
                      className="transition-colors hover:text-white"
                    >
                      {set.video.title}
                    </Link>
                  </p>
                  {set.video.date && (
                    <p className="text-xs text-stone-500">{set.video.date}</p>
                  )}
                </div>
              </div>
            )}

            <div className="min-w-0 flex-1">
              <p className="mb-1 text-xs font-medium uppercase tracking-wide text-stone-400">
                Set {set.set_number} · <Link href={`/killtony/episodes/${set.video.slug}`} className="transition-colors hover:text-stone-200">Episode {set.video.number}</Link>
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
                  <span className="rounded-full bg-stone-100 px-2.5 py-0.5 text-xs font-medium text-stone-500">
                    Small Joke Book
                  </span>
                )}
                {comedian.has_medium_joke_book && (
                  <span className="rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-medium text-amber-700">
                    Medium Joke Book
                  </span>
                )}
                {comedian.has_large_joke_book && (
                  <span className="rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-primary">
                    Big Joke Book
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
                  <span className="text-white">{fmt2(comedian.avg_punch_density)}</span> punch density
                  <span className="mx-2 text-stone-700">·</span>
                  <span className="text-white">{fmt2(comedian.avg_tag_density)}</span> tag density
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
                  <span className="text-white">{fmt2(set.punch_density)}</span> punch density
                  <span className="mx-2 text-stone-700">·</span>
                  <span className="text-white">{fmt2(set.tag_density)}</span> tag density
                  {(() => { const jb = getJokeBookSize(set.attributes); return jb ? (<><span className="mx-2 text-stone-700">·</span><span className="rounded-full px-2 py-0.5 text-[10px] font-semibold bg-stone-700 text-stone-200">{jokeBookLabel[jb]}</span></>) : null; })()}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <SetTranscript bits={set.bits} />
    </div>
  );
}
