"use client";

import { ListPageFilterChipGrid, useListPageFilterRouter } from "@/components/ListPageFilterControls";

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
      <ListPageFilterChipGrid
        title="Filter"
        options={JOKE_TYPES}
        currentValue={currentType}
        onSelect={(value) => push({ joke_type: currentType === value ? "" : value })}
      />
    </div>
  );
}
