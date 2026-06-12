import Link from "next/link";
import BeatOfTheWeek from "@/components/BeatOfTheWeek";
import ComedianPlaylists from "@/page_components/ComedianPlaylists";
import EpisodePlaylists from "@/page_components/EpisodePlaylists";
import { BIT_LISTS } from "@/lib/playlists";
import { getServerBits, getServerComedians, getServerEpisodes, getServerSet } from "@/lib/serverApi";

const FEATURED_BIT_CANDIDATES = BIT_LISTS.flatMap((list) => list.ids);

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
  const [episodes, comedians, bits] = await Promise.all([
    getServerEpisodes(),
    getServerComedians(),
    getServerBits(),
  ]);

  const featuredBit =
    bits?.find((bit) => FEATURED_BIT_CANDIDATES.includes(bit.id)) ??
    bits?.find((bit) => bit.set_id != null);
  const featuredBeatSet = featuredBit ? await getServerSet(String(featuredBit.set_id)) : null;
  const featuredBeatBitIndex = featuredBeatSet?.bits.findIndex((bit) => bit.id === featuredBit?.id) ?? -1;
  const hasFeaturedBeat =
    featuredBeatSet != null &&
    featuredBeatBitIndex >= 0 &&
    featuredBeatSet.bits[featuredBeatBitIndex]?.beats.length > 0;

  return (
    <div className="bg-white">
      {hasFeaturedBeat && featuredBeatSet && (
        <BeatOfTheWeek set={featuredBeatSet} bitIndex={featuredBeatBitIndex} beatIndex={0} />
      )}

      {episodes && (
        <section className="border-b border-stone-200 bg-white py-12">
          <div className="mx-auto max-w-6xl">
            <SectionHeader
              eyebrow="Episode Playlists"
              title="Start with a strong entry point into the archive."
              description="Lead with Kill Tony lore and all-star guests here, then let the full archive page handle the rest."
              href="/killtony/episodes"
              cta="See more episode playlists"
            />
            <EpisodePlaylists episodes={episodes} limit={2} />
          </div>
        </section>
      )}

      {comedians && (
        <section className="border-b border-stone-200 bg-stone-50 py-12">
          <div className="mx-auto max-w-6xl">
            <SectionHeader
              eyebrow="Comedian Playlists"
              title="Browse the roster through grouped lists, not just one giant index."
              description="Use regulars and golden ticket winners as the two homepage comedian entry points."
              href="/killtony/comedians"
              cta="See more comedian playlists"
            />
            <ComedianPlaylists comedians={comedians} limit={2} />
          </div>
        </section>
      )}
    </div>
  );
}
