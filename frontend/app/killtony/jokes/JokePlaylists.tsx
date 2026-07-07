import { getServerSet } from "@/lib/serverApi";
import type { Set } from "@/lib/serverApi";
import AnnotatedBeatCarousel, { type AnnotatedBeatEntry } from "@/components/AnnotatedBeatCarousel";
import { getJokeTypeStyle } from "@/lib/jokeTypes";

type JokeList = {
  type: string;
  title: string;
  description: string;
  seeMoreText: string;
};

type BeatKey = { set_slug: string; bit_id: string; beat_id: string };

function beatKey({ set_slug, bit_id, beat_id }: BeatKey) {
  return `${set_slug}:${bit_id}:${beat_id}`;
}

function beatToEntry(set: Set, pick: BeatKey): AnnotatedBeatEntry | null {
  const bitIndex = set.bits.findIndex((candidate) => candidate.bit_id === pick.bit_id);
  const beatIndex = bitIndex >= 0
    ? set.bits[bitIndex].beats.findIndex((candidate) => candidate.beat_id === pick.beat_id)
    : -1;
  if (bitIndex < 0 || beatIndex < 0) return null;
  return { set, bitIndex, beatIndex };
}

const JOKE_TYPE_PLAYLISTS: (JokeList & { picks: BeatKey[] })[] = [
  {
    type: "misdirect",
    title: "Top Tier Misdirects",
    description: "The setup goes one way. The punch goes somewhere else entirely.",
    seeMoreText: "See all misdirects",
    picks: [
      { set_slug: "Z6sSORy6Xag-437-casey-rocket",        bit_id: "bit_002", beat_id: "bit_002_beat_001" },
      { set_slug: "11FD8eVzsfk-456-casey-rocket",        bit_id: "bit_002", beat_id: "bit_002_beat_001" },
      { set_slug: "lwLnqeBKa-0-352-pat-o-neill",         bit_id: "bit_005", beat_id: "bit_005_beat_001" },
      { set_slug: "lwLnqeBKa-0-352-pat-o-neill",         bit_id: "bit_006", beat_id: "bit_006_beat_001" },
      { set_slug: "cHJVtFgZv8E-6411-todd-royce",          bit_id: "bit_001", beat_id: "bit_001_beat_002" },
      { set_slug: "RQ7Uk4vTPtk-1970-todd-royce",          bit_id: "bit_003", beat_id: "bit_003_beat_001" },
      { set_slug: "6jytsJ8JIDk-3191-randolph-davies",     bit_id: "bit_001", beat_id: "bit_001_beat_001" },
      { set_slug: "2aB2fB1Ylao-6796-ehsan-ahmad",         bit_id: "bit_002", beat_id: "bit_002_beat_001" },
      { set_slug: "GeByotNr20c-3235-martin-phillips",     bit_id: "bit_001", beat_id: "bit_001_beat_001" },
      { set_slug: "auvj7zWVQHU-516-martin-phillips",     bit_id: "bit_001", beat_id: "bit_001_beat_001" },
      { set_slug: "_ZsN6tkpMQQ-1706-jack-shaw",           bit_id: "bit_001", beat_id: "bit_001_beat_001" },
      { set_slug: "wMF5C_BwQTA-568-gary-falcon",         bit_id: "bit_003", beat_id: "bit_003_beat_001" },
      { set_slug: "GZuIpWgRzgo-4118-collin-sledge",       bit_id: "bit_001", beat_id: "bit_001_beat_001" },
      { set_slug: "R0y_PxhMdQ4-3486-collin-sledge",       bit_id: "bit_001", beat_id: "bit_001_beat_001" },
      { set_slug: "EJ6qapvqqpI-389-hans-kim",            bit_id: "bit_003", beat_id: "bit_003_beat_001" },
    ],
  },
  {
    type: "reframe",
    title: "Amazing Reframes",
    description: "Same words, completely different meaning by the end.",
    seeMoreText: "See all reframes",
    picks: [
      { set_slug: "z3lYdMfNDmc-5296-casey-rocket",        bit_id: "bit_002", beat_id: "bit_002_beat_001" },
      { set_slug: "6jytsJ8JIDk-4073-pat-o-neill",         bit_id: "bit_005", beat_id: "bit_005_beat_001" },
      { set_slug: "1upKa86_uKU-3595-pat-o-neill",         bit_id: "bit_002", beat_id: "bit_002_beat_001" },
      { set_slug: "CnjJPpr10vM-7450-pat-o-neill",         bit_id: "bit_003", beat_id: "bit_003_beat_001" },
      { set_slug: "k2gOb6ltZvI-3078-todd-royce",          bit_id: "bit_002", beat_id: "bit_002_beat_001" },
      { set_slug: "e5WJ4jVgTgg-355-martin-phillips",     bit_id: "bit_003", beat_id: "bit_003_beat_001" },
      { set_slug: "RQ7Uk4vTPtk-5470-martin-phillips",     bit_id: "bit_003", beat_id: "bit_003_beat_001" },
      { set_slug: "K-XTZTg0OQ8-477-martin-phillips",     bit_id: "bit_001", beat_id: "bit_001_beat_001" },
      { set_slug: "Z6sSORy6Xag-4504-carlos-lopez",        bit_id: "bit_002", beat_id: "bit_002_beat_001" },
      { set_slug: "M7RsTBpU5xM-369-hans-kim",            bit_id: "bit_003", beat_id: "bit_003_beat_001" },
      { set_slug: "k2gOb6ltZvI-611-hans-kim",            bit_id: "bit_003", beat_id: "bit_003_beat_001" },
      { set_slug: "CqhPsohLbCg-7312-hans-kim",            bit_id: "bit_001", beat_id: "bit_001_beat_002" },
    ],
  },
  {
    type: "phonetic-match",
    title: "Best Phonetic Matches",
    description: "The punchline sounds like the setup. That's the whole trick.",
    seeMoreText: "See all phonetic matches",
    picks: [
      { set_slug: "ezuyuoP5OI8-3382-kansei-yasuda",       bit_id: "bit_002", beat_id: "bit_002_beat_001" },
      { set_slug: "GeByotNr20c-3778-colt",                bit_id: "bit_003", beat_id: "bit_003_beat_001" },
      { set_slug: "cqXwoGrebXs-1011-brandon-lacaruba",    bit_id: "bit_001", beat_id: "bit_001_beat_003" },
      { set_slug: "7AgDQxUvq6w-1296-tony-pepperoni",      bit_id: "bit_001", beat_id: "bit_001_beat_001" },
    ],
  },
  {
    type: "double-meaning",
    title: "Sneaky Double Meanings",
    description: "One word doing two jobs at the same time.",
    seeMoreText: "See all double meanings",
    picks: [
      { set_slug: "A0JWnKvtCAI-2997-hans-kim",            bit_id: "bit_001", beat_id: "bit_001_beat_001" },
      { set_slug: "3R3csSEA_JY-2374-hans-kim",            bit_id: "bit_002", beat_id: "bit_002_beat_001" },
      { set_slug: "2LGShfsvnTM-4423-mike-holder",         bit_id: "bit_001", beat_id: "bit_001_beat_001" },
      { set_slug: "g9OdSD0GkIc-5787-william-montgomery",  bit_id: "bit_003", beat_id: "bit_003_beat_001" },
      { set_slug: "lakXB1OP6Jg-1082-william-montgomery",  bit_id: "bit_005", beat_id: "bit_005_beat_001" },
      { set_slug: "R0y_PxhMdQ4-3486-collin-sledge",       bit_id: "bit_002", beat_id: "bit_002_beat_001" },
    ],
  },
  {
    type: "contradiction",
    title: "Sharp Contradictions",
    description: "The punchline says the opposite of what the setup implied.",
    seeMoreText: "See all contradictions",
    picks: [],
  },
  {
    type: "analogy",
    title: "Killer Analogies",
    description: "An unexpected comparison that makes the bit land harder.",
    seeMoreText: "See all analogies",
    picks: [
      { set_slug: "0DvjvaMG8RQ-398-collin-sledge",       bit_id: "bit_002", beat_id: "bit_002_beat_001" },
      { set_slug: "xwoTIaxgeWA-6183-william-montgomery",  bit_id: "bit_004", beat_id: "bit_004_beat_001" },
      { set_slug: "oLAxMa7JVfA-7275-william-montgomery",  bit_id: "bit_003", beat_id: "bit_003_beat_002" },
      { set_slug: "6GvGjp0nYFs-4729-michael-lehrer",      bit_id: "bit_004", beat_id: "bit_004_beat_002" },
      { set_slug: "QePXRkrAEoE-3224-andrew-wolfe",        bit_id: "bit_006", beat_id: "bit_006_beat_001" },
      { set_slug: "lwLnqeBKa-0-3483-chase-standen",       bit_id: "bit_002", beat_id: "bit_002_beat_002" },
      { set_slug: "zS-4IMtyjPw-806-duncan-stone-street", bit_id: "bit_002", beat_id: "bit_002_beat_001" },
      { set_slug: "a9Le0VGXZDU-1693-michael-hines",       bit_id: "bit_004", beat_id: "bit_004_beat_001" },
    ],
  },
  {
    type: "hyperbole",
    title: "Wild Hyperboles",
    description: "Cranked way past reality for effect.",
    seeMoreText: "See all hyperboles",
    picks: [
      { set_slug: "avLgvLtO10w-2478-steve-lee",           bit_id: "bit_001", beat_id: "bit_001_beat_002" },
      { set_slug: "M7RsTBpU5xM-1685-gary-falcon",         bit_id: "bit_003", beat_id: "bit_003_beat_001" },
      { set_slug: "3tzdqyIPcrM-1054-gabriel-kerr",        bit_id: "bit_001", beat_id: "bit_001_beat_004" },
      { set_slug: "ETk1fMPvekY-541-casey-rocket",        bit_id: "bit_001", beat_id: "bit_001_beat_001" },
      { set_slug: "lakXB1OP6Jg-4675-ari-matti",           bit_id: "bit_004", beat_id: "bit_004_beat_001" },
      { set_slug: "A0JWnKvtCAI-5450-david-lucas",         bit_id: "bit_001", beat_id: "bit_001_beat_003" },
      { set_slug: "r2zQT6MvMXI-372-hans-kim",            bit_id: "bit_003", beat_id: "bit_003_beat_001" },
      { set_slug: "bZ2mFX900FI-6009-martin-phillips",     bit_id: "bit_001", beat_id: "bit_001_beat_001" },
    ],
  },
  {
    type: "elephant-in-the-room",
    title: "Elephant in the Room",
    description: "The thing nobody's supposed to say — said.",
    seeMoreText: "See all elephant-in-the-room jokes",
    picks: [
      { set_slug: "KSGu1gbKP2Q-5748-martin-phillips",     bit_id: "bit_002", beat_id: "bit_002_beat_001" },
      { set_slug: "ezuyuoP5OI8-5587-lisa-smith",          bit_id: "bit_004", beat_id: "bit_004_beat_001" },
      { set_slug: "PG_8dq4YtSQ-1667-mario-zapata",         bit_id: "bit_003", beat_id: "bit_003_beat_001" },
      { set_slug: "NV6fKrnafRc-4801-jack-mcwilliams",      bit_id: "bit_002", beat_id: "bit_002_beat_002" },
    ],
  },
];

