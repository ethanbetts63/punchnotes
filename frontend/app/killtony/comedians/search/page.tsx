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

async function ComedianResults({ sp }: { sp: Record<string, string> }) {
  const { query, page, queryString } = parseSearchPageParams(sp);

  const data = await getServerComediansPaginated(
    queryString,
    COMEDIAN_SEARCH_CONFIG.pageSize,
  );

  const totalPages = Math.max(1, Math.ceil(data.count / COMEDIAN_SEARCH_CONFIG.pageSize));
  const subtitle = buildSearchSubtitle(data.count, "comedian", "comedians", query);

  if (data.results.length === 0) {
    return (
      <>
        <p className="mb-6 text-stone-500">{subtitle}</p>
        <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
          <p className="text-stone-500">No comedians found.</p>
        </div>
      </>
    );
  }

  return (
    <>
      <p className="mb-6 text-stone-500">{subtitle}</p>
      <ComedianSearchResults comedians={data.results} />
      <Paginator page={page} totalPages={totalPages} />
    </>
  );
}

export default async function ComedianSearchPage({ searchParams }: Props) {
  const sp = await searchParams;

  return (
    <ModelSearchLayout
      title="Search Comedians"
      backHref="/killtony/comedians"
      backLabel="Comedians"
      searchPlaceholder="Search all comedians..."
      controls={<FilterControls config={COMEDIAN_SEARCH_CONFIG} />}
    >
      <ComedianResults sp={sp} />
    </ModelSearchLayout>
  );
}
