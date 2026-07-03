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

async function EpisodeResults({ sp }: { sp: Record<string, string> }) {
  const { query, page, queryString } = parseSearchPageParams(sp);

  const data = await getServerVideosPaginated(
    queryString,
    EPISODE_SEARCH_CONFIG.pageSize,
  );

  const totalPages = Math.max(1, Math.ceil(data.count / EPISODE_SEARCH_CONFIG.pageSize));
  const subtitle = buildSearchSubtitle(data.count, "episode", "episodes", query);

  if (data.results.length === 0) {
    return (
      <>
        <p className="mb-6 text-stone-500">{subtitle}</p>
        <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
          <p className="text-stone-500">No episodes found.</p>
        </div>
      </>
    );
  }

  return (
    <>
      <p className="mb-6 text-stone-500">{subtitle}</p>
      <EpisodeSearchResults episodes={data.results} />
      <Paginator page={page} totalPages={totalPages} />
    </>
  );
}

export default async function EpisodeSearchPage({ searchParams }: Props) {
  const sp = await searchParams;

  return (
    <ModelSearchLayout
      title="Search Episodes"
      backHref="/killtony/episodes"
      backLabel="Episodes"
      searchPlaceholder="Search episodes..."
      controls={<FilterControls config={EPISODE_SEARCH_CONFIG} />}
    >
      <EpisodeResults sp={sp} />
    </ModelSearchLayout>
  );
}
