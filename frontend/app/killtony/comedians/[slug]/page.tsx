import { notFound } from "next/navigation";
import Link from "next/link";
import { getServerComedian } from "@/lib/serverApi";
import type { ComedianType, SetInComedian } from "@/lib/serverApi";

type Props = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Props) {
  const { slug } = await params;
  const comedian = await getServerComedian(slug);
  if (!comedian) return { title: "Comedian Not Found | JokeScore" };
  return { title: `${comedian.name} — Kill Tony | JokeScore` };
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

const jokeBookColor: Record<string, string> = {
  small: "bg-stone-100 text-stone-600",
  medium: "bg-amber-100 text-amber-700",
  large: "bg-red-100 text-primary",
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

function SetCard({ set }: { set: SetInComedian }) {
  return (
    <div className="rounded-xl border border-stone-200 bg-white p-5">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs font-medium uppercase tracking-wide text-stone-400 mb-0.5">
            Set {set.set_number}
          </p>
          <Link
            href={`/killtony/episodes/${set.episode.id}`}
            className="font-semibold text-stone-900 hover:text-primary transition-colors leading-snug line-clamp-2"
          >
            KT #{set.episode.number} — {set.episode.title?.replace(/^KT\s*#\d+\s*[-–]\s*/i, "") ?? ""}
          </Link>
          {set.episode.date && (
            <p className="mt-0.5 text-xs text-stone-400">{set.episode.date}</p>
          )}
        </div>
        {set.joke_book && (
          <span className={`shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium ${jokeBookColor[set.joke_book]}`}>
            {jokeBookLabel[set.joke_book]}
          </span>
        )}
      </div>

      {(set.hit_ratio != null || set.punchline_tag_ratio != null) && (
        <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-stone-400">
          {set.hit_ratio != null && (
            <span>
              Setup/punch ratio{" "}
              <span className="font-medium text-stone-600">{fmt2(set.hit_ratio)}</span>
            </span>
          )}
          {set.punchline_tag_ratio != null && (
            <span>
              Punch/tag ratio{" "}
              <span className="font-medium text-stone-600">{fmt2(set.punchline_tag_ratio)}</span>
            </span>
          )}
        </div>
      )}

      <div className="mt-3 flex justify-end">
        <Link
          href={`/killtony/sets/${set.id}`}
          className="text-xs font-medium text-stone-400 hover:text-primary transition-colors"
        >
          View set →
        </Link>
      </div>
    </div>
  );
}

export default async function ComedianDetailPage({ params }: Props) {
  const { slug } = await params;
  const comedian = await getServerComedian(slug);
  if (!comedian) notFound();

  const ct = comedian.comedian_type as ComedianType | "";
  const sets = [...(comedian.sets ?? [])].sort(
    (a, b) => b.episode.number - a.episode.number
  );

  return (
    <div className="bg-white min-h-screen">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <div className="mb-2 text-sm text-stone-400">
          <Link href="/killtony/comedians" className="hover:text-stone-600 transition-colors">
            ← Comedians
          </Link>
        </div>

        {/* Header */}
        <div className="mb-6">
          <div className="flex flex-wrap items-center gap-2 mb-1">
            <h1 className="text-3xl font-bold text-stone-900">{comedian.name}</h1>
            {ct && (
              <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${comedianTypeColor[ct]}`}>
                {comedianTypeLabel[ct]}
              </span>
            )}
          </div>
          {(comedian.has_small_joke_book || comedian.has_medium_joke_book || comedian.has_large_joke_book) && (
            <div className="mt-2 flex flex-wrap gap-1.5">
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
                  Large Joke Book
                </span>
              )}
            </div>
          )}
        </div>

        {/* Stats */}
        <div className="mb-10 flex flex-wrap gap-2">
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

        {/* Set history */}
        <h2 className="mb-4 text-lg font-semibold text-stone-900">Set history</h2>
        {sets.length === 0 ? (
          <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
            <p className="text-stone-500">No sets indexed yet.</p>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2">
            {sets.map((set) => (
              <SetCard key={set.id} set={set} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
