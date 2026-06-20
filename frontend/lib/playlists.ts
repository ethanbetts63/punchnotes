export type ListDef = {
  id: string;
  title: string;
  description: string;
  slugs: string[];
};

export const VIDEO_PLAYLISTS: ListDef[] = [
  {
    id: "allstar-guests",
    title: "Allstar Guests",
    description: "Stacked guest lineups and major-name appearances.",
    slugs: [
      "764", "740", "738", "735", "733", "717", "688", "679", "677", "670",
      "659", "658", "650", "632", "629", "627", "625", "614", "510", "222", "122",
    ],
  },
  {
    id: "kill-tony-lore",
    title: "Kill Tony Lore",
    description: "Key episodes from the show's history and recurring storylines.",
    slugs: ["578", "564", "518", "499", "498", "487", "484", "244", "200", "1"],
  },
  {
    id: "comedians-pretending-to-be-other-people",
    title: "Comedians Pretending to Be Other People",
    description: "Character episodes, impressions, and comics showing up as somebody else.",
    slugs: [
      "758", "749", "739", "709", "705", "704", "697", "689", "684", "682",
      "680", "675", "672", "666", "663", "660", "635", "630",
    ],
  },
  {
    id: "for-the-skanks",
    title: "For the Skanks",
    description: "Episodes at skankfest / featuring a LOS member.",
    slugs: [
      "767", "762", "743", "726", "714", "709", "702", "699", "698", "690",
      "686", "671", "669", "652", "651", "642", "638", "629", "619", "606",
      "582", "581", "574", "566", "561", "544", "509", "425", "414", "398",
      "394", "387", "386", "372", "371", "338", "335", "314", "288", "280",
      "277", "218", "215", "190", "186", "161", "152", "88", "42",
    ],
  },
  {
    id: "golden-ticket-episodes",
    title: "Golden Ticket Episodes",
    description: "Episodes where Tony handed out a golden ticket.",
    slugs: ["55", "42", "35", "28", "18", "12", "7", "2"],
  },
  {
    id: "adam-ray-totally-not-adam-ray",
    title: "Adam Ray + Totally Not Adam Ray",
    description: "Adam Ray appearances and character episodes.",
    slugs: [
      "761", "758", "755", "746", "739", "725", "712", "689", "684", "682",
      "672", "666", "663", "660", "647", "630", "620", "608", "594", "502",
      "417", "210", "141", "18",
    ],
  },
];

export const COMEDIAN_LISTS: ListDef[] = [
  {
    id: "regulars",
    title: "Regulars",
    description: "Comics who earned a regular spot on the show.",
    slugs: [
      "ari-matti", "casey-rocket", "david-lucas", "dedrick-flynn", "hans-kim",
      "kam-patterson", "kimberly-congdon", "malcolm-hatchett", "michael-lehrer",
      "sara-weinshenk", "vanessa-johnston", "william-montgomery",
    ],
  },
  {
    id: "golden-ticket-winners",
    title: "Golden Ticket Winners",
    description: "Comics who earned a golden ticket from Tony.",
    slugs: [
      "ahren-belisle", "aloe-mean", "angel-diaz", "aya-amarir", "carlos-lopez",
      "caroline-smith", "charlie-mac", "chris-silio", "collin-sledge", "colt",
      "drew-nickens", "enrique-chacon", "fiona-cauley", "gary-falcon",
      "heath-cordes", "jack-shaw", "jared-nathan", "jeremy", "jj-alexander",
      "john-callaghan", "kansei-yasuda", "liam-o-brian", "martin-phillips",
      "mason-bird", "nicole-tran", "orhun-timur", "pat-o-neill", "randolph-davies",
      "ric-diez", "ryan-middendorf", "steve-lee", "timmy-no-brakes", "todd-royce",
      "tony-scar", "tristan-bowling", "yaqiao-yang",
    ],
  },
];

export const SET_LISTS: ListDef[] = [
  {
    id: "stand-out-regular-sets",
    title: "Stand Out Regular Sets",
    description: "Standout sets from Kill Tony regulars.",
    slugs: [],
  },
  {
    id: "stand-out-golden-ticket-sets",
    title: "Stand Out Golden Ticket Sets",
    description: "Standout sets from golden ticket winners.",
    slugs: [],
  },
];

export const BIT_LISTS: ListDef[] = [
  {
    id: "golden-ticket-bits",
    title: "Golden Ticket Bits",
    description: "Standout bits from golden ticket winners.",
    slugs: [
      "kt582-set07-jonah-campos?bit=001&beat=001",
      "kt413-set05-nick-gianni?bit=001&beat=001",
      "kt572-set08-david-lucas?bit=001&beat=001",
    ],
  },
  {
    id: "regular-bits",
    title: "Regular Bits",
    description: "Favourite bits from the show's regulars.",
    slugs: [
      "kt492-set06-tristan-bowling?bit=001&beat=001",
      "kt529-set05-trey-pack?bit=001&beat=001",
      "kt424-set02-afrodidy?bit=001&beat=001",
    ],
  },
  {
    id: "filler-bits",
    title: "Crowd Favourites",
    description: "Bits that got a big reaction.",
    slugs: [
      "kt431-set11-steve-lardner?bit=001&beat=001",
      "kt655-set09-aldo-caldo?bit=001&beat=001",
      "kt453-set08-michael-lehrer?bit=001&beat=001",
    ],
  },
];

export type FeaturedBeatSource = {
  setSlug: string;
  bitIndex: number;
  beatIndex: number;
};

export const FEATURED_BEATS: FeaturedBeatSource[] = [
  { setSlug: "kt582-set07-jonah-campos", bitIndex: 0, beatIndex: 0 },
  { setSlug: "kt413-set05-nick-gianni", bitIndex: 0, beatIndex: 0 },
  { setSlug: "kt572-set08-david-lucas", bitIndex: 0, beatIndex: 0 },
  { setSlug: "kt431-set11-steve-lardner", bitIndex: 0, beatIndex: 0 },
  { setSlug: "kt494-set01-alex-frank-encenia", bitIndex: 0, beatIndex: 0 },
  { setSlug: "kt495-set04-cody-sylvia", bitIndex: 0, beatIndex: 0 },
  { setSlug: "kt655-set09-aldo-caldo", bitIndex: 0, beatIndex: 0 },
  { setSlug: "kt453-set01-reuben-aiken-till", bitIndex: 0, beatIndex: 0 },
];
