import Link from "next/link";
import BeatOfTheWeek, { type BeatOfTheWeekEntry } from "@/components/BeatOfTheWeek";
import HowItWorksPanel from "@/components/HowItWorksPanel";
import KillTonyHero from "@/components/KillTonyHero";
import ComedianPlaylists from "@/page_components/ComedianPlaylists";
import EpisodePlaylists from "@/page_components/EpisodePlaylists";
import { BIT_LISTS } from "@/lib/playlists";
import { getServerBits, getServerComedians, getServerEpisodes, getServerSet } from "@/lib/serverApi";

const FEATURED_BIT_CANDIDATES = BIT_LISTS.flatMap((list) => list.ids);
const FEATURED_BEAT_LIMIT = 5;

async function getFeaturedBeatEntries() {
  const bits = await getServerBits();
  if (!bits?.length) return [];

  const priorityBits = [
    ...bits.filter((bit) => FEATURED_BIT_CANDIDATES.includes(bit.id)),
    ...bits.filter((bit) => !FEATURED_BIT_CANDIDATES.includes(bit.id)),
  ].filter((bit) => bit.set_id != null);

  const candidateBits = priorityBits.slice(0, FEATURED_BEAT_LIMIT * 3);
  const uniqueSetIds = [...new Set(candidateBits.map((bit) => bit.set_id))];
  const sets = await Promise.all(uniqueSetIds.map((setId) => getServerSet(String(setId))));
  const setById = new Map(
    sets
      .filter((set): set is NonNullable<typeof set> => set != null)
      .map((set) => [set.id, set])
  );

  const entries: BeatOfTheWeekEntry[] = [];
  for (const bit of candidateBits) {
    const set = setById.get(bit.set_id);
    if (!set) continue;

    const bitIndex = set.bits.findIndex((setBit) => setBit.id === bit.id);
    if (bitIndex < 0) continue;

    const beatCount = set.bits[bitIndex]?.beats.length ?? 0;
    if (beatCount === 0) continue;

    entries.push({ set, bitIndex, beatIndex: 0 });
    if (entries.length >= FEATURED_BEAT_LIMIT) break;
  }

  return entries;
}

function SectionHeader({
  eyebrow,
  title,
  description,
  href,
  cta,
}: {
  eyebrow: string;
  title: string;
  description: string;
  href: string;
  cta: string;
}) {
  return (
    <div className="mb-6 flex items-end justify-between gap-4 px-6">
      <div className="max-w-2xl">
        <p className="text-xs font-bold uppercase tracking-[0.24em] text-primary">{eyebrow}</p>
        <h2 className="mt-2 text-2xl font-bold tracking-tight text-stone-950 sm:text-3xl">{title}</h2>
        <p className="mt-2 text-sm leading-relaxed text-stone-600">{description}</p>
      </div>
      <Link
        href={href}
        className="shrink-0 text-sm font-semibold text-stone-500 transition-colors hover:text-primary"
      >
        {cta}
      </Link>
    </div>
  );
}

export const metadata = {
  title: "Kill Tony - PunchNotes",
  description:
    "Structured comedy analytics for Kill Tony. Browse episodes, comedians, and jokes broken down by premise, mechanism, and audience response.",
};

export default async function KillTonyPage() {
  const [episodes, comedians, featuredBeatEntries] = await Promise.all([
    getServerEpisodes(),
    getServerComedians(),
    getFeaturedBeatEntries(),
  ]);

  return (
    <div className="bg-white">
      <KillTonyHero />

      <section className="border-b border-stone-200 bg-white px-4 py-8">
        <div className="mx-auto grid max-w-6xl gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            {featuredBeatEntries.length > 0 && (
              <BeatOfTheWeek
                set={featuredBeatEntries[0].set}
                bitIndex={featuredBeatEntries[0].bitIndex}
                beatIndex={featuredBeatEntries[0].beatIndex}
                entries={featuredBeatEntries.slice(1)}
              />
            )}
          </div>
          <div className="lg:col-span-1">
            <HowItWorksPanel />
          </div>
        </div>
      </section>

      {episodes && (
        <section className="border-b border-stone-200 bg-white py-12">
          <div className="mx-auto max-w-6xl">
            <SectionHeader
              eyebrow="Episodes"
              title="Open an episode, then drill into the full night."
              description="Click any episode and you will land on that episode's page with the full lineup of sets and comedians from that night."
              href="/killtony/episodes"
              cta="See more "
            />
            <EpisodePlaylists episodes={episodes} limit={2} />
          </div>
        </section>
      )}

      {comedians && (
        <section className="border-b border-stone-200 bg-stone-50 py-12">
          <div className="mx-auto max-w-6xl">
            <SectionHeader
              eyebrow="Comedians"
              title="Jump into a comic's full run on the show."
              description="Click any comedian to see all of their Kill Tony sets across every episode in the archive."
              href="/killtony/comedians"
              cta="See all comics"
            />
            <ComedianPlaylists comedians={comedians} limit={2} />
          </div>
        </section>
      )}
    </div>
  );
}
