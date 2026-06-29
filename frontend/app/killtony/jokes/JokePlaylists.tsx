import type { BeatSearchItem } from "@/lib/serverApi";
import { jokeToTile } from "@/lib/tiles";
import MediaCarousel from "@/components/MediaCarousel";

type JokeList = {
  id: string;
  title: string;
  description: string;
  items: BeatSearchItem[];
};

function uniqueByHref(items: BeatSearchItem[]): BeatSearchItem[] {
  const seen = new Set<string>();
  return items.filter((item) => {
    const key = `${item.set_slug}:${item.bit_id}:${item.beat_id}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

export default function JokePlaylists({ jokes }: { jokes: BeatSearchItem[] }) {
  const withPunchlines = jokes.filter((joke) => joke.punchline);
  const byType = (type: string) => jokes.filter((joke) => joke.joke_type === type);

  const lists: JokeList[] = [
    {
      id: "latest-jokes",
      title: "Latest Jokes",
      description: "A quick pass through recent joke breakdowns in the archive.",
      items: withPunchlines.slice(0, 18),
    },
    {
      id: "misdirects",
      title: "Misdirects",
      description: "Jokes where the punch turns the setup in another direction.",
      items: byType("misdirect").slice(0, 18),
    },
    {
      id: "reframes",
      title: "Reframes",
      description: "Jokes built around changing the meaning of the premise.",
      items: byType("reframe").slice(0, 18),
    },
    {
      id: "short-and-sharp",
      title: "Short and Sharp",
      description: "Compact jokes with short punchlines.",
      items: withPunchlines
        .filter((joke) => joke.punchline.length <= 90)
        .slice(0, 18),
    },
    {
      id: "random-shelf",
      title: "Random Shelf",
      description: "Placeholder picks while the proper joke playlists are being curated.",
      items: jokes.filter((_, index) => index % 7 === 0).slice(0, 18),
    },
  ]
    .map((list) => ({ ...list, items: uniqueByHref(list.items) }))
    .filter((list) => list.items.length > 0);

  if (lists.length === 0) return null;

  return (
    <div className="space-y-10">
      {lists.map((list) => (
        <MediaCarousel
          key={list.id}
          title={list.title}
          description={list.description}
          items={list.items.map(jokeToTile)}
        />
      ))}
    </div>
  );
}