export default async function JokePlaylists() {
  const setSlugs = [...new Set(JOKE_TYPE_PLAYLISTS.flatMap((p) => p.picks.map((k) => k.set_slug)))];
  const sets = await Promise.all(setSlugs.map((slug) => getServerSet(slug)));
  const entryByKey = new Map<string, AnnotatedBeatEntry>();

  sets.filter((set): set is Set => set !== null).forEach((set) => {
    JOKE_TYPE_PLAYLISTS.flatMap((playlist) => playlist.picks)
      .filter((pick) => pick.set_slug === set.slug)
      .forEach((pick) => {
        const entry = beatToEntry(set, pick);
        if (entry) entryByKey.set(beatKey(pick), entry);
      });
  });

  const lists = JOKE_TYPE_PLAYLISTS
    .map((playlist) => {
      const items = playlist.picks
        .map((pick) => entryByKey.get(beatKey(pick)))
        .filter((entry): entry is AnnotatedBeatEntry => entry !== undefined);
      return {
        ...playlist,
        items,
        accentClass: getJokeTypeStyle(playlist.type)?.accent ?? "border-l-stone-300",
      };
    })
    .filter((list) => list.items.length > 0);

  if (lists.length === 0) return null;

  return (
    <div className="space-y-10">
      {lists.map((list) => (
        <AnnotatedBeatCarousel
          key={list.type}
          title={list.title}
          description={list.description}
          accentClass={list.accentClass}
          tileClassName="w-[88%] shrink-0 snap-start px-2 first:pl-6 last:pr-6 sm:w-[70%] md:w-[58%] lg:w-[48%] xl:w-[42%]"
          entries={list.items}
          href={`/killtony/jokes/search?joke_type=${list.type}`}
          linkText={list.seeMoreText}
        />
      ))}
    </div>
  );
}
