import { notFound } from "next/navigation";
import { getServerVideo } from "@/lib/serverApi";
import type { SetInVideo } from "@/lib/serverApi";
import { fmt2, fmtSeconds, fmtDuration, fmtCompact, fmtDate, getEpisodeGuests, getEpisodeGuestLabel, getJokeBookSize, jokeBookLabel } from "@/lib/killTonyDisplay";
import { formatAttributeLabels } from "@/lib/attributes";
import SetImage from "@/components/SetImage";
import SearchResultTile from "@/components/SearchResultTile";
import Breadcrumbs from "@/components/Breadcrumbs";
import { SITE_URL, buildBreadcrumbSchema, buildMetadata } from "@/lib/seo";

type Props = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Props) {
  const { slug } = await params;
  const episode = await getServerVideo(slug);
  if (!episode) return { title: "Episode Not Found | PunchNotes" };
  const guests = getEpisodeGuests(episode);
  const guestLabel = guests.length > 0 ? guests.join(" + ") : getEpisodeGuestLabel(episode, `Episode ${episode.number}`);
  const setCount = episode.sets?.length ?? 0;
  const descriptionParts = [
    `Kill Tony #${episode.number}${guests.length > 0 ? ` with ${guestLabel}` : ""}`,
    episode.date ? `aired ${fmtDate(episode.date)}` : null,
    `with ${setCount} indexed set${setCount !== 1 ? "s" : ""}`,
    `${episode.bucket_pull_count} bucket pull${episode.bucket_pull_count !== 1 ? "s" : ""}`,
    `${episode.regular_count} regular${episode.regular_count !== 1 ? "s" : ""}`,
  ].filter(Boolean);

  return buildMetadata({
    title: `Kill Tony #${episode.number}${guests.length > 0 ? ` with ${guestLabel}` : ""} | PunchNotes`,
    description: `${descriptionParts.join(", ")}. Browse PunchNotes set metrics, comedians, timestamps, and joke book flags for this episode.`,
    canonicalPath: `/killtony/episodes/${episode.slug}`,
  });
}

type EpisodeDetail = NonNullable<Awaited<ReturnType<typeof getServerVideo>>>;

function toIsoDuration(seconds: number | null): string | undefined {
  if (!seconds) return undefined;
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  return `PT${h ? `${h}H` : ""}${m ? `${m}M` : ""}${s ? `${s}S` : ""}`;
}

function joinNames(names: string[]): string {
  if (names.length <= 2) return names.join(" and ");
  return `${names.slice(0, -1).join(", ")}, and ${names[names.length - 1]}`;
}

function buildEpisodeSummary(episode: EpisodeDetail): string {
  const sets = episode.sets ?? [];
  const guests = getEpisodeGuests(episode);
  const guestText = guests.length > 0 ? ` with ${joinNames(guests)}` : "";
  const dateText = episode.date ? ` aired on ${fmtDate(episode.date)}` : "";
  const featuredComedians = sets.slice(0, 5).map((set) => set.comedian.name);
  const comedianText = featuredComedians.length > 0
    ? ` Indexed sets include ${joinNames(featuredComedians)}${sets.length > featuredComedians.length ? ", and more" : ""}.`
    : "";

  return `Kill Tony #${episode.number}${guestText}${dateText}. PunchNotes indexes ${sets.length} set${sets.length !== 1 ? "s" : ""} from this episode, including ${episode.bucket_pull_count} bucket pull${episode.bucket_pull_count !== 1 ? "s" : ""}, ${episode.regular_count} regular${episode.regular_count !== 1 ? "s" : ""}, ${episode.golden_ticket_count} golden ticket${episode.golden_ticket_count !== 1 ? "s" : ""}, and ${episode.large_joke_book_count} big joke book set${episode.large_joke_book_count !== 1 ? "s" : ""}.${comedianText}`;
}

