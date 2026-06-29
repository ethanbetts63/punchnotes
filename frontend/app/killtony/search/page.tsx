import Link from "next/link";
import { ArrowUpRight } from "lucide-react";
import { getServerNavSearch, type NavSearchResponse, type NavSearchResult } from "@/lib/serverApi";
import YoutubeThumbnail from "@/components/YoutubeThumbnail";
import ComedianImage from "@/components/ComedianImage";

export const metadata = {
  title: "Search - Kill Tony | PunchNotes",
};

type Props = { searchParams: Promise<Record<string, string | string[] | undefined>> };

type NavSearchGroupKey = Exclude<keyof NavSearchResponse, "query">;

const GROUPS: { key: NavSearchGroupKey; title: string; description: string }[] = [
  { key: "comedians", title: "Comedians", description: "Guest comics and bucket pulls" },
  { key: "episodes", title: "Episodes", description: "KT numbers, titles, and metadata" },
  { key: "sets", title: "Sets", description: "Individual minutes and interviews" },
  { key: "beats", title: "Jokes", description: "Beat-level setup, punch, and tag matches" },
];

const MAIN_GROUPS: { key: NavSearchGroupKey; title: string }[] = [
  { key: "episodes", title: "Episodes" },
  { key: "comedians", title: "Comedians" },
  { key: "beats", title: "Jokes" },
];

const SIDEBAR_GROUPS: { key: NavSearchGroupKey; title: string }[] = [
  { key: "sets", title: "Sets" },
];

const ALWAYS_VISIBLE_GROUPS = new Set<NavSearchGroupKey>(["comedians", "episodes"]);

function typeStyle(type: NavSearchResult["type"]): string {
  switch (type) {
    case "comedian":
      return "bg-[#ff1464] text-white";
    case "episode":
      return "bg-black text-white";
    case "set":
      return "bg-[#ffff64] text-black";
    case "beat":
      return "bg-emerald-400 text-black";
    default:
      return "bg-indigo-500 text-white";
  }
}

function typeLabel(type: NavSearchResult["type"]): string {
  switch (type) {
    case "comedian":
      return "Comedian";
    case "episode":
      return "Episode";
    case "set":
      return "Set";
    case "beat":
      return "Joke";
    default:
      return "Search result";
  }
}

