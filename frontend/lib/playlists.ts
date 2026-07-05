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
    slugs: ["758", "578", "564", "518", "499", "498", "487", "484", "244", "200", "1"],
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
      "pat-o-neill", "sara-weinshenk", "vanessa-johnston", "william-montgomery",
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
    id: "must-watch-sets",
    title: "Must Watch Sets",
    description: "Sets you can't afford to skip.",
    slugs: [
      "mAaNTFHDovs-set09-ari-matti",
      "11FD8eVzsfk-set01-casey-rocket",
      "1upKa86_uKU-set06-pat-o-neill",
      "ezuyuoP5OI8-set06-kansei-yasuda",
      "GZuIpWgRzgo-set07-collin-sledge",
      "7AgDQxUvq6w-set07-chris-silio",
      "M7RsTBpU5xM-set04-gary-falcon",
      "7AgDQxUvq6w-set02-tony-pepperoni",
      "QePXRkrAEoE-set04-dex",
    ],
  },
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
      "NoUJl5eZOzw-set07-jonah-campos?bit=001&beat=001",
      "8LUSZuuQano-set05-nick-gianni?bit=001&beat=001",
      "VopdOOBFE_M-set08-david-lucas?bit=001&beat=001",
    ],
  },
  {
    id: "regular-bits",
    title: "Regular Bits",
    description: "Favourite bits from the show's regulars.",
    slugs: [
      "0MpZF1HsZSc-set06-tristan-bowling?bit=001&beat=001",
      "-8Qw-1aa1WM-set05-trey-pack?bit=001&beat=001",
      "6GvGjp0nYFs-set02-afrodidy?bit=001&beat=001",
    ],
  },
  {
    id: "filler-bits",
    title: "Crowd Favourites",
    description: "Bits that got a big reaction.",
    slugs: [
      "_IWBzZHL0xw-set11-steve-lardner?bit=001&beat=001",
      "FVR-v_WUYJk-set09-aldo-caldo?bit=001&beat=001",
      "9jb4OkKRADo-set08-michael-lehrer?bit=001&beat=001",
    ],
  },
];

export type FeaturedBeatSource = {
  setSlug: string;
  bitIndex: number;
  beatIndex: number;
};

export const FEATURED_BEATS: FeaturedBeatSource[] = [
  { setSlug: "1upKa86_uKU-set06-pat-o-neill", bitIndex: 1, beatIndex: 0 },
  { setSlug: "A0JWnKvtCAI-set05-hans-kim", bitIndex: 0, beatIndex: 0 },
  { setSlug: "a9Le0VGXZDU-set03-michael-hines", bitIndex: 3, beatIndex: 0 },
  { setSlug: "RQ7Uk4vTPtk-set04-todd-royce", bitIndex: 2, beatIndex: 0 },
  { setSlug: "lakXB1OP6Jg-set01-william-montgomery", bitIndex: 4, beatIndex: 0 },
];
