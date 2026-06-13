import { Suspense } from "react";
import { getServerEpisodes } from "@/lib/serverApi";
import EpisodeSearchFilters from "@/components/EpisodeSearchFilters";
import ListPageHeader from "@/components/ListPageHeader";
import EpisodeSearchResults from "@/page_components/EpisodeSearchResults";

export const metadata = {
  title: "Search Episodes - Kill Tony | PunchNotes",
};

type Props = { searchParams: Promise<Record<string, string>> };

export default async function EpisodeSearchPage({ searchParams }: Props) {
  const searchParamsValue = await searchParams;
  const qs = new URLSearchParams(searchParamsValue).toString();
  const episodes = await getServerEpisodes(qs || undefined);
  const trimmedQuery = (searchParamsValue.q ?? "").trim();
  const subtitle = episodes
    ? `${episodes.length} episode${episodes.length !== 1 ? "s" : ""}${trimmedQuery ? ` matching "${trimmedQuery}"` : ""}`
    : "Loading...";

  return (
    <div className="bg-white min-h-screen">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <Suspense>
          <ListPageHeader
            backHref="/killtony/episodes"
            backLabel="Episodes"
            title="Search Episodes"
            subtitle={subtitle}
            searchPlaceholder="Search episodes..."
            controls={<EpisodeSearchFilters />}
          />
        </Suspense>

        {!episodes || episodes.length === 0 ? (
          <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
            <p className="text-stone-500">No episodes found.</p>
          </div>
        ) : (
          <Suspense>
            <EpisodeSearchResults episodes={episodes} />
          </Suspense>
        )}
      </div>
    </div>
  );
}
