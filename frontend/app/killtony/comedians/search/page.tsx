import { getServerComediansPaginated } from "@/lib/serverApi";
import ModelSearchLayout, { buildSearchSubtitle } from "@/components/ModelSearchLayout";
import FilterControls from "@/components/FilterControls";
import Paginator from "@/components/Paginator";
import { COMEDIAN_SEARCH_CONFIG } from "@/lib/searchConfigs";
import ComedianSearchResults from "./ComedianSearchResults";
import { parseSearchPageParams } from "@/lib/searchParams";

export const metadata = {
  title: "Search Comedians - Kill Tony | PunchNotes",
};

type Props = { searchParams: Promise<Record<string, string>> };

export default async function ComedianSearchPage({ searchParams }: Props) {
  const sp = await searchParams;
  const { query, page, queryString } = parseSearchPageParams(sp);

  const data = await getServerComediansPaginated(
    queryString,
    COMEDIAN_SEARCH_CONFIG.pageSize,
  );

  const totalPages = Math.max(1, Math.ceil(data.count / COMEDIAN_SEARCH_CONFIG.pageSize));

  return (
    <ModelSearchLayout
      title="Search Comedians"
      backHref="/killtony/comedians"
      backLabel="Comedians"
      searchPlaceholder="Search all comedians..."
      subtitle={buildSearchSubtitle(data.count, "comedian", "comedians", query)}
      controls={<FilterControls config={COMEDIAN_SEARCH_CONFIG} />}
      isEmpty={data.results.length === 0}
      emptyMessage="No comedians found."
    >
      {data.results.length > 0 && (
        <>
          <ComedianSearchResults comedians={data.results} />
          <Paginator page={page} totalPages={totalPages} />
        </>
      )}
    </ModelSearchLayout>
  );
}
