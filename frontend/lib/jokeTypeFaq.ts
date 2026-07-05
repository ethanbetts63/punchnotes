import type { FaqItem } from "@/types/FaqItem";

// Definitions lifted from articles/how-to-annotate-jokes.md (joke types only —
// no examples, formulas, or premise structures).
export const JOKE_TYPE_FAQ: FaqItem[] = [
  {
    question: "What is a misdirect joke?",
    answer:
      "An assumption is planted, then subverted. The setup steers you toward a specific conclusion; the punchline reveals it was wrong, and you replace your first reading with the real one — you were meant to be fooled. If your first reading of the setup is still true after the punchline and you've merely gained a new angle, it's a reframe, not a misdirect.",
  },
  {
    question: "What is a reframe joke?",
    answer:
      "A known thing is given a newly visible interpretation. No false assumption is planted and no wording ambiguity is required: the setup is a plain, true statement, and the punchline overlays a second, equally-true way to see the same fact, object, behavior, or situation. Your first reading stays true — the joke adds an angle rather than replacing one.",
  },
  {
    question: "What is a phonetic-match joke?",
    answer:
      "Two different words sound alike. Often both fit the context, but sometimes the resemblance alone is the joke.",
  },
  {
    question: "What is a double-meaning joke?",
    answer:
      "The same word or phrase admits two or more readings. It hinges on semantic ambiguity, not phonetic similarity — the ambiguous word carries both meanings at once.",
  },
  {
    question: "What is a contradiction joke?",
    answer:
      "One subject holds two positions that cannot both be true; the joke is the hypocrisy or exposed inconsistency.",
  },
  {
    question: "What is an analogy joke?",
    answer:
      "Two different things are made funny by showing they share the same unexpected structure. The joke often uses \"like,\" \"as,\" \"same as,\" \"basically,\" or \"prepared me for,\" but the comparison word is not required.",
  },
  {
    question: "What is a hyperbole joke?",
    answer:
      "One dimension of a subject is stretched past plausibility. The laugh comes from excess degree, scale, or intensity.",
  },
  {
    question: "What is an elephant-in-the-room joke?",
    answer:
      "A taboo or socially avoided observation is said aloud. The audience already recognizes the conclusion; the laugh comes from breaking the silence.",
  },
  {
    question: "What is an anti-humor joke?",
    answer:
      "A joke form promises a payoff, then delivers the banal truth; the joke is that there is no joke.",
  },
];
