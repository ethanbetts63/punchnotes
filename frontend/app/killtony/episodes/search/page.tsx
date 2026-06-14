import { getServerVideosPaginated } from "@/lib/serverApi";
import ModelSearchLayout, { buildSearchSubtitle } from "@/components/ModelSearchLayout";
import FilterControls from "@/components/FilterControls";
import Paginator from "@/components/Paginator";
import { EPISODE_SEARCH_CONFIG } from "@/lib/searchConfigs";
import EpisodeSearchResults from "./EpisodeSearchResults";

export const metadata = {
  title: "Search Episodes - Kill Tony | PunchNotes",
};

type Props = { searchParams: Promise<Record<string, string>> };

export default async function EpisodeSearchPage({ searchParams }: Props) {
  const sp = await searchParams;
  const query = (sp.q ?? "").trim();
  const page = Math.max(1, parseInt(sp.page ?? "1", 10) || 1);

  const data = await getServerVideosPaginated(
    new URLSearchParams(sp).toString(),
    EPISODE_SEARCH_CONFIG.pageSize,
  );

  const totalPages = data ? Math.max(1, Math.ceil(data.count / EPISODE_SEARCH_CONFIG.pageSize)) : 1;

  return (
    <ModelSearchLayout
      title="Search Episodes"
      backHref="/killtony/episodes"
      backLabel="Episodes"
      searchPlaceholder="Search episodes..."
      subtitle={buildSearchSubtitle(data?.count ?? null, "episode", "episodes", query)}
      controls={<FilterControls config={EPISODE_SEARCH_CONFIG} />}
      isEmpty={!data || data.results.length === 0}
      emptyMessage="No episodes found."
    >
      {data && data.results.length > 0 && (
        <>
          <EpisodeSearchResults episodes={data.results} />
          <Paginator page={page} totalPages={totalPages} />
        </>
      )}
    </ModelSearchLayout>
  );
}
