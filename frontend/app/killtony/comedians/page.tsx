import Link from "next/link";
import { getServerComedians } from "@/lib/serverApi";
import ComedianPlaylists from "@/components/ComedianPlaylists";
import FilterControls from "@/components/FilterControls";
import { COMEDIAN_SEARCH_CONFIG } from "@/lib/searchConfigs";
import ListPageHeader from "@/components/ListPageHeader";
import { INDEXED_COMEDIAN_MIN_SETS, SITE_URL, buildBreadcrumbSchema, buildMetadata, isIndexedComedian } from "@/lib/seo";

export const metadata = buildMetadata({
  title: "Comedians - Kill Tony | PunchNotes",
  description:
    "Browse all comedians who have performed on Kill Tony, with sets, jokes, and analytics.",
  canonicalPath: "/killtony/comedians",
});

export default async function ComediansBrowsePage() {
  const comedians = await getServerComedians();
  const repeatComedians = (comedians ?? [])
    .filter(isIndexedComedian)
    .sort((a, b) => b.set_count - a.set_count || a.name.localeCompare(b.name));

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
      numberOfItems: repeatComedians.length,
      itemListElement: repeatComedians.slice(0, 20).map((c, i) => ({
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
        <ListPageHeader
          title="Comedians"
          searchPlaceholder="Search all comedians..."
          searchPath="/killtony/comedians/search"
          urlState={false}
          controls={<FilterControls config={COMEDIAN_SEARCH_CONFIG} urlState={false} />}
        />
      </div>

      {comedians && (
        <div className="mx-auto max-w-6xl pb-12">
          <h2 className="mb-6 px-6 text-2xl font-bold tracking-tight text-stone-950">
            Comic lists
          </h2>
          <ComedianPlaylists comedians={comedians} />
        </div>
      )}

      {repeatComedians.length > 0 && (
        <div className="mx-auto max-w-6xl px-4 pb-16 sm:px-6">
          <h2 className="mb-2 text-2xl font-bold tracking-tight text-stone-950">
            Every comic with {INDEXED_COMEDIAN_MIN_SETS} or more sets
          </h2>
          <p className="mb-6 text-sm text-stone-500">
            {repeatComedians.length} comics, most sets first. Each page has their appearances, stats and jokes.
          </p>
          <ul className="grid grid-cols-1 gap-x-6 gap-y-1.5 text-sm sm:grid-cols-2 lg:grid-cols-4">
            {repeatComedians.map((comedian) => (
              <li key={comedian.slug} className="flex items-baseline justify-between gap-3 border-b border-stone-100 py-1">
                <Link href={`/killtony/comedians/${comedian.slug}`} className="truncate text-stone-800 hover:text-primary">
                  {comedian.name}
                </Link>
                <span className="shrink-0 tabular-nums text-xs text-stone-400">{comedian.set_count} sets</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
    </>
  );
}