function buildEpisodeSchema(episode: EpisodeDetail): object {
  const url = `${SITE_URL}/killtony/episodes/${episode.slug}`;
  const youtubeUrl = episode.youtube_id ? `https://www.youtube.com/watch?v=${episode.youtube_id}` : undefined;
  const duration = toIsoDuration(episode.duration_seconds);

  return {
    '@context': 'https://schema.org',
    '@graph': [
      buildBreadcrumbSchema([
        { name: 'Kill Tony', item: `${SITE_URL}/killtony` },
        { name: 'Episodes', item: `${SITE_URL}/killtony/episodes` },
        { name: `Kill Tony #${episode.number}`, item: url },
      ]),
      {
        '@type': 'TVEpisode',
        '@id': `${url}#episode`,
        name: episode.title || `Kill Tony #${episode.number}`,
        url,
        episodeNumber: episode.number,
        description: buildEpisodeSummary(episode),
        ...(episode.date ? { datePublished: episode.date } : {}),
        ...(duration ? { duration } : {}),
        ...(youtubeUrl ? { sameAs: youtubeUrl } : {}),
        partOfSeries: {
          '@type': 'TVSeries',
          name: 'Kill Tony',
        },
        mainEntity: {
          '@type': 'ItemList',
          name: `Kill Tony #${episode.number} indexed sets`,
          numberOfItems: episode.sets?.length ?? 0,
          itemListElement: (episode.sets ?? []).map((set, index) => ({
            '@type': 'ListItem',
            position: index + 1,
            item: {
              '@type': 'CreativeWork',
              name: `${set.comedian.name} set`,
              url: `${SITE_URL}/killtony/sets/${set.slug}`,
              isPartOf: { '@id': `${url}#episode` },
            },
          })),
        },
      },
    ],
  };
}

function SetTile({
  set,
  episodeNumber,
  episodeTitle,
  youtubeId,
}: {
  set: SetInVideo;
  episodeNumber: number;
  episodeTitle: string;
  youtubeId: string | null;
}) {
  const jokeBook = getJokeBookSize(set.attributes);
  const attributes = formatAttributeLabels(set.comedian.attributes);
  return (
    <SearchResultTile
      href={`/killtony/sets/${set.slug}`}
      eyebrow={`KT #${episodeNumber}`}
      title={set.comedian.name}
      subtitle={episodeTitle}
      image={
        <SetImage
          imageUrl={set.image_url}
          fallbackVideoId={youtubeId}
          alt={`${set.comedian.name} set image`}
          className="absolute inset-0 h-full w-full"
        />
      }
      meta={
        <>
          {fmtSeconds(set.start_seconds)}
          {attributes ? ` / ${attributes}` : ""}
        </>
      }
      stats={[
        { label: "Bits", value: set.bit_count },
        { label: "Punch density", value: fmt2(set.punch_density) },
        { label: "Tag density", value: fmt2(set.tag_density) },
      ]}
      badges={
        jokeBook ? (
          <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-bold text-amber-700">
            {jokeBookLabel[jokeBook]}
          </span>
        ) : undefined
      }
    />
  );
}

