import { getServerBeatsPaginated } from "@/lib/serverApi";
import ModelSearchLayout, { buildSearchSubtitle } from "@/components/ModelSearchLayout";
import FilterControls from "@/components/FilterControls";
import Paginator from "@/components/Paginator";
import { JOKES_SEARCH_CONFIG } from "@/lib/searchConfigs";
import { parseSearchPageParams } from "@/lib/searchParams";
import JokeSearchResultCard from "@/components/JokeSearchResultCard";

export const metadata = {
  title: "Search Jokes - Kill Tony | PunchNotes",
};

type Props = { searchParams: Promise<Record<string, string>> };

export default async function JokeSearchPage({ searchParams }: Props) {
  const sp = await searchParams;
  const { query, page, queryString } = parseSearchPageParams(sp);

  const data = await getServerBeatsPaginated(
    queryString,
    JOKES_SEARCH_CONFIG.pageSize,
  );

  const totalPages = Math.max(1, Math.ceil(data.count / JOKES_SEARCH_CONFIG.pageSize));
  const baseSubtitle = buildSearchSubtitle(data.count, "joke", "jokes", query);
  const subtitle = sp.joke_type ? `${baseSubtitle} / ${sp.joke_type}` : baseSubtitle;

  return (
    <ModelSearchLayout
      title="Search Jokes"
      backHref="/killtony/jokes"
      backLabel="Jokes"
      searchPlaceholder="Search jokes..."
      subtitle={subtitle}
      controls={<FilterControls config={JOKES_SEARCH_CONFIG} />}
      isEmpty={data.results.length === 0}
      emptyMessage="No jokes found."
    >
      {data.results.length > 0 && (
        <>
          <div className="flex flex-col gap-3">
            {data.results.map((beat) => (
              <JokeSearchResultCard key={beat.id} item={beat} query={query} />
            ))}
          </div>
          <Paginator page={page} totalPages={totalPages} />
        </>
      )}
    </ModelSearchLayout>
  );
}