function resultInitial(item: NavSearchResult): string {
  if (item.type === "episode") {
    const episodeNumber = item.meta[0]?.match(/#(\d+)/)?.[1] ?? item.title.match(/#(\d+)/)?.[1];
    if (episodeNumber) return episodeNumber;
  }
  const label = item.title.trim() || typeLabel(item.type);
  return label.charAt(0).toUpperCase();
}

function NavSearchResultMark({ item }: { item: NavSearchResult }) {
  if (item.type === "episode") {
    return (
      <YoutubeThumbnail
        videoId={item.youtube_id}
        alt={item.title}
        className="h-[75px] w-[133px] shrink-0"
      />
    );
  }

  if (item.type === "comedian" && item.image_url) {
    return (
      <ComedianImage
        imageUrl={item.image_url}
        name={item.title}
        className="h-[75px] w-[75px] shrink-0"
      />
    );
  }

  return (
    <span
      className={`flex shrink-0 items-center justify-center overflow-hidden font-black uppercase ${
        typeStyle(item.type)
      } h-[75px] w-[75px] text-2xl`}
    >
      {resultInitial(item)}
    </span>
  );
}

function HighlightedText({ text, query }: { text: string; query: string }) {
  if (!query.trim()) return <>{text}</>;

  const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const pattern = new RegExp(`(${escaped})`, "ig");
  const parts = text.split(pattern);

  return (
    <>
      {parts.map((part, index) => (
        part.toLowerCase() === query.toLowerCase() ? <strong key={`${part}-${index}`}>{part}</strong> : part
      ))}
    </>
  );
}

function NavSearchResultCard({
  item,
  query,
  compact = false,
  textOnly = false,
}: {
  item: NavSearchResult;
  query: string;
  compact?: boolean;
  textOnly?: boolean;
}) {
  const subtitle = item.subtitle === typeLabel(item.type) ? "" : item.subtitle;
  const hideMark = compact || textOnly;
  const showHighlightedTitle = item.type === "beat" && Boolean(query.trim());

  return (
    <Link
      href={item.href}
      className={`group flex min-w-0 bg-white text-black transition-colors hover:bg-[#e9e9e9] ${
        compact ? "min-h-0" : "min-h-[75px]"
      }`}
    >
      {!hideMark && <NavSearchResultMark item={item} />}
      <div
        className={`flex min-w-0 flex-1 flex-col justify-between overflow-hidden ${
          compact ? "px-3 py-2" : "px-2.5 py-2"
        }`}
      >
        <div className="min-w-0">
          <div className="flex min-w-0 items-start justify-between gap-2">
            <p
              className={`min-w-0 overflow-hidden text-ellipsis break-words font-bold leading-none text-black ${
                compact ? "text-sm" : "text-base"
              }`}
            >
              {showHighlightedTitle ? <HighlightedText text={item.title} query={query} /> : item.title}
            </p>
            <ArrowUpRight className="mt-0.5 h-3.5 w-3.5 shrink-0 text-stone-400 opacity-0 transition-opacity group-hover:opacity-100" />
          </div>
          {subtitle && (
            <p
              className="mt-1 overflow-hidden text-ellipsis break-words text-xs text-stone-500 line-clamp-1"
            >
              {subtitle}
            </p>
          )}
        </div>
        <p className={`truncate text-xs text-stone-500 ${compact ? "mt-1" : "mt-2"}`}>
          <span className="font-bold text-[#ff1464]">{typeLabel(item.type)}</span>
          {item.meta.length > 0 && <span> / {item.meta.slice(0, 3).join(" / ")}</span>}
        </p>
      </div>
    </Link>
  );
}

function NavSearchResultSection({
  groupKey,
  title,
  items,
  query,
}: {
  groupKey: NavSearchGroupKey;
  title: string;
  items: NavSearchResult[];
  query: string;
}) {
  if (items.length === 0 && !ALWAYS_VISIBLE_GROUPS.has(groupKey)) return null;
  const isBeats = groupKey === "beats";

  return (
    <section className="scroll-mt-24" id={groupKey}>
      <div className="mb-2 mt-5 flex items-end justify-between gap-4 px-4 sm:px-0">
        <h2 className="text-xs font-bold uppercase text-stone-500">{title}</h2>
        <div className="flex items-center gap-3">
          <span className="text-xs text-stone-400">{items.length}</span>
          {items.length > 0 && (
            <Link
              href={refinedHref(groupKey, query)}
              className="text-xs font-bold text-stone-500 transition-colors hover:text-[#ff1464]"
            >
              Show more {title.toLowerCase()}
            </Link>
          )}
        </div>
      </div>
      <div className={`grid gap-2 ${isBeats ? "" : "min-[850px]:grid-cols-2"}`}>
        {items.length > 0 ? (
          items.map((item) => (
            <NavSearchResultCard key={`${item.type}-${item.href}-${item.title}`} item={item} query={query} textOnly={isBeats} />
          ))
        ) : (
          <div className="bg-white px-4 py-5 text-sm text-stone-500">
            No {title.toLowerCase()} matched this search.
          </div>
        )}
      </div>
    </section>
  );
}

function NavSearchSidebarSection({
  groupKey,
  title,
  items,
  query,
}: {
  groupKey: NavSearchGroupKey;
  title: string;
  items: NavSearchResult[];
  query: string;
}) {
  if (items.length === 0) return null;

  return (
    <section className="mt-4 bg-white p-4 text-black" id={groupKey}>
      <div className="mb-2 flex items-end justify-between gap-3">
        <h2 className="text-xs font-bold uppercase text-stone-500">{title}</h2>
        <div className="flex items-center gap-2">
          <span className="text-xs text-stone-400">{items.length}</span>
          <Link
            href={refinedHref(groupKey, query)}
            className="text-xs font-bold text-stone-500 transition-colors hover:text-[#ff1464]"
          >
            More
          </Link>
        </div>
      </div>
      <div className="grid gap-1.5">
        {items.map((item) => (
          <NavSearchResultCard key={`${item.type}-${item.href}-${item.title}`} item={item} query={query} compact />
        ))}
      </div>
    </section>
  );
}

function NavSearchEmptyState({ query }: { query: string }) {
  return (
    <div className="bg-white px-4 py-12 text-center text-black">
      <p className="text-xl font-bold">
        {query ? "No results found." : "Search the Kill Tony archive."}
      </p>
      <p className="mt-2 text-sm text-stone-500">
        Try a comedian, KT number, set detail, or joke line.
      </p>
    </div>
  );
}

function refinedHref(key: NavSearchGroupKey, query: string): string {
  const params = new URLSearchParams();
  if (query) params.set("q", query);
  const qs = params.toString();

  switch (key) {
    case "comedians":
      return `/killtony/comedians/search${qs ? `?${qs}` : ""}`;
    case "episodes":
      return `/killtony/episodes/search${qs ? `?${qs}` : ""}`;
    case "beats":
      return `/killtony/jokes/search${qs ? `?${qs}` : ""}`;
    case "sets":
      return `/killtony/sets/search${qs ? `?${qs}` : ""}`;
  }
}

function NavSearchSidebar({ results, query }: { results: NavSearchResponse | null; query: string }) {
  const counts = GROUPS.map((group) => ({
    ...group,
    count: results ? results[group.key].length : 0,
  }));

  return (
    <aside className="bg-white p-4 text-black">
      <h2 className="text-xs font-bold uppercase text-stone-500">Refine results</h2>
      <div className="mt-3 grid gap-1">
        {counts.map((group) => (
          <Link
            key={group.key}
            href={refinedHref(group.key, query)}
            className="flex items-center justify-between gap-3 px-0 py-2 text-sm transition-colors hover:text-[#ff1464]"
          >
            <span className="min-w-0">
              <span className="block truncate font-bold">{group.title}</span>
              <span className="block truncate text-xs text-stone-500">{group.description}</span>
            </span>
            <span className="shrink-0 text-xs text-stone-400">{group.count}</span>
          </Link>
        ))}
      </div>
    </aside>
  );
}

export default async function NavSearchPage({ searchParams }: Props) {
  const searchParamsValue = await searchParams;
  const rawQuery = searchParamsValue.q;
  const query = Array.isArray(rawQuery) ? rawQuery[0] ?? "" : rawQuery ?? "";
  const trimmedQuery = query.trim();
  const results = trimmedQuery ? await getServerNavSearch(trimmedQuery) : null;
  const hasResults = results ? GROUPS.some(({ key }) => results[key].length > 0) : false;

  return (
    <div className="min-h-screen bg-[#f7f7f7] text-black">
      <section className="bg-[#f7f7f7] text-black">
        <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
          <h1 className="break-words text-center text-4xl font-bold leading-none tracking-normal text-black sm:text-5xl">
            {trimmedQuery ? `"${trimmedQuery}"` : "Search"}
          </h1>
          <p className="mt-3 text-center text-sm font-bold uppercase text-stone-500">All results</p>
        </div>
      </section>

      <div className="mx-auto grid max-w-6xl gap-6 px-0 py-6 sm:px-6 lg:grid-cols-[minmax(0,1fr)_300px]">
        <main className="min-w-0">
          {!trimmedQuery && <NavSearchEmptyState query="" />}
          {trimmedQuery && !results && (
            <div className="bg-white px-4 py-12 text-center">
              <p className="text-lg font-bold">Search is unavailable right now.</p>
            </div>
          )}
          {results && !hasResults && <NavSearchEmptyState query={trimmedQuery} />}
          {results && hasResults && (
            <>
              {MAIN_GROUPS.map(({ key, title }) => (
                <NavSearchResultSection
                  key={key}
                  groupKey={key}
                  title={title}
                  items={results[key]}
                  query={trimmedQuery}
                />
              ))}
            </>
          )}
        </main>
        <aside className="px-4 sm:px-0">
          <NavSearchSidebar results={results} query={trimmedQuery} />
          {results && hasResults && SIDEBAR_GROUPS.map(({ key, title }) => (
            <NavSearchSidebarSection
              key={key}
              groupKey={key}
              title={title}
              items={results[key]}
              query={trimmedQuery}
            />
          ))}
        </aside>
      </div>
    </div>
  );
}
