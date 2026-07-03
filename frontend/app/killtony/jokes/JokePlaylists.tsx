import { getServerSet } from "@/lib/serverApi";
import type { BeatSearchItem, Set } from "@/lib/serverApi";
import { jokeToTile, JOKE_TYPE_STYLES } from "@/lib/tiles";
import MediaCarousel from "@/components/MediaCarousel";

type JokeList = {
  type: string;
  title: string;
  description: string;
};

type BeatKey = { set_slug: string; bit_id: string; beat_id: string };

function beatKey({ set_slug, bit_id, beat_id }: BeatKey) {
  return `${set_slug}:${bit_id}:${beat_id}`;
}

function beatToSearchItem(set: Set, pick: BeatKey): BeatSearchItem | null {
  const bit = set.bits.find((candidate) => candidate.bit_id === pick.bit_id);
  const beat = bit?.beats.find((candidate) => candidate.beat_id === pick.beat_id);
  if (!bit || !beat) return null;

  const setupLines = beat.lines
    .filter((line) => line.label === "setup")
    .map((line) => line.text);
  const punchline = beat.lines.find((line) => line.label === "punchline")?.text ?? "";

  return {
    id: beat.id,
    beat_id: beat.beat_id,
    bit_id: bit.bit_id,
    comedian: set.comedian.name,
    comedian_slug: set.comedian.slug,
    episode_number: set.video.number,
    set_slug: set.slug,
    premise: beat.premise,
    joke_type: beat.joke_type,
    setup_lines: setupLines,
    punchline,
    matched_line: "",
    matched_line_label: "",
  };
}

