import type { BeatSearchItem } from "@/lib/serverApi";
import { jokeToTile, JOKE_TYPE_STYLES } from "@/lib/tiles";
import MediaCarousel from "@/components/MediaCarousel";

type JokeList = {
  type: string;
  title: string;
  description: string;
};

const JOKE_TYPE_PLAYLISTS: JokeList[] = [
  { type: "misdirect",              title: "Top Tier Misdirects",       description: "The setup goes one way. The punch goes somewhere else entirely." },
  { type: "reframe",                title: "Amazing Reframes",          description: "Same words, completely different meaning by the end." },
  { type: "phonetic-match",         title: "Best Phonetic Matches",     description: "The punchline sounds like the setup. That's the whole trick." },
  { type: "double-meaning",         title: "Sneaky Double Meanings",    description: "One word doing two jobs at the same time." },
  { type: "contradiction",          title: "Sharp Contradictions",      description: "The punchline says the opposite of what the setup implied." },
  { type: "analogy",                title: "Killer Analogies",          description: "An unexpected comparison that makes the bit land harder." },
  { type: "hyperbole",              title: "Wild Hyperboles",           description: "Cranked way past reality for effect." },
  { type: "elephant-in-the-room",   title: "Elephant in the Room",      description: "The thing nobody's supposed to say — said." },
];

function uniqueByKey(items: BeatSearchItem[]): BeatSearchItem[] {
  const seen = new Set<string>();
  return items.filter((item) => {
    const key = `${item.set_slug}:${item.bit_id}:${item.beat_id}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

export default function JokePlaylists({ jokes }: { jokes: BeatSearchItem[] }) {
  const byType = (type: string) => jokes.filter((joke) => joke.joke_type === type);

  const lists = JOKE_TYPE_PLAYLISTS
    .map((playlist) => ({
      ...playlist,
      items: uniqueByKey(byType(playlist.type)).slice(0, 18),
      accentClass: JOKE_TYPE_STYLES[playlist.type]?.accent ?? "border-l-stone-300",
    }))
    .filter((list) => list.items.length > 0);

  if (lists.length === 0) return null;

  return (
    <div className="space-y-10">
      {lists.map((list) => (
        <MediaCarousel
          key={list.type}
          title={list.title}
          description={list.description}
          accentClass={list.accentClass}
          tileClass="w-1/2 shrink-0 px-1.5 first:pl-6 last:pr-6 sm:w-1/2 md:w-1/3 lg:w-1/4 xl:w-1/4"
          items={list.items.map(jokeToTile)}
        />
      ))}
    </div>
  );
}
