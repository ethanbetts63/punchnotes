import type { Video, VideoDetail } from "@/lib/serverApi";
import { fmtDate, getEpisodeGuestLabel } from "@/lib/killTonyDisplay";
import YoutubeThumbnail from "@/components/YoutubeThumbnail";
import SearchResultTile from "@/components/SearchResultTile";

export default function KillTonyOverview({
  featuredEpisode,
}: {
  featuredEpisode: Video | VideoDetail | null;
}) {
  return (
    <section className="border-b border-stone-200 bg-white py-12">
      <div className="mx-auto grid max-w-6xl grid-cols-1 gap-10 px-6 lg:grid-cols-5 lg:gap-12">
        <div className="lg:col-span-3">
          <h2 className="text-2xl font-bold tracking-tight text-stone-950 sm:text-3xl">
            What is Kill Tony?
          </h2>
          <div className="mt-5 space-y-4 text-base leading-relaxed text-stone-600">
            <p>
              Kill Tony is the world&rsquo;s biggest live comedy podcast, hosted by
              Tony Hinchcliffe alongside co-host and producer Brian Redban. The
              format is simple and brutal: aspiring comedians drop their name in a
              bucket, get pulled at random, and perform roughly one minute of
              stand-up comedy. Then they face the panel &mdash;
              Tony, Redban and a rotating cast of guest comics
              &mdash; for an interview that&rsquo;s often funnier than the set
              itself. Since its 2013 debut as a Deathsquad pilot at the Comedy
              Store in Los Angeles, the show has turned open-mic unknowns into
              breakout regulars. The highs are incredibly high, the lows are devastatingly 
              low, and we wouldn't want it any other way.
            </p>
            <p>
              The show began in 2013 at the Comedy Store in Los Angeles its since 
              moved to Austin in 2021 and now tapes weekly out of the
              Comedy Mothership, but it&rsquo;s the live spectacle that made it a
              phenomenon &mdash; selling out Madison Square Garden in 2024, 
              landing a run of Netflix specials, and building a devoted
              community around its regulars, running bits, and golden-ticket
              moments. PunchNotes is a fan-made archive that breaks it all down:
              every set, comedian, and joke, searchable and annotated.
            </p>
          </div>
        </div>

        {featuredEpisode && (
          <div className="lg:col-span-2">
            <p className="text-[11px] font-bold uppercase tracking-[0.2em] text-primary">
              Start here
            </p>
            <h3 className="mt-2 text-lg font-bold tracking-tight text-stone-950">
              One of our favorite episodes of all time
            </h3>
            <div className="mt-4">
              <SearchResultTile
                href={`/killtony/episodes/${featuredEpisode.slug}`}
                eyebrow={`Episode ${featuredEpisode.number}`}
                title={getEpisodeGuestLabel(
                  featuredEpisode,
                  `Kill Tony #${featuredEpisode.number}`,
                )}
                subtitle={fmtDate(featuredEpisode.date) || undefined}
                image={
                  <YoutubeThumbnail
                    videoId={featuredEpisode.youtube_id}
                    alt={`Kill Tony #${featuredEpisode.number}`}
                    className="absolute inset-0 h-full w-full"
                  />
                }
              />
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
