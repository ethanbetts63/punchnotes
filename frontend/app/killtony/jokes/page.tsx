import Link from "next/link";
import FilterControls from "@/components/FilterControls";
import { JOKES_SEARCH_CONFIG } from "@/lib/searchConfigs";
import ListPageHeader from "@/components/ListPageHeader";
import { SITE_URL, buildBreadcrumbSchema, buildMetadata } from "@/lib/seo";
import { FaqSection } from "@/components/FaqSection";
import JokePlaylists from "./JokePlaylists";
import { JOKE_TYPE_FAQ, JOKE_TYPES } from "@/lib/jokeTypes";

export const metadata = buildMetadata({
  title: "Jokes - Kill Tony | PunchNotes",
  description:
    "Browse and search individual joke beats from Kill Tony, labelled by type, setup, punchline, and tags.",
  canonicalPath: "/killtony/jokes",
});

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
  const typeLabels = JOKE_TYPES.map((type) => type.label);
  const leadingTypeLabels = typeLabels.slice(0, -1).join(", ");
  const finalTypeLabel = typeLabels.at(-1);

  return (
    <>
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
    />
    <div className="min-h-screen bg-white">
      <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6">
        <ListPageHeader
          title="Jokes"
          searchPlaceholder="Search jokes..."
          searchPath="/killtony/jokes/search"
          urlState={false}
          controls={<FilterControls config={JOKES_SEARCH_CONFIG} urlState={false} />}
        />
      </div>

      <div className="mx-auto max-w-6xl pb-12">
        <h2 className="mb-6 px-6 text-2xl font-bold tracking-tight text-stone-950">
          Joke playlists
        </h2>
        <JokePlaylists />
      </div>

      <div className="mx-auto max-w-6xl px-6 pb-16 border-t border-stone-100 pt-10">
        <p className="text-stone-500">
          Every joke is broken into beats — each with a setup, punchline, and any tags — and assigned one of {JOKE_TYPES.length} structural types:{" "}
          <span className="font-medium text-stone-700">{leadingTypeLabels},</span>{" "}
          and <span className="font-medium text-stone-700">{finalTypeLabel}</span>.{" "}
          <Link href="/articles/how-to-annotate-jokes" className="text-primary underline underline-offset-2 hover:text-primary/80">
            How to Annotate Jokes &rarr;
          </Link>
        </p>
      </div>

      <FaqSection title="Joke types explained" faqData={JOKE_TYPE_FAQ} />
    </div>
    </>
  );
}
