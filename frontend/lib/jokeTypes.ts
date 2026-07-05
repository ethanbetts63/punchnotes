import type { FaqItem } from "@/types/FaqItem";

export type JokeTypeDef = {
  id: string;
  label: string;
  question: string;
  answer: string;
  badgeClass: string;
  accentClass: string;
};

export const JOKE_TYPES: JokeTypeDef[] = [
  {
    id: "misdirect",
    label: "misdirect",
    question: "What is a misdirect joke?",
    answer:
      "An assumption is planted, then subverted. The setup steers you toward a specific conclusion; the punchline reveals it was wrong, and you replace your first reading with the real one - you were meant to be fooled. If your first reading of the setup is still true after the punchline and you've merely gained a new angle, it's a reframe, not a misdirect.",
    badgeClass: "bg-red-500 text-white",
    accentClass: "border-l-red-500",
  },
  {
    id: "reframe",
    label: "reframe",
    question: "What is a reframe joke?",
    answer:
      "A known thing is given a newly visible interpretation. No false assumption is planted and no wording ambiguity is required: the setup is a plain, true statement, and the punchline overlays a second, equally-true way to see the same fact, object, behavior, or situation. Your first reading stays true - the joke adds an angle rather than replacing one.",
    badgeClass: "bg-blue-500 text-white",
    accentClass: "border-l-blue-500",
  },
  {
    id: "phonetic-match",
    label: "phonetic-match",
    question: "What is a phonetic-match joke?",
    answer:
      "Two different words sound alike. Often both fit the context, but sometimes the resemblance alone is the joke.",
    badgeClass: "bg-amber-400 text-stone-900",
    accentClass: "border-l-amber-400",
  },
  {
    id: "double-meaning",
    label: "double-meaning",
    question: "What is a double-meaning joke?",
    answer:
      "The same word or phrase admits two or more readings. It hinges on semantic ambiguity, not phonetic similarity - the ambiguous word carries both meanings at once.",
    badgeClass: "bg-violet-500 text-white",
    accentClass: "border-l-violet-500",
  },
  {
    id: "contradiction",
    label: "contradiction",
    question: "What is a contradiction joke?",
    answer:
      "One subject holds two positions that cannot both be true; the joke is the hypocrisy or exposed inconsistency.",
    badgeClass: "bg-orange-500 text-white",
    accentClass: "border-l-orange-500",
  },
  {
    id: "analogy",
    label: "analogy",
    question: "What is an analogy joke?",
    answer:
      "Two different things are made funny by showing they share the same unexpected structure. The joke often uses \"like,\" \"as,\" \"same as,\" \"basically,\" or \"prepared me for,\" but the comparison word is not required.",
    badgeClass: "bg-emerald-500 text-white",
    accentClass: "border-l-emerald-500",
  },
  {
    id: "hyperbole",
    label: "hyperbole",
    question: "What is a hyperbole joke?",
    answer:
      "One dimension of a subject is stretched past plausibility. The laugh comes from excess degree, scale, or intensity.",
    badgeClass: "bg-pink-500 text-white",
    accentClass: "border-l-pink-500",
  },
  {
    id: "elephant-in-the-room",
    label: "elephant-in-the-room",
    question: "What is an elephant-in-the-room joke?",
    answer:
      "A taboo or socially avoided observation is said aloud. The audience already recognizes the conclusion; the laugh comes from breaking the silence.",
    badgeClass: "bg-cyan-500 text-white",
    accentClass: "border-l-cyan-500",
  },
  {
    id: "anti-humor",
    label: "anti-humor",
    question: "What is an anti-humor joke?",
    answer:
      "A joke form promises a payoff, then delivers the banal truth; the joke is that there is no joke.",
    badgeClass: "bg-stone-700 text-white",
    accentClass: "border-l-stone-700",
  },
  {
    id: "absurdism",
    label: "absurdism",
    question: "What is an absurdism joke?",
    answer:
      "The payoff is random given the setup. No assumption is subverted and no second true reading is added; the joke comes from a frame being met with a non sequitur with no connecting logic.",
    badgeClass: "bg-lime-500 text-stone-950",
    accentClass: "border-l-lime-500",
  },
];

export const JOKE_TYPE_FAQ: FaqItem[] = JOKE_TYPES.map(({ question, answer }) => ({ question, answer }));

export const JOKE_TYPE_FILTER_OPTIONS = [
  { value: "", label: "All types" },
  ...JOKE_TYPES.map(({ id, label }) => ({ value: id, label })),
];

const JOKE_TYPE_STYLES = Object.fromEntries(
  JOKE_TYPES.map(({ id, badgeClass, accentClass }) => [id, { badge: badgeClass, accent: accentClass }])
) as Record<string, { badge: string; accent: string }>;

export function getJokeTypeStyle(jokeType: string | null | undefined) {
  return jokeType ? JOKE_TYPE_STYLES[jokeType] : undefined;
}
