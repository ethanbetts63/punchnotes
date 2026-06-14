import { getServerBeats } from "@/lib/serverApi";
import ModelSearchLayout, { buildSearchSubtitle } from "@/components/ModelSearchLayout";
import FilterControls from "@/components/FilterControls";
import { JOKES_SEARCH_CONFIG } from "@/lib/searchConfigs";
import JokesList from "./JokesList";

export const metadata = {
  title: "Jokes - Kill Tony | PunchNotes",
};

type Props = { searchParams: Promise<Record<string, string>> };

export default async function JokesPage({ searchParams }: Props) {
  const searchParamsValue = await searchParams;
  const qs = new URLSearchParams(searchParamsValue).toString();
  const beats = await getServerBeats(qs);
  const query = (searchParamsValue.q ?? "").trim();

  const baseSubtitle = buildSearchSubtitle(beats?.length ?? null, "joke", "jokes", query);
  const jokeType = searchParamsValue.joke_type;
  const subtitle = jokeType ? `${baseSubtitle} / ${jokeType}` : baseSubtitle;

  return (
    <ModelSearchLayout
      title="Jokes"
      searchPlaceholder="Search jokes..."
      subtitle={subtitle}
      controls={<FilterControls config={JOKES_SEARCH_CONFIG} />}
      isEmpty={!beats || beats.length === 0}
      emptyMessage="No jokes found."
    >
      {beats && <JokesList beats={beats} query={query} />}
    </ModelSearchLayout>
  );
}
