export type ListDef = {
  id: string;
  title: string;
  description: string;
  ids: number[];
};

// All IDs below are placeholders — replace with real database IDs.

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
    id: "most-appearances",
    title: "Most Appearances",
    description: "Comics who keep coming back to the bucket.",
    ids: [1, 2, 3, 4, 5, 6, 7, 8],
  },
  {
    id: "golden-ticket-winners",
    title: "Golden Ticket Winners",
    description: "Comics who earned a golden ticket from Tony.",
    ids: [9, 10, 11, 12, 13, 14, 15, 16],
  },
  {
    id: "large-joke-book",
    title: "Large Joke Book",
    description: "Comics Tony gave a large joke book to.",
    ids: [17, 18, 19, 20, 21, 22, 23, 24],
  },
];

export const SET_LISTS: ListDef[] = [
  {
    id: "first-regular-sets",
    title: "First Regular Sets",
    description: "The debut set from each comedian who became a regular.",
    ids: [1, 5, 9, 13, 17, 21, 25, 29],
  },
  {
    id: "large-joke-book-sets",
    title: "Large Joke Book Sets",
    description: "Sets that earned a large joke book award.",
    ids: [3, 7, 11, 15, 19, 23, 27, 31],
  },
  {
    id: "golden-ticket-sets",
    title: "Golden Ticket Sets",
    description: "The sets where a golden ticket was awarded.",
    ids: [2, 6, 10, 14, 18, 22, 26, 30],
  },
];

export const BIT_LISTS: ListDef[] = [
  {
    id: "best-misdirects",
    title: "Best Misdirects",
    description: "Bits built around the classic misdirect structure.",
    ids: [1, 4, 8, 12, 16, 20, 24, 28],
  },
  {
    id: "hyperbole-bits",
    title: "Hyperbole Bits",
    description: "Bits that lean hard into exaggeration.",
    ids: [2, 5, 9, 13, 17, 21, 25, 29],
  },
  {
    id: "double-meaning-bits",
    title: "Double Meaning",
    description: "Jokes that pivot on a word with two readings.",
    ids: [3, 6, 10, 14, 18, 22, 26, 30],
  },
];
