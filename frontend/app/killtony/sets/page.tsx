import { Suspense } from "react";
import { getServerSets } from "@/lib/serverApi";
import SetPlaylists from "./SetPlaylists";
import FilterControls from "@/components/FilterControls";
import { SET_SEARCH_CONFIG } from "@/lib/searchConfigs";
import ListPageHeader from "@/components/ListPageHeader";
import { SITE_URL, buildBreadcrumbSchema } from "@/lib/seo";

export const metadata = {
  title: "Sets - Kill Tony | PunchNotes",
};

export default async function SetsBrowsePage() {
  const sets = await getServerSets();

  const schema = {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    name: 'Kill Tony Sets',
    description: 'Browse all Kill Tony stand-up sets with joke breakdowns, transcripts, and comedian analytics.',
    url: `${SITE_URL}/killtony/sets`,
    breadcrumb: buildBreadcrumbSchema([
      { name: 'Kill Tony', item: `${SITE_URL}/killtony` },
      { name: 'Sets', item: `${SITE_URL}/killtony/sets` },
    ]),
    mainEntity: {
      '@type': 'ItemList',
      numberOfItems: sets?.length ?? 0,
      itemListElement: (sets ?? []).slice(0, 20).map((s, i) => ({
        '@type': 'ListItem',
        position: i + 1,
        item: {
          '@type': 'CreativeWork',
          name: `${s.comedian.name} — Kill Tony #${s.video.number}`,
          url: `${SITE_URL}/killtony/sets/${s.slug}`,
          genre: 'Stand-up Comedy',
          author: { '@type': 'Person', name: s.comedian.name },
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
    <div className="min-h-screen bg-white">
      <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6">
        <Suspense>
          <ListPageHeader
            title="Sets"
            searchPlaceholder="Search sets..."
            searchPath="/killtony/sets/search"
            controls={<FilterControls config={SET_SEARCH_CONFIG} />}
          />
        </Suspense>
      </div>

      {sets && (
        <div className="mx-auto max-w-6xl pb-12">
          <h2 className="mb-6 px-6 text-2xl font-bold tracking-tight text-stone-950">
            Set playlists
          </h2>
          <SetPlaylists sets={sets} />
        </div>
      )}
    </div>
    </>
  );
}
