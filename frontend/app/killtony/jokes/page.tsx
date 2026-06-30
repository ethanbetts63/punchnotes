import { Suspense } from "react";
import FilterControls from "@/components/FilterControls";
import { JOKES_SEARCH_CONFIG } from "@/lib/searchConfigs";
import ListPageHeader from "@/components/ListPageHeader";
import { SITE_URL, buildBreadcrumbSchema } from "@/lib/seo";
import JokePlaylists from "./JokePlaylists";

export const metadata = {
  title: "Jokes - Kill Tony | PunchNotes",
};

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
};

export default async function JokesPage() {
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
        <JokePlaylists />
      </div>
    </div>
    </>
  );
}
