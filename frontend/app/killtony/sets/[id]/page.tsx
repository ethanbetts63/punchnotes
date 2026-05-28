import { notFound } from "next/navigation";
import Link from "next/link";
import { getServerSet } from "@/lib/serverApi";
import { Badge } from "@/components/ui/badge";
import VideoEmbed from "@/components/VideoEmbed";

type Props = { params: Promise<{ id: string }> };

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

export async function generateMetadata({ params }: Props) {
  const { id } = await params;
  const set = await getServerSet(id);
  if (!set) return { title: "Set Not Found | JokeScore" };
  return {
    title: `${set.comedian.name} — Ep ${set.episode.number} | JokeScore`,
  };
}

export default async function SetDetailPage({ params }: Props) {
  const { id } = await params;
  const set = await getServerSet(id);
  if (!set) notFound();

  return (
    <div className="bg-white min-h-screen">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <div className="mb-2 text-sm text-stone-400">
          <Link href={`/killtony/episodes/${set.episode.id}`} className="hover:text-stone-600 transition-colors">
            ← Episode {set.episode.number}
          </Link>
        </div>

        <div className="mb-8 flex items-start justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-stone-900">
              <Link href={`/killtony/comedians/${set.comedian.slug}`} className="hover:text-primary transition-colors">
                {set.comedian.name}
              </Link>
            </h1>
            <p className="mt-1 text-stone-400">
              Episode {set.episode.number} · {set.episode.date}
            </p>
          </div>
          {set.joke_book_award && (
            <Badge variant={jokeBookVariant[set.joke_book_award]}>
              {jokeBookLabel[set.joke_book_award]}
            </Badge>
          )}
        </div>

        <div className="mb-8">
          <VideoEmbed youtubeId={set.episode.youtube_id} startSeconds={Math.max(0, set.start_seconds - 10)} className="max-w-sm" />
        </div>

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
                </div>
                <div className="divide-y divide-stone-100">
                  {bit.beats.map((beat, bti) => (
                    <div key={beat.id} className="px-5 py-5">
                      <div className="mb-3 flex flex-wrap items-center gap-2">
                        <span className="text-xs font-medium text-stone-400 uppercase tracking-wide">
                          Beat {bti + 1}
                        </span>
                        <Badge variant="default">{beat.joke_type}</Badge>
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
