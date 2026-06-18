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
    id: "golden-ticket-first-sets",
    title: "Golden Ticket Debuts",
    description: "The first appearance of every comedian who went on to win a golden ticket.",
    slugs: ["346", "26", "282", "55", "145", "156", "491", "90", "89", "489", "119", "95", "235"],
  },
  {
    id: "regular-first-sets",
    title: "Regular Debuts",
    description: "The first appearance of every comedian who became a regular.",
    slugs: ["142", "25", "211", "421", "51", "37"],
  },
];

export const BIT_LISTS: ListDef[] = [
  {
    id: "golden-ticket-bits",
    title: "Golden Ticket Bits",
    description: "Standout bits from golden ticket winners.",
    slugs: ["144", "145", "209", "303", "92", "240", "11", "620", "621", "510", "375", "754", "395"],
  },
  {
    id: "regular-bits",
    title: "Regular Bits",
    description: "Favourite bits from the show's regulars.",
    slugs: ["695", "46", "72", "5", "241", "1037", "917", "159", "160", "67", "74", "171"],
  },
  {
    id: "filler-bits",
    title: "Crowd Favourites",
    description: "Bits that got a big reaction.",
    slugs: ["415", "304", "275", "324", "478", "152", "117", "93", "94", "162", "161", "346", "347"],
  },
];

export type FeaturedBeatSource = {
  setId: number;
  bitIndex: number;
  beatIndex: number;
};

export const FEATURED_BEATS: FeaturedBeatSource[] = [
  { setId: 346, bitIndex: 0, beatIndex: 0 },
  { setId: 26, bitIndex: 0, beatIndex: 0 },
  { setId: 282, bitIndex: 0, beatIndex: 0 },
  { setId: 55, bitIndex: 0, beatIndex: 0 },
  { setId: 145, bitIndex: 0, beatIndex: 0 },
  { setId: 156, bitIndex: 0, beatIndex: 0 },
  { setId: 491, bitIndex: 0, beatIndex: 0 },
  { setId: 90, bitIndex: 0, beatIndex: 0 },
];
