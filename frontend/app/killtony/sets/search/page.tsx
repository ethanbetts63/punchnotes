import { Suspense } from "react";
import { getServerSets } from "@/lib/serverApi";
import ListPageHeader from "@/components/ListPageHeader";
import SetSearchFilters from "@/components/SetSearchFilters";
import SetList from "@/page_components/SetList";

export const metadata = {
  title: "Search Sets - Kill Tony | PunchNotes",
};

type Props = { searchParams: Promise<Record<string, string>> };

export default async function SetSearchPage({ searchParams }: Props) {
  const searchParamsValue = await searchParams;
  const qs = new URLSearchParams(searchParamsValue).toString();
  const sets = await getServerSets(qs || undefined);
  const trimmedQuery = (searchParamsValue.q ?? "").trim();
  const subtitle = sets
    ? `${sets.length} set${sets.length !== 1 ? "s" : ""}${trimmedQuery ? ` matching "${trimmedQuery}"` : ""}`
    : "Loading...";

  return (
    <div className="min-h-screen bg-white">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <Suspense>
          <ListPageHeader
            backHref="/killtony/sets"
            backLabel="Sets"
            title="Search Sets"
            subtitle={subtitle}
            searchPlaceholder="Search sets..."
            controls={<SetSearchFilters />}
          />
        </Suspense>

        {!sets || sets.length === 0 ? (
          <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
            <p className="text-stone-500">No sets found.</p>
          </div>
        ) : (
          <Suspense>
            <SetList sets={sets} filterKey={qs} />
          </Suspense>
        )}
      </div>
    </div>
  );
}
