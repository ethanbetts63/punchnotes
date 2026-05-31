import { Suspense } from "react";
import Link from "next/link";
import { getServerSets } from "@/lib/serverApi";
import BrowseSearchBar from "@/components/BrowseSearchBar";
import SetSearchFilters from "@/components/SetSearchFilters";
import SetList from "@/page_components/SetList";

export const metadata = {
  title: "Search Sets — Kill Tony | PunchNotes",
};

type Props = { searchParams: Promise<Record<string, string>> };

export default async function SetSearchPage({ searchParams }: Props) {
  const sp = await searchParams;
  const qs = new URLSearchParams(sp).toString();
  const sets = await getServerSets(qs || undefined);
  const trimmedQuery = (sp.q ?? "").trim();

  return (
    <div className="min-h-screen bg-white">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <Link
          href="/killtony/sets"
          className="mb-6 inline-flex items-center gap-1.5 text-sm font-medium text-stone-500 transition-colors hover:text-stone-900"
        >
          ← Sets
        </Link>

        <div className="mb-6 mt-4">
          <h1 className="text-3xl font-bold text-stone-900">Search Sets</h1>
          <p className="mt-2 text-stone-500">
            {sets
              ? `${sets.length} set${sets.length !== 1 ? "s" : ""}${trimmedQuery ? ` matching "${trimmedQuery}"` : ""}`
              : "Loading…"}
          </p>
        </div>

        <Suspense>
          <BrowseSearchBar placeholder="Search sets…" />
        </Suspense>

        <Suspense>
          <SetSearchFilters />
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
