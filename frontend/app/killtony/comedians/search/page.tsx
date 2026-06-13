import { Suspense } from "react";
import { getServerComedians } from "@/lib/serverApi";
import ComedianSearchFilters from "@/components/ComedianSearchFilters";
import ListPageHeader from "@/components/ListPageHeader";
import ComedianList from "@/page_components/ComedianList";

export const metadata = {
  title: "Search Comedians - Kill Tony | PunchNotes",
};

type Props = { searchParams: Promise<Record<string, string>> };

export default async function ComedianSearchPage({ searchParams }: Props) {
  const searchParamsValue = await searchParams;
  const qs = new URLSearchParams(searchParamsValue).toString();
  const comedians = await getServerComedians(qs || undefined);
  const trimmedQuery = (searchParamsValue.q ?? "").trim();
  const subtitle = comedians
    ? `${comedians.length} comedian${comedians.length !== 1 ? "s" : ""}${trimmedQuery ? ` matching "${trimmedQuery}"` : ""}`
    : "Loading...";

  return (
    <div className="bg-white min-h-screen">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <Suspense>
          <ListPageHeader
            backHref="/killtony/comedians"
            backLabel="Comedians"
            title="Search Comedians"
            subtitle={subtitle}
            searchPlaceholder="Search comedians..."
            controls={<ComedianSearchFilters />}
          />
        </Suspense>

        {!comedians || comedians.length === 0 ? (
          <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
            <p className="text-stone-500">No comedians found.</p>
          </div>
        ) : (
          <Suspense>
            <ComedianList comedians={comedians} filterKey={qs} />
          </Suspense>
        )}
      </div>
    </div>
  );
}
