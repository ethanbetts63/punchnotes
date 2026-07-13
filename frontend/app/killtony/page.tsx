import Link from "next/link";
import BeatOfTheWeek from "@/components/BeatOfTheWeek";
import HowItWorksPanel from "@/components/HowItWorksPanel";
import KillTonyHero from "@/components/KillTonyHero";
import ComedianPlaylists from "@/components/ComedianPlaylists";
import VideoPlaylists from "@/components/VideoPlaylists";
import KillTonyOverview from "@/components/KillTonyOverview";
import MediaCarousel from "@/components/MediaCarousel";
import { getFeaturedBeatEntries } from "@/lib/featuredBeats";
import {
  getServerComedians,
  getServerSets,
  getServerVideo,
  getServerVideos,
} from "@/lib/serverApi";
import { SET_LISTS } from "@/lib/playlists";
import { setToTile } from "@/lib/tiles";

const MUST_WATCH_SETS = SET_LISTS.find((list) => list.id === "must-watch-sets")!;

const FEATURED_EPISODE_SLUG =
  "kill-tony-578-dave-attell-greg-fitzsimmons-ian-fidance--M7RsTBpU5xM";
import { buildMetadata, buildOrganizationSchema, buildWebSiteSchema } from "@/lib/seo";

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
  ...buildMetadata({
    title: "Kill Tony - PunchNotes",
    description:
      "Structured comedy analytics for Kill Tony. Browse episodes, comedians, and jokes broken down by mechanism, line structure, and audience response.",
    canonicalPath: "/killtony",
  }),
  verification: {
    google: "HLJ7Gj_HgQqq9tVk6emNp1EbT5W2yoYCAIwMbHYEf3E",
  },
};

export default async function KillTonyPage() {
  const [episodes, comedians, featuredBeatEntries, featuredEpisode, mustWatchSets] =
    await Promise.all([
      getServerVideos(),
      getServerComedians(),
      getFeaturedBeatEntries(),
      getServerVideo(FEATURED_EPISODE_SLUG),
      getServerSets(`slugs=${MUST_WATCH_SETS.slugs.join(",")}`),
    ]);

  return (
    <>
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{
        __html: JSON.stringify([buildOrganizationSchema(), buildWebSiteSchema()]),
      }}
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

      {mustWatchSets && mustWatchSets.length > 0 && (
        <section className="border-b border-stone-200 bg-white py-12">
          <div className="mx-auto max-w-6xl">
            <SectionHeader
              title="Sets"
              href="/killtony/sets"
              cta="See all sets"
            />
            <MediaCarousel
              title={MUST_WATCH_SETS.title}
              description={MUST_WATCH_SETS.description}
              items={mustWatchSets.map(setToTile)}
            />
          </div>
        </section>
      )}

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

      <KillTonyOverview featuredEpisode={featuredEpisode} />
    </div>
    </>
  );
}
