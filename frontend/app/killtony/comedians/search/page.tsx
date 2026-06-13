import { getServerComedians } from "@/lib/serverApi";
import ModelSearchLayout, { buildSearchSubtitle } from "@/components/ModelSearchLayout";
import ComedianSearchFilters from "@/components/ComedianSearchFilters";
import ComedianSearchResults from "./ComedianSearchResults";

export const metadata = {
  title: "Search Comedians - Kill Tony | PunchNotes",
};

type Props = { searchParams: Promise<Record<string, string>> };

export default async function ComedianSearchPage({ searchParams }: Props) {
  const searchParamsValue = await searchParams;
  const qs = new URLSearchParams(searchParamsValue).toString();
  const comedians = await getServerComedians(qs || undefined);
  const query = (searchParamsValue.q ?? "").trim();

  return (
    <ModelSearchLayout
      title="Search Comedians"
      backHref="/killtony/comedians"
      backLabel="Comedians"
      searchPlaceholder="Search comedians..."
      subtitle={buildSearchSubtitle(comedians?.length ?? null, "comedian", "comedians", query)}
      controls={<ComedianSearchFilters />}
      isEmpty={!comedians || comedians.length === 0}
      emptyMessage="No comedians found."
    >
      {comedians && <ComedianSearchResults comedians={comedians} />}
    </ModelSearchLayout>
  );
}
