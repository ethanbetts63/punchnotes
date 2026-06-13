import { getServerSets } from "@/lib/serverApi";
import ModelSearchLayout, { buildSearchSubtitle } from "@/components/ModelSearchLayout";
import SetSearchFilters from "@/components/SetSearchFilters";
import SetSearchResults from "./SetSearchResults";

export const metadata = {
  title: "Search Sets - Kill Tony | PunchNotes",
};

type Props = { searchParams: Promise<Record<string, string>> };

export default async function SetSearchPage({ searchParams }: Props) {
  const searchParamsValue = await searchParams;
  const qs = new URLSearchParams(searchParamsValue).toString();
  const sets = await getServerSets(qs || undefined);
  const query = (searchParamsValue.q ?? "").trim();

  return (
    <ModelSearchLayout
      title="Search Sets"
      backHref="/killtony/sets"
      backLabel="Sets"
      searchPlaceholder="Search sets..."
      subtitle={buildSearchSubtitle(sets?.length ?? null, "set", "sets", query)}
      controls={<SetSearchFilters />}
      isEmpty={!sets || sets.length === 0}
      emptyMessage="No sets found."
    >
      {sets && <SetSearchResults sets={sets} />}
    </ModelSearchLayout>
  );
}