export default async function EpisodeDetailPage({ params }: Props) {
  const { slug } = await params;
  const episode = await getServerVideo(slug);
  if (!episode) notFound();

  const sets = episode.sets ?? [];
  const viewLikeRatio =
    episode.view_like_ratio != null
      ? episode.view_like_ratio.toFixed(1)
      : null;
  const schema = buildEpisodeSchema(episode);

  return (
    <>
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
    />
    <div className="bg-white min-h-screen">
      {/* Dark hero */}
      <div className="bg-stone-900 text-white">
        <div className="mx-auto max-w-5xl px-6 py-10">
          <Breadcrumbs
            tone="dark"
            className="mb-6"
            items={[
              { label: "Kill Tony", href: "/killtony" },
              { label: "Episodes", href: "/killtony/episodes" },
              { label: `#${episode.number}` },
            ]}
          />
          <div className="flex gap-8 items-start">

            {/* YouTube thumbnail */}
            {episode.youtube_id && (
              <div className="hidden sm:block w-36 md:w-48 shrink-0">
                <a
                  href={`https://www.youtube.com/watch?v=${episode.youtube_id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block rounded-lg overflow-hidden shadow-xl ring-1 ring-white/10 hover:ring-yellow-400/50 transition-all group relative"
                >
                  <img
                    src={`https://img.youtube.com/vi/${episode.youtube_id}/hqdefault.jpg`}
                    alt={`Episode ${episode.number} thumbnail`}
                    className="w-full aspect-video object-cover"
                  />
                  <div className="absolute inset-0 flex items-center justify-center bg-black/30 opacity-0 group-hover:opacity-100 transition-opacity">
                    <div className="w-10 h-10 rounded-full bg-white/90 flex items-center justify-center">
                      <svg className="w-4 h-4 text-stone-900 ml-0.5" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M6.3 2.841A1.5 1.5 0 004 4.11v11.78a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.841z" />
                      </svg>
                    </div>
                  </div>
                </a>
                {episode.date && (
                  <p className="mt-2 text-xs text-stone-500">{episode.date}</p>
                )}
              </div>
            )}

            {/* Info */}
            <div className="flex-1 min-w-0">
              <h1 className="text-3xl md:text-4xl font-bold text-white mb-1">
                {episode.title || `Kill Tony #${episode.number}`}
              </h1>

              <p className="text-stone-400 text-sm mb-5">
                Episode {episode.number}
                {episode.date ? ` · ${episode.date}` : ""}
              </p>

              <p className="text-sm text-stone-400">
                <span className="text-white">{sets.length}</span> set{sets.length !== 1 ? "s" : ""}
                <span className="mx-2 text-stone-700">·</span>
                <span className="text-white">{fmtDuration(episode.duration_seconds)}</span>
                <span className="mx-2 text-stone-700">·</span>
                <span className="text-white">{episode.bucket_pull_count}</span> bucket pull{episode.bucket_pull_count !== 1 ? "s" : ""}
                <span className="mx-2 text-stone-700">·</span>
                <span className="text-white">{episode.golden_ticket_count}</span> golden ticket{episode.golden_ticket_count !== 1 ? "s" : ""}
                <span className="mx-2 text-stone-700">·</span>
                <span className="text-white">{episode.regular_count}</span> regular{episode.regular_count !== 1 ? "s" : ""}
                <span className="mx-2 text-stone-700">·</span>
                <span className="text-white">{episode.large_joke_book_count}</span> big joke book{episode.large_joke_book_count !== 1 ? "s" : ""}
                {episode.view_count != null && (
                  <>
                    <span className="mx-2 text-stone-700">·</span>
                    <span className="text-white">{fmtCompact(episode.view_count)}</span> views
                  </>
                )}
                {episode.like_count != null && (
                  <>
                    <span className="mx-2 text-stone-700">·</span>
                    <span className="text-white">{fmtCompact(episode.like_count)}</span> likes
                  </>
                )}
                {episode.comment_count != null && (
                  <>
                    <span className="mx-2 text-stone-700">·</span>
                    <span className="text-white">{fmtCompact(episode.comment_count)}</span> comments
                  </>
                )}
                {viewLikeRatio && (
                  <>
                    <span className="mx-2 text-stone-700">·</span>
                    <span className="text-white">{viewLikeRatio}</span> views/like
                  </>
                )}
              </p>
            </div>

          </div>
        </div>
      </div>

      {/* Sets grid */}
      <div className="mx-auto max-w-5xl px-6 py-10">
        <p className="mb-8 max-w-3xl text-base leading-relaxed text-stone-700">
          {buildEpisodeSummary(episode)}
        </p>
        {sets.length === 0 ? (
          <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
            <p className="text-stone-500">No sets indexed for this episode yet.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {sets.map((set) => (
              <SetTile
                key={set.id}
                set={set}
                episodeNumber={episode.number}
                episodeTitle={episode.title}
                youtubeId={episode.youtube_id}
              />
            ))}
          </div>
        )}
      </div>
    </div>
    </>
  );
}
