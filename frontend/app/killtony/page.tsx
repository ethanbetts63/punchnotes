import Link from "next/link";
import { getServerBits, getServerEpisodes, getServerComedians, getServerSet, getServerSets } from "@/lib/serverApi";
import FeaturedEpisodesCarousel from "@/components/FeaturedEpisodesCarousel";
import CuratedSetsSection from "@/components/CuratedSetsSection";
import BeatOfTheWeek from "@/components/BeatOfTheWeek";

export const metadata = {
  title: "Kill Tony — PunchPedia",
  description: "Structured comedy analytics for Kill Tony. Browse episodes, comedians, and jokes broken down by premise, mechanism, and audience response.",
};

const FEATURED_BEAT_SET_ID = "138";
const FEATURED_BEAT_BIT_INDEX = 3;
const FEATURED_BEAT_INDEX = 0;

export default async function KillTonyPage() {
  const [episodes, comedians, bits, sets, featuredBeatSet] = await Promise.all([
    getServerEpisodes(),
    getServerComedians(),
    getServerBits(),
    getServerSets(),
    getServerSet(FEATURED_BEAT_SET_ID),
  ]);

  const episodeCount = episodes?.length ?? 0;
  const comedianCount = comedians?.length ?? 0;
  const setCount = episodes?.reduce((sum, ep) => sum + (ep.set_count ?? 0), 0) ?? 0;
  const bitCount = bits?.length ?? 0;

  return (
    <div className="bg-white">
      {episodes && <FeaturedEpisodesCarousel episodes={episodes} />}

      {featuredBeatSet && (
        <BeatOfTheWeek
          set={featuredBeatSet}
          bitIndex={FEATURED_BEAT_BIT_INDEX}
          beatIndex={FEATURED_BEAT_INDEX}
        />
      )}

      {sets && <CuratedSetsSection sets={sets} />}

      {/* Stats */}
      <section className="border-b border-stone-200 bg-stone-50 py-10 px-4">
        <div className="mx-auto max-w-4xl">
          <dl className="grid grid-cols-2 gap-6 sm:grid-cols-4">
            {[
              { label: "Episodes", value: episodeCount || "—" },
              { label: "Comedians", value: comedianCount || "—" },
              { label: "Sets", value: setCount || "—" },
              { label: "Bits", value: bitCount || "—" },
            ].map(({ label, value }) => (
              <div key={label} className="text-center">
                <dt className="text-sm text-stone-500">{label}</dt>
                <dd className="mt-1 text-3xl font-bold text-stone-900">{value}</dd>
              </div>
            ))}
          </dl>
        </div>
      </section>

      {/* Nav tiles */}
      <section className="py-16 px-4">
        <div className="mx-auto max-w-4xl grid gap-6 sm:grid-cols-3">
          {[
            {
              href: "/killtony/episodes",
              title: "Episodes",
              description: "Every episode with its full lineup, dates, and set-by-set breakdown.",
            },
            {
              href: "/killtony/comedians",
              title: "Comedians",
              description: "Every comedian who has performed, with their career arc and joke book history.",
            },
            {
              href: "/killtony/jokes",
              title: "Jokes",
              description: "Search every joke by premise, topic, or mechanism type.",
            },
          ].map(({ href, title, description }) => (
            <Link
              key={href}
              href={href}
              className="group rounded-xl border border-stone-200 bg-white p-6 hover:border-primary/50 hover:shadow-sm transition-all"
            >
              <h2 className="text-lg font-semibold text-stone-900 group-hover:text-primary transition-colors">
                {title}
              </h2>
              <p className="mt-2 text-sm text-stone-500 leading-relaxed">{description}</p>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
