export const metadata = {
  title: "About — JokeScore",
  description: "What JokeScore is and why it exists.",
};

export default function AboutPage() {
  return (
    <div className="bg-white min-h-screen">
      <div className="mx-auto max-w-2xl px-4 py-16 sm:px-6">
        <h1 className="text-3xl font-bold text-stone-900">About JokeScore</h1>

        <div className="mt-8 space-y-6 text-stone-600 leading-relaxed">
          <p>
            JokeScore is a system for analysing stand-up comedy at the structural level — connecting
            how jokes are built to how audiences actually respond.
          </p>
          <p>
            The project starts with Kill Tony because it provides a uniquely useful dataset: short
            standardised sets, high performance variance, recurring comedians, live audience reactions,
            and explicit quality signals like joke book awards.
          </p>
          <p>
            Every set is annotated line by line — setup, punchline, tag, fluff — then grouped into
            bits and beats. Each beat gets a premise, a joke mechanism, and topic labels. The goal is
            to understand which structures reliably produce laughter, and why the same premise lands
            differently in different hands.
          </p>
          <p>
            From there the system will expand into broader stand-up datasets and eventually become
            both a comedy analytics platform and a training dataset for AI systems that learn humor
            from actual audience response rather than text alone.
          </p>
        </div>
      </div>
    </div>
  );
}
