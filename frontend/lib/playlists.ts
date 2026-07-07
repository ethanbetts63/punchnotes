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
    description: "Key episodes from the show's history that you need to watch to understand.",
    slugs: ["733", "726", "578", "564", "518", "499", "498", "487", "484", "244", "200", "1"],
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
  }
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
      "mAaNTFHDovs-5134-ari-matti",
      "11FD8eVzsfk-456-casey-rocket",
      "1upKa86_uKU-3595-pat-o-neill",
      "ezuyuoP5OI8-3382-kansei-yasuda",
      "GZuIpWgRzgo-4118-collin-sledge",
      "7AgDQxUvq6w-4531-chris-silio",
      "M7RsTBpU5xM-1685-gary-falcon",
      "7AgDQxUvq6w-1296-tony-pepperoni",
      "QePXRkrAEoE-2058-dex",
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
      "NoUJl5eZOzw-3819-jonah-campos?bit=001&beat=001",
      "8LUSZuuQano-3027-nick-gianni?bit=001&beat=001",
      "VopdOOBFE_M-5066-david-lucas?bit=001&beat=001",
    ],
  },
  {
    id: "regular-bits",
    title: "Regular Bits",
    description: "Favourite bits from the show's regulars.",
    slugs: [
      "0MpZF1HsZSc-3548-tristan-bowling?bit=001&beat=001",
      "-8Qw-1aa1WM-2389-trey-pack?bit=001&beat=001",
      "6GvGjp0nYFs-1265-aphrodite?bit=001&beat=001",
    ],
  },
  {
    id: "filler-bits",
    title: "Crowd Favourites",
    description: "Bits that got a big reaction.",
    slugs: [
      "_IWBzZHL0xw-7144-steve-lardner?bit=001&beat=001",
      "FVR-v_WUYJk-5315-aldo-caldo?bit=001&beat=001",
      "9jb4OkKRADo-5549-michael-lehrer?bit=001&beat=001",
    ],
  },
];

export type FeaturedBeatSource = {
  setSlug: string;
  bitIndex: number;
  beatIndex: number;
};

export const FEATURED_BEATS: FeaturedBeatSource[] = [
  { setSlug: "1upKa86_uKU-3595-pat-o-neill", bitIndex: 1, beatIndex: 0 },
  { setSlug: "A0JWnKvtCAI-2997-hans-kim", bitIndex: 0, beatIndex: 0 },
  { setSlug: "a9Le0VGXZDU-1693-michael-hines", bitIndex: 3, beatIndex: 0 },
  { setSlug: "RQ7Uk4vTPtk-1970-todd-royce", bitIndex: 2, beatIndex: 0 },
  { setSlug: "lakXB1OP6Jg-1082-william-montgomery", bitIndex: 4, beatIndex: 0 },
];
