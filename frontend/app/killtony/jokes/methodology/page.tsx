import Link from "next/link";
import { SITE_URL, buildBreadcrumbSchema } from "@/lib/seo";

export const metadata = {
  title: "How We Classify Jokes - Kill Tony | PunchNotes",
  description:
    "A detailed look at how PunchNotes labels every line and assigns a joke type to each beat in Kill Tony sets.",
};

const schema = {
  "@context": "https://schema.org",
  "@type": "Article",
  headline: "How We Classify Jokes",
  description:
    "A detailed look at how PunchNotes labels every line and assigns a joke type to each beat in Kill Tony sets.",
  url: `${SITE_URL}/killtony/jokes/methodology`,
  breadcrumb: buildBreadcrumbSchema([
    { name: "Kill Tony", item: `${SITE_URL}/killtony` },
    { name: "Jokes", item: `${SITE_URL}/killtony/jokes` },
    { name: "How We Classify Jokes", item: `${SITE_URL}/killtony/jokes/methodology` },
  ]),
};

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mb-12">
      <h2 className="mb-4 text-2xl font-bold text-stone-900">{title}</h2>
      {children}
    </section>
  );
}

function JokeType({
  name,
  formula,
  definition,
  setup,
  punchline,
  premise,
}: {
  name: string;
  formula: string;
  definition: string;
  setup: string[];
  punchline: string;
  premise: string;
}) {
  return (
    <div className="mb-8 rounded-xl border border-stone-200 p-6">
      <div className="mb-3 flex items-center gap-3">
        <span className="inline-flex items-center rounded-full bg-primary/10 px-3 py-1 text-sm font-semibold text-primary">
          {name}
        </span>
      </div>
      <p className="mb-3 text-stone-700">{definition}</p>
      <p className="mb-4 text-sm font-medium text-stone-500">
        Formula:{" "}
        <span className="font-mono text-stone-700">{formula}</span>
      </p>
      <div className="rounded-lg bg-stone-50 p-4">
        <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-stone-400">Example</p>
        <div className="space-y-1">
          {setup.map((line, i) => (
            <p key={i} className="text-sm text-stone-500 italic">{line}</p>
          ))}
          <p className="text-sm font-semibold text-stone-900">{punchline}</p>
        </div>
        <p className="mt-3 border-t border-stone-200 pt-3 text-sm text-stone-500">
          <span className="font-medium text-stone-700">Premise:</span>{" "}
          <span className="italic">&ldquo;{premise}&rdquo;</span>
        </p>
      </div>
    </div>
  );
}

function LineLabel({
  label,
  definition,
}: {
  label: string;
  definition: string;
}) {
  return (
    <div className="mb-4 flex gap-4">
      <span className="mt-0.5 shrink-0 rounded bg-stone-100 px-2 py-0.5 font-mono text-sm font-semibold text-stone-700">
        {label}
      </span>
      <p className="text-stone-600">{definition}</p>
    </div>
  );
}

