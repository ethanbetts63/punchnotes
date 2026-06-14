import { getServerComediansPaginated } from "@/lib/serverApi";
import ModelSearchLayout, { buildSearchSubtitle } from "@/components/ModelSearchLayout";
import FilterControls from "@/components/FilterControls";
import Paginator from "@/components/Paginator";
import { COMEDIAN_SEARCH_CONFIG } from "@/lib/searchConfigs";
import ComedianSearchResults from "./ComedianSearchResults";

export const metadata = {
  title: "Search Comedians - Kill Tony | PunchNotes",
};

type Props = { searchParams: Promise<Record<string, string>> };

export default async function ComedianSearchPage({ searchParams }: Props) {
  const sp = await searchParams;
  const query = (sp.q ?? "").trim();
  const page = Math.max(1, parseInt(sp.page ?? "1", 10) || 1);

  const data = await getServerComediansPaginated(new URLSearchParams(sp).toString());

  const totalPages = data ? Math.max(1, Math.ceil(data.count / COMEDIAN_SEARCH_CONFIG.pageSize)) : 1;

  return (
    <ModelSearchLayout
      title="Search Comedians"
      backHref="/killtony/comedians"
      backLabel="Comedians"
      searchPlaceholder="Search comedians..."
      subtitle={buildSearchSubtitle(data?.count ?? null, "comedian", "comedians", query)}
      controls={<FilterControls config={COMEDIAN_SEARCH_CONFIG} />}
      isEmpty={!data || data.results.length === 0}
      emptyMessage="No comedians found."
    >
      {data && data.results.length > 0 && (
        <>
          <ComedianSearchResults comedians={data.results} />
          <Paginator page={page} totalPages={totalPages} />
        </>
      )}
    </ModelSearchLayout>
  );
}
