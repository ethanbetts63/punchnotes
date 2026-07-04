import { getServerVideos } from "@/lib/serverApi";
import VideoPlaylists from "@/components/VideoPlaylists";
import FilterControls from "@/components/FilterControls";
import { EPISODE_SEARCH_CONFIG } from "@/lib/searchConfigs";
import ListPageHeader from "@/components/ListPageHeader";
import { SITE_URL, buildBreadcrumbSchema } from "@/lib/seo";

export const metadata = {
  title: "Episodes - Kill Tony | PunchNotes",
};

export default async function EpisodesBrowsePage() {
  const episodes = await getServerVideos();

  const schema = {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    name: 'Kill Tony Episodes',
    description: 'Browse all Kill Tony episodes with comedian sets, jokes, and breakdowns.',
    url: `${SITE_URL}/killtony/episodes`,
    breadcrumb: buildBreadcrumbSchema([
      { name: 'Kill Tony', item: `${SITE_URL}/killtony` },
      { name: 'Episodes', item: `${SITE_URL}/killtony/episodes` },
    ]),
    mainEntity: {
      '@type': 'ItemList',
      numberOfItems: episodes?.length ?? 0,
      itemListElement: (episodes ?? []).slice(0, 20).map((ep, i) => ({
        '@type': 'ListItem',
        position: i + 1,
        item: {
          '@type': 'TVEpisode',
          name: ep.title,
          episodeNumber: ep.number,
          url: `${SITE_URL}/killtony/episodes/${ep.slug}`,
          ...(ep.date ? { datePublished: ep.date } : {}),
        },
      })),
    },
  };

  return (
    <>
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
    />
    <div className="bg-white min-h-screen">
      <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6">
        <ListPageHeader
          title="Episodes"
          searchPlaceholder="Search episodes..."
          searchPath="/killtony/episodes/search"
          urlState={false}
          controls={<FilterControls config={EPISODE_SEARCH_CONFIG} urlState={false} />}
        />
      </div>

      {episodes && (
        <div className="mx-auto max-w-6xl pb-12">
          <h2 className="mb-6 px-6 text-2xl font-bold tracking-tight text-stone-950">
            Episode playlists
          </h2>
          <VideoPlaylists episodes={episodes} />
        </div>
      )}
    </div>
    </>
  );
}