const JOKE_TYPE_PLAYLISTS: (JokeList & { picks: BeatKey[] })[] = [
  {
    type: "misdirect",
    title: "Top Tier Misdirects",
    description: "The setup goes one way. The punch goes somewhere else entirely.",
    picks: [
      { set_slug: "xINfBBZBa3U-set07-timmy-no-brakes",     bit_id: "bit_001", beat_id: "bit_001_beat_001" },
      { set_slug: "Z6sSORy6Xag-set01-casey-rocket",        bit_id: "bit_002", beat_id: "bit_002_beat_001" },
      { set_slug: "11FD8eVzsfk-set01-casey-rocket",        bit_id: "bit_002", beat_id: "bit_002_beat_001" },
      { set_slug: "lwLnqeBKa-0-set01-pat-o-neill",         bit_id: "bit_005", beat_id: "bit_005_beat_001" },
      { set_slug: "lwLnqeBKa-0-set01-pat-o-neill",         bit_id: "bit_006", beat_id: "bit_006_beat_001" },
      { set_slug: "cHJVtFgZv8E-set12-todd-royce",          bit_id: "bit_001", beat_id: "bit_001_beat_002" },
      { set_slug: "RQ7Uk4vTPtk-set04-todd-royce",          bit_id: "bit_003", beat_id: "bit_003_beat_001" },
      { set_slug: "6jytsJ8JIDk-set07-randolph-davies",     bit_id: "bit_001", beat_id: "bit_001_beat_001" },
      { set_slug: "2aB2fB1Ylao-set11-ehsan-ahmad",         bit_id: "bit_002", beat_id: "bit_002_beat_001" },
      { set_slug: "GeByotNr20c-set06-martin-phillips",     bit_id: "bit_001", beat_id: "bit_001_beat_001" },
      { set_slug: "auvj7zWVQHU-set01-martin-phillips",     bit_id: "bit_001", beat_id: "bit_001_beat_001" },
      { set_slug: "_ZsN6tkpMQQ-set04-jack-shaw",           bit_id: "bit_001", beat_id: "bit_001_beat_001" },
      { set_slug: "wMF5C_BwQTA-set01-gary-falcon",         bit_id: "bit_003", beat_id: "bit_003_beat_001" },
      { set_slug: "GZuIpWgRzgo-set07-collin-sledge",       bit_id: "bit_001", beat_id: "bit_001_beat_001" },
      { set_slug: "R0y_PxhMdQ4-set06-collin-sledge",       bit_id: "bit_001", beat_id: "bit_001_beat_001" },
      { set_slug: "EJ6qapvqqpI-set01-hans-kim",            bit_id: "bit_003", beat_id: "bit_003_beat_001" },
    ],
  },
  {
    type: "reframe",
    title: "Amazing Reframes",
    description: "Same words, completely different meaning by the end.",
    picks: [
      { set_slug: "z3lYdMfNDmc-set10-casey-rocket",        bit_id: "bit_002", beat_id: "bit_002_beat_001" },
      { set_slug: "6jytsJ8JIDk-set08-pat-o-neill",         bit_id: "bit_005", beat_id: "bit_005_beat_001" },
      { set_slug: "1upKa86_uKU-set06-pat-o-neill",         bit_id: "bit_002", beat_id: "bit_002_beat_001" },
      { set_slug: "CnjJPpr10vM-set14-pat-o-neill",         bit_id: "bit_003", beat_id: "bit_003_beat_001" },
      { set_slug: "k2gOb6ltZvI-set06-todd-royce",          bit_id: "bit_002", beat_id: "bit_002_beat_001" },
      { set_slug: "e5WJ4jVgTgg-set01-martin-phillips",     bit_id: "bit_003", beat_id: "bit_003_beat_001" },
      { set_slug: "RQ7Uk4vTPtk-set10-martin-phillips",     bit_id: "bit_003", beat_id: "bit_003_beat_001" },
      { set_slug: "K-XTZTg0OQ8-set01-martin-phillips",     bit_id: "bit_001", beat_id: "bit_001_beat_001" },
      { set_slug: "Z6sSORy6Xag-set08-carlos-lopez",        bit_id: "bit_002", beat_id: "bit_002_beat_001" },
      { set_slug: "M7RsTBpU5xM-set01-hans-kim",            bit_id: "bit_003", beat_id: "bit_003_beat_001" },
      { set_slug: "k2gOb6ltZvI-set01-hans-kim",            bit_id: "bit_003", beat_id: "bit_003_beat_001" },
      { set_slug: "CqhPsohLbCg-set11-hans-kim",            bit_id: "bit_001", beat_id: "bit_001_beat_002" },
    ],
  },
  {
    type: "phonetic-match",
    title: "Best Phonetic Matches",
    description: "The punchline sounds like the setup. That's the whole trick.",
    picks: [
      { set_slug: "ezuyuoP5OI8-set06-kansei-yasuda",       bit_id: "bit_002", beat_id: "bit_002_beat_001" },
      { set_slug: "GeByotNr20c-set07-colt",                bit_id: "bit_003", beat_id: "bit_003_beat_001" },
    ],
  },
  {
    type: "double-meaning",
    title: "Sneaky Double Meanings",
    description: "One word doing two jobs at the same time.",
    picks: [
      { set_slug: "A0JWnKvtCAI-set05-hans-kim",            bit_id: "bit_001", beat_id: "bit_001_beat_001" },
      { set_slug: "3R3csSEA_JY-set05-hans-kim",            bit_id: "bit_002", beat_id: "bit_002_beat_001" },
    ],
  },
  {
    type: "contradiction",
    title: "Sharp Contradictions",
    description: "The punchline says the opposite of what the setup implied.",
    picks: [],
  },
  {
    type: "analogy",
    title: "Killer Analogies",
    description: "An unexpected comparison that makes the bit land harder.",
    picks: [
      { set_slug: "0DvjvaMG8RQ-set01-collin-sledge",       bit_id: "bit_002", beat_id: "bit_002_beat_001" },
    ],
  },
  {
    type: "hyperbole",
    title: "Wild Hyperboles",
    description: "Cranked way past reality for effect.",
    picks: [
      { set_slug: "avLgvLtO10w-set04-steve-lee",           bit_id: "bit_001", beat_id: "bit_001_beat_002" },
      { set_slug: "M7RsTBpU5xM-set04-gary-falcon",         bit_id: "bit_003", beat_id: "bit_003_beat_001" },
    ],
  },
  {
    type: "elephant-in-the-room",
    title: "Elephant in the Room",
    description: "The thing nobody's supposed to say — said.",
    picks: [
      { set_slug: "KSGu1gbKP2Q-set13-martin-phillips",     bit_id: "bit_002", beat_id: "bit_002_beat_001" },
    ],
  },
];

export default async function JokePlaylists() {
  const setSlugs = [...new Set(JOKE_TYPE_PLAYLISTS.flatMap((p) => p.picks.map((k) => k.set_slug)))];
  const sets = await Promise.all(setSlugs.map((slug) => getServerSet(slug)));
  const jokeByKey = new Map<string, BeatSearchItem>();

  sets.filter((set): set is Set => set !== null).forEach((set) => {
    JOKE_TYPE_PLAYLISTS.flatMap((playlist) => playlist.picks)
      .filter((pick) => pick.set_slug === set.slug)
      .forEach((pick) => {
        const joke = beatToSearchItem(set, pick);
        if (joke) jokeByKey.set(beatKey(pick), joke);
      });
  });

  const lists = JOKE_TYPE_PLAYLISTS
    .map((playlist) => {
      const items = playlist.picks
        .map((pick) => jokeByKey.get(beatKey(pick)))
        .filter((j): j is BeatSearchItem => j !== undefined);
      return {
        ...playlist,
        items,
        accentClass: JOKE_TYPE_STYLES[playlist.type]?.accent ?? "border-l-stone-300",
      };
    })
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
          items={list.items.map((j) => jokeToTile(j))}
        />
      ))}
    </div>
  );
}
