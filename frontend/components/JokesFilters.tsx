"use client";

import { ListPageFilterSection, useListPageFilterRouter } from "@/components/ListPageFilterControls";

const JOKE_TYPES = [
  { value: "", label: "All types" },
  { value: "misdirect", label: "misdirect" },
  { value: "reframe", label: "reframe" },
  { value: "phonetic-match", label: "phonetic-match" },
  { value: "double-meaning", label: "double-meaning" },
  { value: "contradiction", label: "contradiction" },
  { value: "analogy", label: "analogy" },
  { value: "hyperbole", label: "hyperbole" },
  { value: "elephant-in-the-room", label: "elephant-in-the-room" },
];

export default function JokesFilters() {
  const { getParam, push } = useListPageFilterRouter({
    searchPath: "/killtony/jokes",
    trackedParams: ["joke_type"],
  });

  const currentType = getParam("joke_type");

  return (
    <div className="mb-6">
      <ListPageFilterSection title="Filter">
        <div className="grid gap-2 [grid-template-columns:repeat(auto-fit,minmax(150px,1fr))]">
          {JOKE_TYPES.map(({ value, label }) => (
            <button
              key={value || "all"}
              onClick={() => push({ joke_type: currentType === value ? "" : value })}
              className={`rounded-full border px-3 py-1.5 text-xs font-medium text-center transition-colors ${
                currentType === value
                  ? "border-stone-900 bg-stone-900 text-white"
                  : "border-stone-200 bg-white text-stone-600 hover:border-stone-400"
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </ListPageFilterSection>
    </div>
  );
}
