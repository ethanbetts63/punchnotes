import { notFound } from "next/navigation";
import Link from "next/link";
import { getServerEpisode } from "@/lib/serverApi";
import type { SetInEpisode, ComedianType } from "@/lib/serverApi";
import VideoEmbed from "@/components/VideoEmbed";

type Props = { params: Promise<{ id: string }> };

export async function generateMetadata({ params }: Props) {
  const { id } = await params;
  const episode = await getServerEpisode(id);
  if (!episode) return { title: "Episode Not Found | JokeScore" };
  return {
    title: `KT #${episode.number} — Kill Tony | JokeScore`,
  };
}

function fmtSeconds(s: number): string {
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = Math.floor(s % 60);
  if (h > 0) return `${h}:${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")}`;
  return `${m}:${String(sec).padStart(2, "0")}`;
}

function fmtDuration(seconds: number | null): string {
  if (!seconds) return "—";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  return h > 0 ? `${h}h ${m}m` : `${m}m`;
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

const jokeBookColor: Record<string, string> = {
  small: "bg-stone-100 text-stone-600",
  medium: "bg-amber-100 text-amber-700",
  large: "bg-red-100 text-primary",
};

const comedianTypeLabel: Record<ComedianType, string> = {
  bucket_pull:   "Bucket Pull",
  regular:       "Regular",
  golden_ticket: "Golden Ticket",
};

const comedianTypeColor: Record<ComedianType, string> = {
  bucket_pull:   "bg-stone-100 text-stone-500",
  regular:       "bg-blue-50 text-blue-600",
  golden_ticket: "bg-amber-100 text-amber-700",
};

function SetTile({ set, duration }: { set: SetInEpisode; duration: number | null }) {
  const ct = set.comedian.comedian_type;
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
        </div>
        <div className="flex shrink-0 flex-col items-end gap-1.5">
          {ct && (
            <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${comedianTypeColor[ct]}`}>
              {comedianTypeLabel[ct]}
            </span>
          )}
          {set.joke_book && (
            <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${jokeBookColor[set.joke_book]}`}>
              {jokeBookLabel[set.joke_book]}
            </span>
          )}
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

      <div className="flex items-center justify-between text-sm">
        <span className="text-stone-400">
          {set.bit_count === 0
            ? "No bits annotated"
            : `${set.bit_count} bit${set.bit_count === 1 ? "" : "s"}`}
        </span>
        <span className="text-stone-300 group-hover:text-primary transition-colors text-xs font-medium">
          View set →
        </span>
      </div>
    </Link>
  );
}

export default async function EpisodeDetailPage({ params }: Props) {
  const { id } = await params;
  const episode = await getServerEpisode(id);
  if (!episode) notFound();

  const sets = episode.sets ?? [];

  return (
    <div className="bg-white min-h-screen">
      <div className="mx-auto max-w-5xl px-4 py-12 sm:px-6">
        <div className="mb-2 text-sm text-stone-400">
          <Link href="/killtony/episodes" className="hover:text-stone-600 transition-colors">
            ← Episodes
          </Link>
        </div>

        <div className="mb-6">
          <p className="text-sm font-medium text-primary uppercase tracking-wide">
            Episode {episode.number}
          </p>
          <h1 className="mt-1 text-3xl font-bold text-stone-900">
            {episode.title || `Kill Tony #${episode.number}`}
          </h1>
          <p className="mt-1 text-stone-400">{episode.date ?? "Date unknown"}</p>
        </div>

        <div className="mb-6">
          <VideoEmbed youtubeId={episode.youtube_id} startSeconds={0} className="max-w-sm" />
        </div>

        {/* Episode stats */}
        <div className="mb-8 flex flex-wrap gap-2">
          <Stat label="Duration" value={fmtDuration(episode.duration_seconds)} />
          <Stat label="Sets" value={sets.length} />
          <Stat label="Bucket pulls" value={episode.bucket_pull_count} />
          <Stat label="Golden tickets" value={episode.golden_ticket_count} />
          <Stat label="Regulars" value={episode.regular_count} />
          <Stat label="Big joke books" value={episode.large_joke_book_count} />
        </div>

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
