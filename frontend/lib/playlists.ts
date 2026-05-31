export type ListDef = {
  id: string;
  title: string;
  description: string;
  ids: number[];
  matchBy?: "id" | "number";
};

export const EPISODE_LISTS: ListDef[] = [
  {
    id: "adam-ray-totally-not-adam-ray",
    title: "Adam Ray + Totally Not Adam Ray",
    description: "Adam Ray appearances and character episodes.",
    matchBy: "number",
    ids: [
      18, 141, 210, 417, 502, 594, 608, 620, 630, 647, 660, 663,
      666, 672, 682, 684, 689, 712, 725, 739, 746, 755, 758, 761,
    ],
  },
  {
    id: "allstar-guests",
    title: "Allstar Guests",
    description: "Stacked guest lineups and major-name appearances.",
    matchBy: "number",
    ids: [
      670, 625, 679, 738, 677, 658, 650, 629, 740, 733, 659, 764,
      688, 735, 632, 717, 627, 614, 510, 122, 222,
    ],
  },
  {
    id: "kill-tony-lore",
    title: "Kill Tony Lore",
    description: "Key episodes from the show's history and recurring storylines.",
    matchBy: "number",
    ids: [564, 244, 498, 1, 499, 518, 487, 484, 200, 578],
  },
  {
    id: "comedians-pretending-to-be-other-people",
    title: "Comedians Pretending to Be Other People",
    description: "Character episodes, impressions, and comics showing up as somebody else.",
    matchBy: "number",
    ids: [
      758, 749, 739, 705, 704, 689, 684, 682, 680, 675, 672, 666,
      663, 660, 635, 630,
    ],
  },
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
      53, 29, 192, 20, 54, 40,
    ],
  },
  {
    id: "golden-ticket-winners",
    title: "Golden Ticket Winners",
    description: "Comics who earned a golden ticket from Tony.",
    ids: [
      306, 32, 257, 58, 41, 77, 169, 13, 93, 245, 120, 97, 215,
    ],
  },
];

export const SET_LISTS: ListDef[] = [
  {
    id: "golden-ticket-first-sets",
    title: "Golden Ticket Debuts",
    description: "The first appearance of every comedian who went on to win a golden ticket.",
    ids: [
      346, 26, 282, 55, 145, 156, 491, 90, 89, 489, 119, 95, 235,
    ],
  },
  {
    id: "regular-first-sets",
    title: "Regular Debuts",
    description: "The first appearance of every comedian who became a regular.",
    ids: [
      142, 25, 211, 421, 51, 37,
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