export default function MethodologyPage() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
      />
      <div className="min-h-screen bg-white">
        <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6">
          <Link
            href="/killtony/jokes"
            className="mb-8 inline-flex items-center gap-1.5 text-sm font-medium text-stone-500 transition-colors hover:text-stone-900"
          >
            &larr; Jokes
          </Link>

          <h1 className="mb-3 text-4xl font-black tracking-tight text-stone-950">
            How We Classify Jokes
          </h1>
          <p className="mb-12 text-lg text-stone-500">
            Every joke in the Kill Tony database is annotated at the line level and assigned a structural type. Here&rsquo;s exactly how that works.
          </p>

          <Section title="Line labels">
            <p className="mb-6 text-stone-600">
              Before we can assign a joke type, every line in a set gets one of four labels. These labels describe the structural role each line plays in delivering a joke.
            </p>
            <LineLabel
              label="setup"
              definition="A line that establishes the premise, scenario, or context for a joke — building toward the laugh without delivering it."
            />
            <LineLabel
              label="punchline"
              definition="The line where the laugh lands. The reveal, twist, or payoff the setup was building toward. Every joke beat has exactly one punchline."
            />
            <LineLabel
              label="tag"
              definition="An additional punchline that builds off the previous one without needing new setup. A tag rides on the laugh already in the room. If it introduces fresh material, it becomes new setup for the next beat."
            />
            <LineLabel
              label="fluff"
              definition="Everything that isn't doing comedic work: greetings, sign-offs, name introductions, verbal stumbles, sound effects, and crowd-acknowledgement filler."
            />
          </Section>

          <Section title="Bits and beats">
            <p className="mb-4 text-stone-600">
              Jokes are organized into a two-level hierarchy.
            </p>
            <div className="mb-6 space-y-4">
              <div className="rounded-xl border border-stone-200 p-5">
                <h3 className="mb-1 font-semibold text-stone-900">Beat</h3>
                <p className="text-stone-600">
                  A single setup–punchline–tags unit with its own specific comedic logic. Every beat contains at least one punchline. A new beat starts at the first setup line after a punchline lands.
                </p>
              </div>
              <div className="rounded-xl border border-stone-200 p-5">
                <h3 className="mb-1 font-semibold text-stone-900">Bit</h3>
                <p className="text-stone-600">
                  One or more beats that share an overarching premise. The test for whether two beats belong in the same bit: can you extract one beat alone and still have it make sense? If yes, it&rsquo;s its own bit. If not — because it depends on a premise established by another beat — they belong together.
                </p>
              </div>
            </div>
            <p className="text-stone-600">
              Shared subject matter alone doesn&rsquo;t make two beats the same bit. A comedian can do five different jokes about their marriage and each may be its own standalone bit if they each set up and pay off independently.
            </p>
          </Section>

          <Section title="Joke types">
            <p className="mb-8 text-stone-600">
              Every beat gets assigned one of nine joke types based on the underlying comedic mechanism — the reason the joke is funny, not what it&rsquo;s about. We also write a one-sentence <span className="font-medium text-stone-900">premise</span> for each beat that captures the abstract logic using a type-specific formula.
            </p>

            <JokeType
              name="misdirect"
              definition="An assumption is planted, then subverted. The audience follows one logical path and is suddenly rerouted."
              formula="[bait] implies [implication], but reveals [reveal]."
              setup={[
                `"My son just came out as trans."`,
                `"Well, shouldn't call him my son anymore."`,
              ]}
              punchline={`"Now that he's dead to me,"`}
              premise="Refusing to call a transitioning child your son implies a new title, but reveals disownment."
            />

            <JokeType
              name="reframe"
              definition="A known thing is given a newly visible interpretation. No false assumption is planted — the joke surfaces an alternate perspective on the same fact, object, behavior, or situation."
              formula="[subject] could be [reframe]."
              setup={[`"They got him on puberty blockers"`]}
              punchline={`"or as pedophiles call them, preservatives."`}
              premise="Puberty blockers could be beneficial to pedophiles."
            />

            <JokeType
              name="phonetic-match"
              definition="Two different words sound alike. The resemblance itself — or the fact that both words fit the context — is the joke."
              formula={`"[heard]" sounds like "[reheard]", and "[reheard]" fits because [reason].`}
              setup={[`"What do you call a little person with ADHD?"`]}
              punchline={`"That's right, a fidget."`}
              premise={`"Midget" sounds like "fidget", and "fidget" fits because ADHD.`}
            />

            <JokeType
              name="double-meaning"
              definition="The same word or phrase admits two or more readings. The joke hinges on semantic ambiguity, not phonetic similarity."
              formula={`"[phrase]" can mean [expected] or [comic].`}
              setup={[`"'In case of fire, use stairs.'"`]}
              punchline={`"Fuck that, let's use water."`}
              premise={`"In case of fire, use stairs" can mean use stairs during a fire or use stairs to fight a fire.`}
            />

            <JokeType
              name="contradiction"
              definition="One subject holds two positions that cannot both be true. The joke is the hypocrisy or exposed inconsistency."
              formula="[subject] both [a] and yet [b]."
              setup={[
                `"My girlfriend thinks The Godfather is too long,"`,
                `"but her story about when her coworker was bitchy to her two years ago is..."`,
              ]}
              punchline={`"the perfect length."`}
              premise="Women both find good movies too long and yet tell long stories."
            />

            <JokeType
              name="analogy"
              definition="Two different things are made funny by showing they share the same unexpected structure."
              formula="[X] is like [Y] because both [shared structure]."
              setup={[
                `"Golfing prepared me for marriage,"`,
                `"cause both involved me spending a lot of money"`,
              ]}
              punchline={`"at something I'm not really good at."`}
              premise="Golf is like marriage because both involve expensive repeated failure."
            />

            <JokeType
              name="hyperbole"
              definition="One dimension of a subject is stretched past plausibility. The laugh comes from excess degree, scale, or intensity."
              formula="[subject] becomes so extreme that [extreme]."
              setup={[
                `"So I've already seen a third of this collection"`,
                `"and I don't have enough bodily fluids"`,
              ]}
              punchline={`"for the other two thirds of this collection."`}
              premise="A porn collection becomes so extreme that you run out of sperm."
            />

            <JokeType
              name="elephant-in-the-room"
              definition="A taboo or socially avoided observation is said aloud. The audience already recognizes the conclusion; the laugh comes from breaking the silence."
              formula="[elephant] is widely understood but rarely said aloud."
              setup={[`"You know, these shootings are often done by the same race."`]}
              punchline={`"I'm looking at you, honkies."`}
              premise="White men dominate mass shootings is widely understood but rarely said aloud."
            />

            <JokeType
              name="anti-humor"
              definition="A joke form promises a payoff, then delivers the banal truth. The joke is that there is no joke."
              formula="[frame] implies a punchline, but reveals only [answer]."
              setup={[
                `"A duck walks into a pharmacy with a rash on his beak."`,
                `"He asks the pharmacist for some ointment."`,
              ]}
              punchline={`"Sorry, we don't have medicine for ducks here."`}
              premise="An animal asking a business for service implies a punchline, but reveals only that the business does not serve animals."
            />
          </Section>

          <div className="border-t border-stone-200 pt-8 text-stone-500">
            <p>
              Browse jokes by type using the filters on the{" "}
              <Link href="/killtony/jokes" className="text-primary underline underline-offset-2 hover:text-primary/80">
                jokes page
              </Link>
              .
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
