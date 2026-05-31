export type ListDef = {
  id: string;
  title: string;
  description: string;
  ids: number[];
};

export const EPISODE_LISTS: ListDef[] = [
  {
    id: "milestone-episodes",
    title: "Milestone Episodes",
    description: "Big number episodes and live specials.",
    ids: [1, 10, 20, 30, 40, 50, 60, 70],
  },
  {
    id: "golden-ticket-episodes",
    title: "Golden Ticket Episodes",
    description: "Episodes where Tony handed out a golden ticket.",
    ids: [2, 7, 12, 18, 28, 35, 42, 55],
  },
  {
    id: "biggest-lineups",
    title: "Biggest Lineups",
    description: "Episodes with the most sets on the night.",
    ids: [5, 15, 25, 35, 45, 55, 65, 75],
  },
];

export const COMEDIAN_LISTS: ListDef[] = [
  {
    id: "regulars",
    title: "Regulars",
    description: "Comics who earned a regular spot on the show.",
    ids: [
      167, 6, 34, 35, 229, 56, 196, 401, 53, 205, 1, 415, 233, 110, 20,
      317, 180, 161, 407, 74, 451, 525, 431, 172, 85, 538, 4, 276, 122,
      147, 52, 13, 113, 48, 112, 107, 129, 191, 435, 217, 249, 80, 70, 255,
    ],
  },
  {
    id: "golden-ticket-winners",
    title: "Golden Ticket Winners",
    description: "Comics who earned a golden ticket from Tony.",
    ids: [
      290, 102, 174, 1, 392, 7, 239, 280, 45, 119, 50, 71, 147, 464, 13,
      217, 116, 92, 187, 58, 255,
    ],
  },
];

export const SET_LISTS: ListDef[] = [
  {
    id: "golden-ticket-first-sets",
    title: "Golden Ticket Debuts",
    description: "The first appearance of every comedian who went on to win a golden ticket.",
    ids: [
      516, 93, 177, 644, 456, 5, 246, 296, 134, 109, 43, 122, 660, 544,
      78, 656, 107, 83, 188, 52, 592,
    ],
  },
  {
    id: "regular-first-sets",
    title: "Regular Debuts",
    description: "The first appearance of every comedian who became a regular.",
    ids: [
      168, 4, 51, 31, 234, 49, 197, 464, 137, 207, 644, 482, 240, 520,
      318, 638, 182, 330, 470, 67, 528, 620, 500, 174, 74, 640, 171, 290,
      113, 660, 45, 78, 103, 41, 102, 195, 121, 192, 504, 656, 630, 71,
      116, 592,
    ],
  },
];

export const BIT_LISTS: ListDef[] = [
  {
    id: "golden-ticket-bits",
    title: "Golden Ticket Bits",
    description: "Standout bits from golden ticket winners.",
    ids: [144, 145, 209, 303, 92, 240, 11, 620, 621, 510, 375, 754, 395],
  },
  {
    id: "regular-bits",
    title: "Regular Bits",
    description: "Favourite bits from the show's regulars.",
    ids: [695, 46, 72, 5, 241, 1037, 917, 159, 160, 67, 74, 171],
  },
  {
    id: "filler-bits",
    title: "Crowd Favourites",
    description: "Bits that got a big reaction.",
    ids: [415, 304, 275, 324, 478, 152, 117, 93, 94, 162, 161, 346, 347],
  },
];
