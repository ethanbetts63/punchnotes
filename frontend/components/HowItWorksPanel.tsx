import Link from "next/link";
import { ArrowLeft, ArrowRight, Mic2, Search, Tv } from "lucide-react";

const steps = [
  {
    level: "01",
    title: "Pick an entry point.",
    description:
      "Browse curated playlists for episodes, comedians and sets. Or search to find something specific.",
    href: "/killtony/episodes",
    cta: "Browse archive",
    icon: Tv,
  },
  {
    level: "02",
    title: "Open the detail page.",
    description:
      "Each episodes page shows every set from the night. Comedian pages show all sets from that comic.",
    href: "/killtony/comedians",
    cta: "See comics",
    icon: Mic2,
  },
  {
    level: "03",
    title: "Drill into the joke.",
    description:
      "Quick jump to watch set clip and see the full transcript annotated.",
    href: "/killtony/sets",
    cta: "Explore sets",
    icon: Search,
  },
];

// Literal class strings so the Tailwind scanner picks up the named-peer variants.
const peerName = ["peer/s0", "peer/s1", "peer/s2"];
const slideShow = [
  "hidden peer-checked/s0:block",
  "hidden peer-checked/s1:block",
  "hidden peer-checked/s2:block",
];

export default function HowItWorksPanel() {
  return (
    <aside className="rounded-none border border-white/10 bg-[linear-gradient(180deg,#0b1020_0%,#171d2c_100%)] p-5 shadow-[0_24px_80px_rgba(0,0,0,0.16)] lg:rounded-2xl">
      {steps.map((_, i) => (
        <input
          key={i}
          type="radio"
          name="how-it-works-step"
          id={`how-it-works-${i}`}
          defaultChecked={i === 0}
          className={`hidden ${peerName[i]}`}
        />
      ))}

      {steps.map((step, i) => {
        const Icon = step.icon;
        const prev = (i - 1 + steps.length) % steps.length;
        const next = (i + 1) % steps.length;
        return (
          <div key={i} className={slideShow[i]}>
            <div className="flex items-center justify-between gap-4">
              <h2 className="text-2xl font-bold tracking-tight text-primary sm:text-3xl">
                How it works
              </h2>
              <div className="flex items-center gap-2">
                <label
                  htmlFor={`how-it-works-${prev}`}
                  className="flex h-9 w-9 cursor-pointer items-center justify-center rounded-full border border-white/10 text-stone-300 transition-colors hover:border-primary/40 hover:text-white"
                  aria-label="Show previous step"
                >
                  <ArrowLeft className="h-4 w-4" />
                </label>
                <label
                  htmlFor={`how-it-works-${next}`}
                  className="flex h-9 w-9 cursor-pointer items-center justify-center rounded-full border border-white/10 text-stone-300 transition-colors hover:border-primary/40 hover:text-white"
                  aria-label="Show next step"
                >
                  <ArrowRight className="h-4 w-4" />
                </label>
              </div>
            </div>

            <div className="mt-5 rounded-2xl border border-white/10 bg-white/5 p-5">
              <div className="flex items-center justify-between gap-3">
                <span className="inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-primary/15 text-primary">
                  <Icon className="h-5 w-5" />
                </span>
                <span className="text-sm font-bold tracking-[0.24em] text-white/45">{step.level}</span>
              </div>

              <h3 className="mt-5 text-xl font-bold tracking-tight text-white">{step.title}</h3>
              <p className="mt-3 text-sm leading-relaxed text-stone-300">{step.description}</p>

              <div className="mt-6 flex items-center justify-end">
                <Link
                  href={step.href}
                  className="inline-flex items-center rounded-full border border-primary/30 bg-primary/12 px-4 py-2 text-xs font-bold uppercase tracking-[0.18em] text-primary transition-colors hover:bg-primary hover:text-white"
                >
                  {step.cta}
                </Link>
              </div>
            </div>
          </div>
        );
      })}
    </aside>
  );
}
