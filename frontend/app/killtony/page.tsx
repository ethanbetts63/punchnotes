import Link from "next/link";
import BeatOfTheWeek from "@/components/BeatOfTheWeek";
import HowItWorksPanel from "@/components/HowItWorksPanel";
import KillTonyHero from "@/components/KillTonyHero";
import ComedianPlaylists from "@/page_components/ComedianPlaylists";
import EpisodePlaylists from "@/page_components/EpisodePlaylists";
import { getFeaturedBeatEntries } from "@/lib/featuredBeats";
import { getServerComedians, getServerEpisodes } from "@/lib/serverApi";

function SectionHeader({
  title,
  href,
  cta,
}: {
  title: string;
  href: string;
  cta: string;
}) {
  return (
    <div className="mb-6 flex items-end justify-between gap-4 px-6">
      <div className="max-w-2xl">
        <h2 className="text-2xl font-bold tracking-tight text-stone-950 sm:text-3xl">
          {title}
        </h2>
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
          <div className="lg:col-span-1">
            <HowItWorksPanel />
          </div>
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
        </div>
      </section>

      {episodes && (
        <section className="border-b border-stone-200 bg-white py-12">
          <div className="mx-auto max-w-6xl">
            <SectionHeader
              title="Episode Playlists"
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
              title="Comic Playlists"
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
