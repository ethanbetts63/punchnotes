import { getServerEpisodes } from "@/lib/serverApi";
import ModelSearchLayout, { buildSearchSubtitle } from "@/components/ModelSearchLayout";
import EpisodeSearchFilters from "@/components/EpisodeSearchFilters";
import EpisodeSearchResults from "@/page_components/EpisodeSearchResults";

export const metadata = {
  title: "Search Episodes - Kill Tony | PunchNotes",
};

type Props = { searchParams: Promise<Record<string, string>> };

export default async function EpisodeSearchPage({ searchParams }: Props) {
  const searchParamsValue = await searchParams;
  const qs = new URLSearchParams(searchParamsValue).toString();
  const episodes = await getServerEpisodes(qs || undefined);
  const query = (searchParamsValue.q ?? "").trim();

  return (
    <ModelSearchLayout
      title="Search Episodes"
      backHref="/killtony/episodes"
      backLabel="Episodes"
      searchPlaceholder="Search episodes..."
      subtitle={buildSearchSubtitle(episodes?.length ?? null, "episode", "episodes", query)}
      controls={<EpisodeSearchFilters />}
      isEmpty={!episodes || episodes.length === 0}
      emptyMessage="No episodes found."
    >
      {episodes && <EpisodeSearchResults episodes={episodes} />}
    </ModelSearchLayout>
  );
}
