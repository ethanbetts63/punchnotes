import Link from "next/link";
import { getServerEpisodes, getServerComedians, getServerJokes } from "@/lib/serverApi";
import YoutubeThumbnail from "@/components/YoutubeThumbnail";

export const metadata = {
  title: "Kill Tony — PunchPedia",
  description: "Structured comedy analytics for Kill Tony. Browse episodes, comedians, and jokes broken down by premise, mechanism, and audience response.",
};

function fmtNumber(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

function fmtDuration(seconds: number | null): string {
  if (!seconds) return "-";
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  return h > 0 ? `${h}h ${m}m` : `${m}m`;
}

function fmtDate(date: string | null): string {
  if (!date) return "";
  return new Date(date).toLocaleDateString("en-AU", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export default async function KillTonyPage() {
  const [episodes, comedians, jokes] = await Promise.all([
    getServerEpisodes(),
    getServerComedians(),
    getServerJokes(),
  ]);

  const episodeCount = episodes?.length ?? 0;
  const comedianCount = comedians?.length ?? 0;
  const setCount = episodes?.reduce((sum, ep) => sum + (ep.set_count ?? 0), 0) ?? 0;
  const jokeCount = jokes?.length ?? 0;
  const latestEpisode = episodes
    ? [...episodes].sort((a, b) => b.number - a.number)[0]
    : null;
  const latestViewLikeRatio =
    latestEpisode?.view_count && latestEpisode.like_count != null && latestEpisode.view_count > 0
      ? `${((latestEpisode.like_count / latestEpisode.view_count) * 100).toFixed(1)}%`
      : null;

  return (
    <div className="bg-white">
      {/* Hero */}
      <section className="bg-stone-900 py-20 px-4">
        <div className="mx-auto max-w-4xl text-center">
          <h1 className="text-4xl font-bold tracking-tight text-white sm:text-5xl">
            Kill Tony
          </h1>
          <p className="mt-4 text-lg text-stone-400 max-w-2xl mx-auto">
            Every set. Every joke. Broken down by premise, mechanism, and what actually made the audience laugh.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <Link
              href="/killtony/comedians"
              className="rounded-md bg-primary px-5 py-2.5 text-sm font-semibold text-white hover:bg-primary/90 transition-colors"
            >
              Browse Comedians
            </Link>
            <Link
              href="/killtony/episodes"
              className="rounded-md bg-white/10 px-5 py-2.5 text-sm font-semibold text-white hover:bg-white/20 transition-colors"
            >
              Browse Episodes
            </Link>
          </div>
        </div>
      </section>

      {latestEpisode && (
        <section className="border-b border-stone-200 bg-white px-4 py-12">
          <div className="mx-auto max-w-5xl">
            <div className="mb-5 flex items-end justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-primary">
                  Most recent episode
                </p>
                <h2 className="mt-1 text-2xl font-bold tracking-tight text-stone-900">
                  Start with the latest pull
                </h2>
              </div>
              <Link
                href="/killtony/episodes"
                className="hidden text-sm font-semibold text-stone-500 transition-colors hover:text-stone-900 sm:block"
              >
                All episodes
              </Link>
            </div>

            <div className="overflow-hidden rounded-lg border border-stone-200 bg-stone-950 text-white shadow-sm">
              <div className="grid md:grid-cols-[minmax(0,1.05fr)_minmax(0,1fr)]">
                <Link
                  href={`/killtony/episodes/${latestEpisode.id}`}
                  className="group relative block min-h-56 bg-stone-900 md:min-h-full"
                >
                  <YoutubeThumbnail
                    videoId={latestEpisode.youtube_id}
                    alt={latestEpisode.title || `Kill Tony #${latestEpisode.number}`}
                    className="h-full min-h-56 w-full bg-stone-950"
                    fit="contain"
                  />
                  <div className="absolute inset-0 bg-black/10 transition-colors group-hover:bg-black/0" />
                  <div className="absolute left-4 top-4 rounded-md bg-black/75 px-2.5 py-1 text-xs font-semibold text-white">
                    KT #{latestEpisode.number}
                  </div>
                </Link>

                <div className="p-6 sm:p-7">
                  <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs font-medium uppercase tracking-wide text-stone-400">
                    <span>Episode {latestEpisode.number}</span>
                    {latestEpisode.date && <span>{fmtDate(latestEpisode.date)}</span>}
                  </div>

                  <h3 className="mt-3 text-2xl font-bold leading-tight tracking-tight text-white sm:text-3xl">
                    <Link
                      href={`/killtony/episodes/${latestEpisode.id}`}
                      className="transition-colors hover:text-yellow-300"
                    >
                      {latestEpisode.title || `Kill Tony #${latestEpisode.number}`}
                    </Link>
                  </h3>

                  <dl className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3">
                    {[
                      { label: "Duration", value: fmtDuration(latestEpisode.duration_seconds) },
                      { label: "Sets", value: latestEpisode.set_count },
                      { label: "Bucket pulls", value: latestEpisode.bucket_pull_count },
                      { label: "Regulars", value: latestEpisode.regular_count },
                      { label: "Golden tickets", value: latestEpisode.golden_ticket_count },
                      { label: "Big joke books", value: latestEpisode.large_joke_book_count },
                    ].map(({ label, value }) => (
                      <div key={label} className="rounded-md border border-white/10 bg-white/5 px-3 py-2">
                        <dt className="text-[11px] text-stone-500">{label}</dt>
                        <dd className="mt-0.5 text-sm font-semibold tabular-nums text-white">{value}</dd>
                      </div>
                    ))}
                  </dl>

                  {(latestEpisode.view_count != null ||
                    latestEpisode.like_count != null ||
                    latestEpisode.comment_count != null) && (
                    <div className="mt-4 flex flex-wrap gap-x-4 gap-y-1 text-sm text-stone-400">
                      {latestEpisode.view_count != null && (
                        <span><span className="text-white">{fmtNumber(latestEpisode.view_count)}</span> views</span>
                      )}
                      {latestEpisode.like_count != null && (
                        <span><span className="text-white">{fmtNumber(latestEpisode.like_count)}</span> likes</span>
                      )}
                      {latestEpisode.comment_count != null && (
                        <span><span className="text-white">{fmtNumber(latestEpisode.comment_count)}</span> comments</span>
                      )}
                      {latestViewLikeRatio && (
                        <span><span className="text-white">{latestViewLikeRatio}</span> view/like ratio</span>
                      )}
                    </div>
                  )}

                  <div className="mt-6 flex flex-wrap gap-3">
                    <Link
                      href={`/killtony/episodes/${latestEpisode.id}`}
                      className="rounded-md bg-primary px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-primary/90"
                    >
                      Open breakdown
                    </Link>
                    {latestEpisode.youtube_id && (
                      <a
                        href={`https://www.youtube.com/watch?v=${latestEpisode.youtube_id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="rounded-md bg-white/10 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-white/20"
                      >
                        Watch episode
                      </a>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Stats */}
      <section className="border-b border-stone-200 bg-stone-50 py-10 px-4">
        <div className="mx-auto max-w-4xl">
          <dl className="grid grid-cols-2 gap-6 sm:grid-cols-4">
            {[
              { label: "Episodes", value: episodeCount || "—" },
              { label: "Comedians", value: comedianCount || "—" },
              { label: "Sets", value: setCount || "—" },
              { label: "Jokes", value: jokeCount || "—" },
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
