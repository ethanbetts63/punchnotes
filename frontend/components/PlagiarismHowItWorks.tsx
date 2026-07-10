import { ClipboardPaste, ScanSearch, ListChecks } from "lucide-react";

const steps = [
  {
    level: "01",
    title: "Paste your joke.",
    description:
      "A premise, a bit, or a full chunk of material — up to 2,000 characters.",
    icon: ClipboardPaste,
  },
  {
    level: "02",
    title: "We compare it line by line.",
    description:
      "Your text is matched against every joke in the database using semantic similarity, not just word overlap.",
    icon: ScanSearch,
  },
  {
    level: "03",
    title: "See the closest matches.",
    description:
      "The top matches show the full joke with line-level highlights, linked straight to the set and timestamp.",
    icon: ListChecks,
  },
];

export default function PlagiarismHowItWorks() {
  return (
    <section>
      <h2 className="mb-6 text-2xl font-bold text-stone-900">How it works</h2>

      <div className="grid gap-4 sm:grid-cols-3">
        {steps.map((step) => {
          const Icon = step.icon;
          return (
            <div key={step.level} className="rounded-xl border border-stone-200 bg-white p-5">
              <div className="flex items-center justify-between gap-3">
                <span className="inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-primary/10 text-primary">
                  <Icon className="h-5 w-5" />
                </span>
                <span className="text-sm font-bold tracking-[0.24em] text-stone-300">{step.level}</span>
              </div>

              <h3 className="mt-5 text-lg font-bold tracking-tight text-stone-900">{step.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-stone-500">{step.description}</p>
            </div>
          );
        })}
      </div>
    </section>
  );
}
