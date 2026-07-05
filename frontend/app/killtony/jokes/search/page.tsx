import { getServerBeatsPaginated, getServerSet, type Set } from "@/lib/serverApi";
import ModelSearchLayout, { buildSearchSubtitle } from "@/components/ModelSearchLayout";
import FilterControls from "@/components/FilterControls";
import Paginator from "@/components/Paginator";
import { JOKES_SEARCH_CONFIG } from "@/lib/searchConfigs";
import { parseSearchPageParams } from "@/lib/searchParams";
import JokeSearchResultCard from "@/components/JokeSearchResultCard";
import { FaqSection } from "@/components/FaqSection";
import { JOKE_TYPE_FAQ } from "@/lib/jokeTypeFaq";

export const metadata = {
  title: "Search Jokes - Kill Tony | PunchNotes",
};

type Props = { searchParams: Promise<Record<string, string>> };

async function JokeResults({ sp }: { sp: Record<string, string> }) {
  const { query, page, queryString } = parseSearchPageParams(sp);

  const data = await getServerBeatsPaginated(queryString);
  const setSlugs = [...new Set(data.results.map((beat) => beat.set_slug))];
  const sets = await Promise.all(setSlugs.map((slug) => getServerSet(slug)));
  const setsBySlug = new Map<string, Set>(
    sets.filter((set): set is Set => set !== null).map((set) => [set.slug, set])
  );

  const totalPages = Math.max(1, Math.ceil(data.count / JOKES_SEARCH_CONFIG.pageSize));
  const baseSubtitle = buildSearchSubtitle(data.count, "joke", "jokes", query);
  const subtitle = sp.joke_type ? `${baseSubtitle} / ${sp.joke_type}` : baseSubtitle;

  if (data.results.length === 0) {
    return (
      <>
        <p className="mb-6 text-stone-500">{subtitle}</p>
        <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
          <p className="text-stone-500">No jokes found.</p>
        </div>
      </>
    );
  }

  return (
    <>
      <p className="mb-6 text-stone-500">{subtitle}</p>
      <div className="flex flex-col gap-3">
        {data.results.map((beat) => (
          <JokeSearchResultCard
            key={beat.id}
            item={beat}
            query={query}
            set={setsBySlug.get(beat.set_slug)}
          />
        ))}
      </div>
      <Paginator page={page} totalPages={totalPages} />
    </>
  );
}

export default async function JokeSearchPage({ searchParams }: Props) {
  const sp = await searchParams;

  return (
    <>
      <ModelSearchLayout
        title="Search Jokes"
        backHref="/killtony/jokes"
        backLabel="Jokes"
        searchPlaceholder="Search jokes..."
        controls={<FilterControls config={JOKES_SEARCH_CONFIG} />}
      >
        <JokeResults sp={sp} />
      </ModelSearchLayout>

      <FaqSection title="Joke types explained" faqData={JOKE_TYPE_FAQ} />
    </>
  );
}
