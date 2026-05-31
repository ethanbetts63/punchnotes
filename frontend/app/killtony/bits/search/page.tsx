import { Suspense } from "react";
import Link from "next/link";
import { getServerBits } from "@/lib/serverApi";
import BrowseSearchBar from "@/components/BrowseSearchBar";
import BitSearchFilters from "@/components/BitSearchFilters";
import BitsList from "@/page_components/BitsList";

export const metadata = {
  title: "Search Bits — Kill Tony | PunchPedia",
};

type Props = { searchParams: Promise<Record<string, string>> };

export default async function BitSearchPage({ searchParams }: Props) {
  const sp = await searchParams;
  const qs = new URLSearchParams(sp).toString();
  const bits = await getServerBits(qs || undefined);
  const trimmedQuery = (sp.q ?? "").trim();

  return (
    <div className="bg-white min-h-screen">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <Link
          href="/killtony/bits"
          className="mb-6 inline-flex items-center gap-1.5 text-sm font-medium text-stone-500 transition-colors hover:text-stone-900"
        >
          ← Bits
        </Link>

        <div className="mb-6 mt-4">
          <h1 className="text-3xl font-bold text-stone-900">Search Bits</h1>
          <p className="mt-2 text-stone-500">
            {bits
              ? `${bits.length} bit${bits.length !== 1 ? "s" : ""}${trimmedQuery ? ` matching "${trimmedQuery}"` : ""}`
              : "Loading…"}
          </p>
        </div>

        <Suspense>
          <BrowseSearchBar placeholder="Search bits…" />
        </Suspense>

        <Suspense>
          <BitSearchFilters />
        </Suspense>

        {!bits || bits.length === 0 ? (
          <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
            <p className="text-stone-500">No bits found.</p>
          </div>
        ) : (
          <Suspense>
            <BitsList bits={bits} filterKey={qs} />
          </Suspense>
        )}
      </div>
    </div>
  );
}
