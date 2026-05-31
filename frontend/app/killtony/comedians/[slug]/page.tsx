import { notFound } from "next/navigation";
import Link from "next/link";
import { getServerComedian } from "@/lib/serverApi";
import type { ComedianAttribute, SetInComedian } from "@/lib/serverApi";
import ComedianImage from "@/components/ComedianImage";

type Props = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Props) {
  const { slug } = await params;
  const comedian = await getServerComedian(slug);
  if (!comedian) return { title: "Comedian Not Found | PunchNotes" };
  return { title: `${comedian.name} — Kill Tony | PunchNotes` };
}

function fmt2(n: number | null): string {
  return n == null ? "—" : n.toFixed(2);
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

const jokeBookBadgeDark: Record<string, string> = {
  small:  "bg-stone-700 text-stone-300",
  medium: "bg-amber-900/60 text-amber-300",
  large:  "bg-red-900/60 text-red-300",
};

function SetCard({ set }: { set: SetInComedian }) {
  return (
    <Link
      href={`/killtony/sets/${set.id}`}
      className="group block rounded-xl border border-stone-200 bg-white p-5 transition-all hover:border-primary/40 hover:shadow-sm"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs font-medium uppercase tracking-wide text-stone-400 mb-0.5">
            Set {set.set_number}
          </p>
          <p className="font-semibold text-stone-900 group-hover:text-primary transition-colors leading-snug line-clamp-2">
            KT #{set.episode.number} — {set.episode.title?.replace(/^KT\s*#\d+\s*[-–]\s*/i, "") ?? ""}
          </p>
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

      <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-stone-400">
        <span>
          Setup/punch ratio{" "}
          <span className="font-medium text-stone-600">{fmt2(set.hit_ratio)}</span>
        </span>
        <span>
          Punch/tag ratio{" "}
          <span className="font-medium text-stone-600">{fmt2(set.punchline_tag_ratio)}</span>
        </span>
      </div>
    </Link>
  );
}

export default async function ComedianDetailPage({ params }: Props) {
  const { slug } = await params;
  const comedian = await getServerComedian(slug);
  if (!comedian) notFound();

  const ct = getAppearanceType(comedian.attributes);
  const sets = [...(comedian.sets ?? [])].sort(
    (a, b) => b.episode.number - a.episode.number
  );

  return (
    <div className="bg-white min-h-screen">
      {/* Dark hero */}
      <div className="bg-stone-900 text-white">
        <div className="mx-auto max-w-5xl px-6 py-10">
          <div className="flex gap-8 items-start">

            <ComedianImage
              imageUrl={comedian.image_url}
              name={comedian.name}
              className="hidden aspect-video w-36 shrink-0 rounded-lg bg-stone-800 shadow-xl ring-1 ring-white/10 sm:block md:w-48"
            />

            {/* Info */}
            <div className="flex-1 min-w-0">
              <h1 className="text-3xl md:text-4xl font-bold text-white mb-1">
                {comedian.name}
              </h1>

              {/* Type + joke book badges */}
              <div className="flex flex-wrap gap-1.5 mb-5">
                {ct && (
                  <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${comedianTypeBadge[ct]}`}>
                    {comedianTypeLabel[ct]}
                  </span>
                )}
                {comedian.has_small_joke_book && (
                  <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${jokeBookBadgeDark.small}`}>
                    Small Joke Book
                  </span>
                )}
                {comedian.has_medium_joke_book && (
                  <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${jokeBookBadgeDark.medium}`}>
                    Medium Joke Book
                  </span>
                )}
                {comedian.has_large_joke_book && (
                  <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${jokeBookBadgeDark.large}`}>
                    Large Joke Book
                  </span>
                )}
              </div>

              {/* Stats */}
              <p className="text-sm text-stone-400">
                <span className="text-white">{comedian.set_count}</span> set{comedian.set_count !== 1 ? "s" : ""}
                <span className="mx-2 text-stone-700">·</span>
                <span className="text-white">{fmt2(comedian.avg_bits_per_set)}</span> bits/set
                <span className="mx-2 text-stone-700">·</span>
                <span className="text-white">{fmt2(comedian.avg_beats_per_set)}</span> beats/set
                <span className="mx-2 text-stone-700">·</span>
                <span className="text-white">{fmt2(comedian.avg_hit_ratio)}</span> setup/punch
                <span className="mx-2 text-stone-700">·</span>
                <span className="text-white">{fmt2(comedian.avg_punchline_tag_ratio)}</span> punch/tag
              </p>
            </div>

          </div>
        </div>
      </div>

      {/* Set history */}
      <div className="mx-auto max-w-5xl px-6 py-10">
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
