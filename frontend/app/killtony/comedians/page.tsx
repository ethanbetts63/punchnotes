import { Suspense } from "react";
import { getServerComedians } from "@/lib/serverApi";
import ComedianPlaylists from "@/components/ComedianPlaylists";
import FilterControls from "@/components/FilterControls";
import { COMEDIAN_SEARCH_CONFIG } from "@/lib/searchConfigs";
import ListPageHeader from "@/components/ListPageHeader";
import { SITE_URL, buildBreadcrumbSchema } from "@/lib/seo";

export const metadata = {
  title: "Comedians - Kill Tony | PunchNotes",
};

export default async function ComediansBrowsePage() {
  const comedians = await getServerComedians();

  const schema = {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    name: 'Kill Tony Comedians',
    description: 'Browse all comedians who have performed on Kill Tony, with sets, jokes, and analytics.',
    url: `${SITE_URL}/killtony/comedians`,
    breadcrumb: buildBreadcrumbSchema([
      { name: 'Kill Tony', item: `${SITE_URL}/killtony` },
      { name: 'Comedians', item: `${SITE_URL}/killtony/comedians` },
    ]),
    mainEntity: {
      '@type': 'ItemList',
      numberOfItems: comedians?.length ?? 0,
      itemListElement: (comedians ?? []).slice(0, 20).map((c, i) => ({
        '@type': 'ListItem',
        position: i + 1,
        item: {
          '@type': 'Person',
          name: c.name,
          url: `${SITE_URL}/killtony/comedians/${c.slug}`,
          jobTitle: 'Comedian',
          ...(c.image_url ? { image: c.image_url } : {}),
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
        <Suspense>
          <ListPageHeader
            title="Comedians"
            searchPlaceholder="Search all comedians..."
            searchPath="/killtony/comedians/search"
            controls={<FilterControls config={COMEDIAN_SEARCH_CONFIG} />}
          />
        </Suspense>
      </div>

      {comedians && (
        <div className="mx-auto max-w-6xl pb-12">
          <h2 className="mb-6 px-6 text-2xl font-bold tracking-tight text-stone-950">
            Comic lists
          </h2>
          <ComedianPlaylists comedians={comedians} />
        </div>
      )}
    </div>
    </>
  );
}
