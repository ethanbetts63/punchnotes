import Link from "next/link";
import BeatOfTheWeek from "@/components/BeatOfTheWeek";
import HowItWorksPanel from "@/components/HowItWorksPanel";
import KillTonyHero from "@/components/KillTonyHero";
import ComedianPlaylists from "@/components/ComedianPlaylists";
import VideoPlaylists from "@/components/VideoPlaylists";
import { getFeaturedBeatEntries } from "@/lib/featuredBeats";
import { getServerComedians, getServerVideos } from "@/lib/serverApi";
import { buildWebSiteSchema } from "@/lib/seo";

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
  verification: {
    google: "HLJ7Gj_HgQqq9tVk6emNp1EbT5W2yoYCAIwMbHYEf3E",
  },
};

export default async function KillTonyPage() {
  const [episodes, comedians, featuredBeatEntries] = await Promise.all([
    getServerVideos(),
    getServerComedians(),
    getFeaturedBeatEntries(),
  ]);

  return (
    <>
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(buildWebSiteSchema()) }}
    />
    <div className="bg-white">
      <KillTonyHero />

      <section className="border-b border-stone-200 bg-white px-4 py-8">
        <div className="mx-auto grid max-w-6xl grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="order-2 min-w-0 lg:order-1 lg:col-span-1">
            <div className="-mx-4 lg:mx-0">
              <HowItWorksPanel />
            </div>
          </div>
          <div className="order-1 min-w-0 lg:order-2 lg:col-span-2">
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
              cta="See all episodes"
            />
            <VideoPlaylists episodes={episodes} limit={2} />
          </div>
        </section>
      )}

      {comedians && (
        <section className="border-b border-stone-200 bg-stone-50 py-12">
          <div className="mx-auto max-w-6xl">
            <SectionHeader
              title="Comedians"
              href="/killtony/comedians"
              cta="See all comedians"
            />
            <ComedianPlaylists comedians={comedians} limit={2} />
          </div>
        </section>
      )}
    </div>
    </>
  );
}
