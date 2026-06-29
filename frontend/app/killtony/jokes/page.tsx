import { getServerBeatsPaginated } from "@/lib/serverApi";
import ModelSearchLayout, { buildSearchSubtitle } from "@/components/ModelSearchLayout";
import FilterControls from "@/components/FilterControls";
import Paginator from "@/components/Paginator";
import { JOKES_SEARCH_CONFIG } from "@/lib/searchConfigs";
import JokesList from "./JokesList";
import { SITE_URL, buildBreadcrumbSchema } from "@/lib/seo";

export const metadata = {
  title: "Jokes - Kill Tony | PunchNotes",
};

type Props = { searchParams: Promise<Record<string, string>> };

export default async function JokesPage({ searchParams }: Props) {
  const sp = await searchParams;
  const query = (sp.q ?? "").trim();
  const page = Math.max(1, parseInt(sp.page ?? "1", 10) || 1);

  const data = await getServerBeatsPaginated(
    new URLSearchParams(sp).toString(),
    JOKES_SEARCH_CONFIG.pageSize,
  );

  const totalPages = data ? Math.max(1, Math.ceil(data.count / JOKES_SEARCH_CONFIG.pageSize)) : 1;

  const baseSubtitle = buildSearchSubtitle(data?.count ?? null, "joke", "jokes", query);
  const subtitle = sp.joke_type ? `${baseSubtitle} / ${sp.joke_type}` : baseSubtitle;

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

  return (
    <>
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
    />
    <ModelSearchLayout
      title="Jokes"
      searchPlaceholder="Search jokes..."
      subtitle={subtitle}
      controls={<FilterControls config={JOKES_SEARCH_CONFIG} />}
      isEmpty={!data || data.results.length === 0}
      emptyMessage="No jokes found."
    >
      {data && data.results.length > 0 && (
        <>
          <JokesList beats={data.results} query={query} />
          <Paginator page={page} totalPages={totalPages} />
        </>
      )}
    </ModelSearchLayout>
    </>
  );
}
