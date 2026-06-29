import { getServerBeatsPaginated } from "@/lib/serverApi";
import ModelSearchLayout, { buildSearchSubtitle } from "@/components/ModelSearchLayout";
import FilterControls from "@/components/FilterControls";
import Paginator from "@/components/Paginator";
import { JOKES_SEARCH_CONFIG } from "@/lib/searchConfigs";
import JokesList from "./JokesList";
import { SITE_URL, buildBreadcrumbSchema } from "@/lib/seo";
import { parseSearchPageParams } from "@/lib/searchParams";

export const metadata = {
  title: "Jokes - Kill Tony | PunchNotes",
};

type Props = { searchParams: Promise<Record<string, string>> };

export default async function JokesPage({ searchParams }: Props) {
  const sp = await searchParams;
  const { query, page, queryString } = parseSearchPageParams(sp);

  const data = await getServerBeatsPaginated(
    queryString,
    JOKES_SEARCH_CONFIG.pageSize,
  );

  const totalPages = Math.max(1, Math.ceil(data.count / JOKES_SEARCH_CONFIG.pageSize));

  const baseSubtitle = buildSearchSubtitle(data.count, "joke", "jokes", query);
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
      isEmpty={data.results.length === 0}
      emptyMessage="No jokes found."
    >
      {data.results.length > 0 && (
        <>
          <JokesList beats={data.results} query={query} />
          <Paginator page={page} totalPages={totalPages} />
        </>
      )}
    </ModelSearchLayout>
    </>
  );
}
