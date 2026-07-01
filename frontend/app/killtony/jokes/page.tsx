import { Suspense } from "react";
import Link from "next/link";
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

      <div className="mx-auto max-w-6xl px-6 pb-16 border-t border-stone-100 pt-10">
        <p className="text-stone-500">
          Every joke is broken into beats — each with a setup, punchline, and any tags — and assigned one of nine structural types:{" "}
          <span className="font-medium text-stone-700">misdirect, reframe, phonetic-match, double-meaning, contradiction, analogy, hyperbole, elephant-in-the-room,</span>{" "}
          and <span className="font-medium text-stone-700">anti-humor</span>.{" "}
          <Link href="/articles/how-we-classify-jokes" className="text-primary underline underline-offset-2 hover:text-primary/80">
            How we classify jokes &rarr;
          </Link>
        </p>
      </div>
    </div>
    </>
  );
}
