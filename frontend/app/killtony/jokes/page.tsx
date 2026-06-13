import { Suspense } from "react";
import { getServerBeats } from "@/lib/serverApi";
import JokesFilters from "@/components/JokesFilters";
import JokesList from "@/page_components/JokesList";
import ListPageHeader from "@/components/ListPageHeader";

export const metadata = {
  title: "Jokes - Kill Tony | PunchNotes",
};

type Props = { searchParams: Promise<Record<string, string>> };

export default async function JokesPage({ searchParams }: Props) {
  const searchParamsValue = await searchParams;
  const qs = new URLSearchParams(searchParamsValue).toString();
  const beats = await getServerBeats(qs);
  const query = (searchParamsValue.q ?? "").trim();
  const subtitle = [
    beats ? `${beats.length} jokes` : "",
    searchParamsValue.q ? `matching "${searchParamsValue.q}"` : "",
    searchParamsValue.joke_type ? searchParamsValue.joke_type : "",
  ]
    .filter(Boolean)
    .join(" / ");

  return (
    <div className="bg-white min-h-screen">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <Suspense>
          <ListPageHeader
            title="Jokes"
            subtitle={subtitle || (!beats ? "Loading..." : undefined)}
            searchPlaceholder="Search jokes..."
            controls={<JokesFilters />}
          />
        </Suspense>

        {!beats ? (
          <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
            <p className="text-stone-500">No jokes found.</p>
          </div>
        ) : (
          <Suspense>
            <JokesList beats={beats} query={query} />
          </Suspense>
        )}
      </div>
    </div>
  );
}
