import { Suspense } from "react";
import Link from "next/link";
import { getServerComedians } from "@/lib/serverApi";
import BrowseSearchBar from "@/components/BrowseSearchBar";
import ComedianSearchFilters from "@/components/ComedianSearchFilters";
import ComedianList from "@/components/ComedianList";

export const metadata = {
  title: "Search Comedians — Kill Tony | PunchPedia",
};

type Props = { searchParams: Promise<Record<string, string>> };

export default async function ComedianSearchPage({ searchParams }: Props) {
  const sp = await searchParams;
  const qs = new URLSearchParams(sp).toString();
  const comedians = await getServerComedians(qs || undefined);
  const trimmedQuery = (sp.q ?? "").trim();

  return (
    <div className="bg-white min-h-screen">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <Link
          href="/killtony/comedians"
          className="mb-6 inline-flex items-center gap-1.5 text-sm font-medium text-stone-500 transition-colors hover:text-stone-900"
        >
          ← Comedians
        </Link>

        <div className="mb-6 mt-4">
          <h1 className="text-3xl font-bold text-stone-900">Search Comedians</h1>
          <p className="mt-2 text-stone-500">
            {comedians
              ? `${comedians.length} comedian${comedians.length !== 1 ? "s" : ""}${trimmedQuery ? ` matching "${trimmedQuery}"` : ""}`
              : "Loading…"}
          </p>
        </div>

        <Suspense>
          <BrowseSearchBar placeholder="Search comedians…" />
        </Suspense>

        <Suspense>
          <ComedianSearchFilters />
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
