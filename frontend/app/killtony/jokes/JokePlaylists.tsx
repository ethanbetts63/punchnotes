import { getServerSet } from "@/lib/serverApi";
import type { Set } from "@/lib/serverApi";
import AnnotatedBeatCarousel, { type AnnotatedBeatEntry } from "@/components/AnnotatedBeatCarousel";
import { JOKE_TYPE_STYLES } from "@/lib/tiles";

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
    seeMoreText: "See all reframes",
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
    seeMoreText: "See all phonetic matches",
    picks: [
      { set_slug: "ezuyuoP5OI8-set06-kansei-yasuda",       bit_id: "bit_002", beat_id: "bit_002_beat_001" },
      { set_slug: "GeByotNr20c-set07-colt",                bit_id: "bit_003", beat_id: "bit_003_beat_001" },
      { set_slug: "cqXwoGrebXs-set02-brandon-lacaruba",    bit_id: "bit_001", beat_id: "bit_001_beat_003" },
      { set_slug: "7AgDQxUvq6w-set02-tony-pepperoni",      bit_id: "bit_001", beat_id: "bit_001_beat_001" },
    ],
  },
  {
    type: "double-meaning",
    title: "Sneaky Double Meanings",
    description: "One word doing two jobs at the same time.",
    seeMoreText: "See all double meanings",
    picks: [
      { set_slug: "A0JWnKvtCAI-set05-hans-kim",            bit_id: "bit_001", beat_id: "bit_001_beat_001" },
      { set_slug: "3R3csSEA_JY-set05-hans-kim",            bit_id: "bit_002", beat_id: "bit_002_beat_001" },
      { set_slug: "2LGShfsvnTM-set08-mike-holder",         bit_id: "bit_001", beat_id: "bit_001_beat_001" },
      { set_slug: "g9OdSD0GkIc-set10-william-montgomery",  bit_id: "bit_003", beat_id: "bit_003_beat_001" },
      { set_slug: "lakXB1OP6Jg-set01-william-montgomery",  bit_id: "bit_005", beat_id: "bit_005_beat_001" },
      { set_slug: "R0y_PxhMdQ4-set06-collin-sledge",       bit_id: "bit_002", beat_id: "bit_002_beat_001" },
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
      { set_slug: "0DvjvaMG8RQ-set01-collin-sledge",       bit_id: "bit_002", beat_id: "bit_002_beat_001" },
      { set_slug: "xwoTIaxgeWA-set11-william-montgomery",  bit_id: "bit_004", beat_id: "bit_004_beat_001" },
      { set_slug: "oLAxMa7JVfA-set09-william-montgomery",  bit_id: "bit_003", beat_id: "bit_003_beat_002" },
      { set_slug: "6GvGjp0nYFs-set08-michael-lehrer",      bit_id: "bit_004", beat_id: "bit_004_beat_002" },
      { set_slug: "QePXRkrAEoE-set06-andrew-wolfe",        bit_id: "bit_006", beat_id: "bit_006_beat_001" },
      { set_slug: "lwLnqeBKa-0-set08-chase-standen",       bit_id: "bit_002", beat_id: "bit_002_beat_002" },
      { set_slug: "zS-4IMtyjPw-set02-duncan-stone-street", bit_id: "bit_002", beat_id: "bit_002_beat_001" },
      { set_slug: "a9Le0VGXZDU-set03-michael-hines",       bit_id: "bit_004", beat_id: "bit_004_beat_001" },
    ],
  },
  {
    type: "hyperbole",
    title: "Wild Hyperboles",
    description: "Cranked way past reality for effect.",
    seeMoreText: "See all hyperboles",
    picks: [
      { set_slug: "avLgvLtO10w-set04-steve-lee",           bit_id: "bit_001", beat_id: "bit_001_beat_002" },
      { set_slug: "M7RsTBpU5xM-set04-gary-falcon",         bit_id: "bit_003", beat_id: "bit_003_beat_001" },
      { set_slug: "3tzdqyIPcrM-set02-gabriel-kerr",        bit_id: "bit_001", beat_id: "bit_001_beat_004" },
      { set_slug: "ETk1fMPvekY-set01-casey-rocket",        bit_id: "bit_001", beat_id: "bit_001_beat_001" },
      { set_slug: "lakXB1OP6Jg-set12-ari-matti",           bit_id: "bit_004", beat_id: "bit_004_beat_001" },
      { set_slug: "A0JWnKvtCAI-set07-david-lucas",         bit_id: "bit_001", beat_id: "bit_001_beat_003" },
      { set_slug: "r2zQT6MvMXI-set01-hans-kim",            bit_id: "bit_003", beat_id: "bit_003_beat_001" },
      { set_slug: "bZ2mFX900FI-set10-martin-phillips",     bit_id: "bit_001", beat_id: "bit_001_beat_001" },
    ],
  },
  {
    type: "elephant-in-the-room",
    title: "Elephant in the Room",
    description: "The thing nobody's supposed to say — said.",
    seeMoreText: "See all elephant-in-the-room jokes",
    picks: [
      { set_slug: "KSGu1gbKP2Q-set13-martin-phillips",     bit_id: "bit_002", beat_id: "bit_002_beat_001" },
      { set_slug: "ezuyuoP5OI8-set10-lisa-smith",          bit_id: "bit_004", beat_id: "bit_004_beat_001" },
      { set_slug: "PG_8dq4YtSQ-set03-mario-zapata",         bit_id: "bit_003", beat_id: "bit_003_beat_001" },
      { set_slug: "NV6fKrnafRc-set08-jack-mcwilliams",      bit_id: "bit_002", beat_id: "bit_002_beat_002" },
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
        accentClass: JOKE_TYPE_STYLES[playlist.type]?.accent ?? "border-l-stone-300",
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
