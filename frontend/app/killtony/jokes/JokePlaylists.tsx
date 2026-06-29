import type { BeatSearchItem } from "@/lib/serverApi";
import { jokeToTile, JOKE_TYPE_STYLES } from "@/lib/tiles";
import MediaCarousel from "@/components/MediaCarousel";

type JokeList = {
  type: string;
  title: string;
  description: string;
};

type BeatKey = { set_slug: string; bit_id: string; beat_id: string };

const JOKE_TYPE_PLAYLISTS: (JokeList & { picks: BeatKey[] })[] = [
  {
    type: "misdirect",
    title: "Top Tier Misdirects",
    description: "The setup goes one way. The punch goes somewhere else entirely.",
    picks: [
      { set_slug: "kt697-set04-joe-barnholt",    bit_id: "bit_001", beat_id: "bit_001_beat_001" },
      { set_slug: "kt724-set04-cynthia-brazil",  bit_id: "bit_004", beat_id: "bit_004_beat_001" },
      { set_slug: "kt676-set09-benjamin-grelli", bit_id: "bit_001", beat_id: "bit_001_beat_001" },
      { set_slug: "kt722-set05-michael-ridley",  bit_id: "bit_002", beat_id: "bit_002_beat_001" },
      { set_slug: "kt657-set07-kent-hunter",     bit_id: "bit_002", beat_id: "bit_002_beat_001" },
    ],
  },
  {
    type: "reframe",
    title: "Amazing Reframes",
    description: "Same words, completely different meaning by the end.",
    picks: [
      { set_slug: "kt666-set12-wendy-cressly",   bit_id: "bit_001", beat_id: "bit_001_beat_001" },
      { set_slug: "kt467-set06-michael-lehrer",  bit_id: "bit_001", beat_id: "bit_001_beat_001" },
      { set_slug: "kt575-set01-hans-kim",        bit_id: "bit_003", beat_id: "bit_003_beat_001" },
      { set_slug: "kt731-set01-martin-phillips", bit_id: "bit_002", beat_id: "bit_002_beat_002" },
      { set_slug: "kt750-set11-pauly-shore",     bit_id: "bit_002", beat_id: "bit_002_beat_001" },
    ],
  },
  {
    type: "phonetic-match",
    title: "Best Phonetic Matches",
    description: "The punchline sounds like the setup. That's the whole trick.",
    picks: [
      { set_slug: "kt669-set08-cj-gore",                  bit_id: "bit_001", beat_id: "bit_001_beat_002" },
      { set_slug: "kt741-set06-blake-jones",              bit_id: "bit_001", beat_id: "bit_001_beat_001" },
      { set_slug: "kt748-set05-mitch",                    bit_id: "bit_002", beat_id: "bit_002_beat_001" },
      { set_slug: "kt103-set01-ryan-dalton",              bit_id: "bit_002", beat_id: "bit_002_beat_001" },
      { set_slug: "kt175-set04-bradless-falactette",      bit_id: "bit_001", beat_id: "bit_001_beat_004" },
    ],
  },
  {
    type: "double-meaning",
    title: "Sneaky Double Meanings",
    description: "One word doing two jobs at the same time.",
    picks: [
      { set_slug: "kt148-set09-stevie-timble",   bit_id: "bit_001", beat_id: "bit_001_beat_004" },
      { set_slug: "kt531-set08-ellis-h",         bit_id: "bit_003", beat_id: "bit_003_beat_001" },
      { set_slug: "kt670-set08-trey-on-stage",   bit_id: "bit_004", beat_id: "bit_004_beat_001" },
      { set_slug: "kt417-set04-mitchell-lamar",  bit_id: "bit_003", beat_id: "bit_003_beat_001" },
      { set_slug: "kt495-set09-jesse-jacobson",  bit_id: "bit_003", beat_id: "bit_003_beat_001" },
    ],
  },
  {
    type: "contradiction",
    title: "Sharp Contradictions",
    description: "The punchline says the opposite of what the setup implied.",
    picks: [
      { set_slug: "kt654-set02-jackson-nami",  bit_id: "bit_001", beat_id: "bit_001_beat_001" },
      { set_slug: "kt412-set05-angel-johnson", bit_id: "bit_004", beat_id: "bit_004_beat_001" },
      { set_slug: "kt764-set01-dedrick-flynn", bit_id: "bit_001", beat_id: "bit_001_beat_002" },
      { set_slug: "kt700-set05-matt-edgar",    bit_id: "bit_001", beat_id: "bit_001_beat_002" },
      { set_slug: "kt513-set10-michael-ehr",   bit_id: "bit_004", beat_id: "bit_004_beat_001" },
    ],
  },
  {
    type: "analogy",
    title: "Killer Analogies",
    description: "An unexpected comparison that makes the bit land harder.",
    picks: [
      { set_slug: "kt225-set05-tierney-michon", bit_id: "bit_002", beat_id: "bit_002_beat_001" },
      { set_slug: "kt664-set08-jacob-cantor",   bit_id: "bit_001", beat_id: "bit_001_beat_001" },
      { set_slug: "kt766-set12-caleb-andrews",  bit_id: "bit_004", beat_id: "bit_004_beat_002" },
      { set_slug: "kt654-set02-jackson-nami",   bit_id: "bit_004", beat_id: "bit_004_beat_001" },
      { set_slug: "kt506-set01-paul-cyphers",   bit_id: "bit_003", beat_id: "bit_003_beat_002" },
    ],
  },
  {
    type: "hyperbole",
    title: "Wild Hyperboles",
    description: "Cranked way past reality for effect.",
    picks: [
      { set_slug: "kt592-set08-david-lucas",         bit_id: "bit_002", beat_id: "bit_002_beat_001" },
      { set_slug: "kt587-set07-william-montgomery",  bit_id: "bit_001", beat_id: "bit_001_beat_001" },
      { set_slug: "kt594-set06-mia-chan",            bit_id: "bit_002", beat_id: "bit_002_beat_001" },
      { set_slug: "kt711-set02-jovan-afzali",        bit_id: "bit_003", beat_id: "bit_003_beat_002" },
      { set_slug: "kt430-set04-steve-lee",           bit_id: "bit_001", beat_id: "bit_001_beat_001" },
    ],
  },
  {
    type: "elephant-in-the-room",
    title: "Elephant in the Room",
    description: "The thing nobody's supposed to say — said.",
    picks: [
      { set_slug: "kt682-set06-joe-derosa",    bit_id: "bit_004", beat_id: "bit_004_beat_001" },
      { set_slug: "kt588-set06-mr-hip-hop",    bit_id: "bit_001", beat_id: "bit_001_beat_002" },
      { set_slug: "kt762-set04-joe-ellis",     bit_id: "bit_007", beat_id: "bit_007_beat_001" },
      { set_slug: "kt421-set06-chuck-davidson",bit_id: "bit_003", beat_id: "bit_003_beat_001" },
      { set_slug: "kt707-set26-mario-zapata",  bit_id: "bit_003", beat_id: "bit_003_beat_001" },
    ],
  },
];


export default function JokePlaylists({ jokes }: { jokes: BeatSearchItem[] }) {
  const lists = JOKE_TYPE_PLAYLISTS
    .map((playlist) => {
      const items = playlist.picks
        .map((pick) => jokes.find(
          (j) => j.set_slug === pick.set_slug && j.bit_id === pick.bit_id && j.beat_id === pick.beat_id
        ))
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
