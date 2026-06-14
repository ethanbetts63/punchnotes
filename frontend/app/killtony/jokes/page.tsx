import { getServerBeatsPaginated } from "@/lib/serverApi";
import ModelSearchLayout, { buildSearchSubtitle } from "@/components/ModelSearchLayout";
import FilterControls from "@/components/FilterControls";
import Paginator from "@/components/Paginator";
import { JOKES_SEARCH_CONFIG } from "@/lib/searchConfigs";
import JokesList from "./JokesList";

export const metadata = {
  title: "Jokes - Kill Tony | PunchNotes",
};

type Props = { searchParams: Promise<Record<string, string>> };

export default async function JokesPage({ searchParams }: Props) {
  const sp = await searchParams;
  const query = (sp.q ?? "").trim();
  const page = Math.max(1, parseInt(sp.page ?? "1", 10) || 1);

  const data = await getServerBeatsPaginated(new URLSearchParams(sp).toString());

  const totalPages = data ? Math.max(1, Math.ceil(data.count / JOKES_SEARCH_CONFIG.pageSize)) : 1;

  const baseSubtitle = buildSearchSubtitle(data?.count ?? null, "joke", "jokes", query);
  const subtitle = sp.joke_type ? `${baseSubtitle} / ${sp.joke_type}` : baseSubtitle;

  return (
    <ModelSearchLayout
      title="Jokes"
      searchPlaceholder="Search jokes..."
      subtitle={subtitle}
      controls={<FilterControls config={JOKES_SEARCH_CONFIG} />}
      isEmpty={!data || data.results.length === 0}
      emptyMessage="No jokes found."
    >
      {data && data.results.length > 0 && (
        <>
          <JokesList beats={data.results} query={query} />
          <Paginator page={page} totalPages={totalPages} />
        </>
      )}
    </ModelSearchLayout>
  );
}
