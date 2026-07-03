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

async function SetResults({ sp }: { sp: Record<string, string> }) {
  const { query, page, queryString } = parseSearchPageParams(sp);

  const data = await getServerSetsPaginated(
    queryString,
    SET_SEARCH_CONFIG.pageSize,
  );

  const totalPages = Math.max(1, Math.ceil(data.count / SET_SEARCH_CONFIG.pageSize));
  const subtitle = buildSearchSubtitle(data.count, "set", "sets", query);

  if (data.results.length === 0) {
    return (
      <>
        <p className="mb-6 text-stone-500">{subtitle}</p>
        <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
          <p className="text-stone-500">No sets found.</p>
        </div>
      </>
    );
  }

  return (
    <>
      <p className="mb-6 text-stone-500">{subtitle}</p>
      <SetSearchResults sets={data.results} />
      <Paginator page={page} totalPages={totalPages} />
    </>
  );
}

export default async function SetSearchPage({ searchParams }: Props) {
  const sp = await searchParams;

  return (
    <ModelSearchLayout
      title="Search Sets"
      backHref="/killtony/sets"
      backLabel="Sets"
      searchPlaceholder="Search sets..."
      controls={<FilterControls config={SET_SEARCH_CONFIG} />}
    >
      <SetResults sp={sp} />
    </ModelSearchLayout>
  );
}
