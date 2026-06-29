import { getServerSetsPaginated } from "@/lib/serverApi";
import ModelSearchLayout, { buildSearchSubtitle } from "@/components/ModelSearchLayout";
import FilterControls from "@/components/FilterControls";
import Paginator from "@/components/Paginator";
import { SET_SEARCH_CONFIG } from "@/lib/searchConfigs";
import SetSearchResults from "./SetSearchResults";
import { parseSearchPageParams } from "@/lib/searchParams";

export const metadata = {
  title: "Search Sets - Kill Tony | PunchNotes",
};

type Props = { searchParams: Promise<Record<string, string>> };

export default async function SetSearchPage({ searchParams }: Props) {
  const sp = await searchParams;
  const { query, page, queryString } = parseSearchPageParams(sp);

  const data = await getServerSetsPaginated(
    queryString,
    SET_SEARCH_CONFIG.pageSize,
  );

  const totalPages = Math.max(1, Math.ceil(data.count / SET_SEARCH_CONFIG.pageSize));

  return (
    <ModelSearchLayout
      title="Search Sets"
      backHref="/killtony/sets"
      backLabel="Sets"
      searchPlaceholder="Search sets..."
      subtitle={buildSearchSubtitle(data.count, "set", "sets", query)}
      controls={<FilterControls config={SET_SEARCH_CONFIG} />}
      isEmpty={data.results.length === 0}
      emptyMessage="No sets found."
    >
      {data.results.length > 0 && (
        <>
          <SetSearchResults sets={data.results} />
          <Paginator page={page} totalPages={totalPages} />
        </>
      )}
    </ModelSearchLayout>
  );
}
