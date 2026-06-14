import { getServerSetsPaginated } from "@/lib/serverApi";
import ModelSearchLayout, { buildSearchSubtitle } from "@/components/ModelSearchLayout";
import FilterControls from "@/components/FilterControls";
import Paginator from "@/components/Paginator";
import { SET_SEARCH_CONFIG } from "@/lib/searchConfigs";
import SetSearchResults from "./SetSearchResults";

export const metadata = {
  title: "Search Sets - Kill Tony | PunchNotes",
};

type Props = { searchParams: Promise<Record<string, string>> };

export default async function SetSearchPage({ searchParams }: Props) {
  const sp = await searchParams;
  const query = (sp.q ?? "").trim();
  const page = Math.max(1, parseInt(sp.page ?? "1", 10) || 1);

  const data = await getServerSetsPaginated(new URLSearchParams(sp).toString());

  const totalPages = data ? Math.max(1, Math.ceil(data.count / SET_SEARCH_CONFIG.pageSize)) : 1;

  return (
    <ModelSearchLayout
      title="Search Sets"
      backHref="/killtony/sets"
      backLabel="Sets"
      searchPlaceholder="Search sets..."
      subtitle={buildSearchSubtitle(data?.count ?? null, "set", "sets", query)}
      controls={<FilterControls config={SET_SEARCH_CONFIG} />}
      isEmpty={!data || data.results.length === 0}
      emptyMessage="No sets found."
    >
      {data && data.results.length > 0 && (
        <>
          <SetSearchResults sets={data.results} />
          <Paginator page={page} totalPages={totalPages} />
        </>
      )}
    </ModelSearchLayout>
  );
}
