import { Suspense } from "react";
import { getServerBeats } from "@/lib/serverApi";
import FilterControls from "@/components/FilterControls";
import { JOKES_SEARCH_CONFIG } from "@/lib/searchConfigs";
import ListPageHeader from "@/components/ListPageHeader";
import { SITE_URL, buildBreadcrumbSchema } from "@/lib/seo";
import JokePlaylists from "./JokePlaylists";

export const metadata = {
  title: "Jokes - Kill Tony | PunchNotes",
};

export default async function JokesPage() {
  const jokes = await getServerBeats();

  const schema = {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    name: 'Kill Tony Jokes',
    description: 'Browse and search individual joke beats from Kill Tony, labelled by type, setup, punchline, and tags.',
    url: `${SITE_URL}/killtony/jokes`,
    breadcrumb: buildBreadcrumbSchema([
      { name: 'Kill Tony', item: `${SITE_URL}/killtony` },
      { name: 'Jokes', item: `${SITE_URL}/killtony/jokes` },
    ]),
    mainEntity: {
      '@type': 'ItemList',
      numberOfItems: jokes.length,
      itemListElement: jokes.slice(0, 20).map((joke, i) => ({
        '@type': 'ListItem',
        position: i + 1,
        item: {
          '@type': 'CreativeWork',
          name: joke.punchline || joke.premise,
          url: `${SITE_URL}/killtony/sets/${joke.set_slug}`,
          genre: 'Stand-up Comedy',
          author: { '@type': 'Person', name: joke.comedian },
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
            title="Jokes"
            searchPlaceholder="Search jokes..."
            searchPath="/killtony/jokes/search"
            controls={<FilterControls config={JOKES_SEARCH_CONFIG} />}
          />
        </Suspense>
      </div>

      <div className="mx-auto max-w-6xl pb-12">
        <h2 className="mb-6 px-6 text-2xl font-bold tracking-tight text-stone-950">
          Joke playlists
        </h2>
        <JokePlaylists jokes={jokes} />
      </div>
    </div>
    </>
  );
}
