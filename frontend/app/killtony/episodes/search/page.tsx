import { getServerVideosPaginated } from "@/lib/serverApi";
import ModelSearchLayout, { buildSearchSubtitle } from "@/components/ModelSearchLayout";
import FilterControls from "@/components/FilterControls";
import Paginator from "@/components/Paginator";
import { EPISODE_SEARCH_CONFIG } from "@/lib/searchConfigs";
import EpisodeSearchResults from "./EpisodeSearchResults";
import { parseSearchPageParams } from "@/lib/searchParams";

export const metadata = {
  title: "Search Episodes - Kill Tony | PunchNotes",
};

type Props = { searchParams: Promise<Record<string, string>> };

export default async function EpisodeSearchPage({ searchParams }: Props) {
  const sp = await searchParams;
  const { query, page, queryString } = parseSearchPageParams(sp);

  const data = await getServerVideosPaginated(
    queryString,
    EPISODE_SEARCH_CONFIG.pageSize,
  );

  const totalPages = Math.max(1, Math.ceil(data.count / EPISODE_SEARCH_CONFIG.pageSize));

  return (
    <ModelSearchLayout
      title="Search Episodes"
      backHref="/killtony/episodes"
      backLabel="Episodes"
      searchPlaceholder="Search episodes..."
      subtitle={buildSearchSubtitle(data.count, "episode", "episodes", query)}
      controls={<FilterControls config={EPISODE_SEARCH_CONFIG} />}
      isEmpty={data.results.length === 0}
      emptyMessage="No episodes found."
    >
      {data.results.length > 0 && (
        <>
          <EpisodeSearchResults episodes={data.results} />
          <Paginator page={page} totalPages={totalPages} />
        </>
      )}
    </ModelSearchLayout>
  );
}
