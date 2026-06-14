"use client";

import { ATTRIBUTE_LABELS } from "@/lib/attributes";
import { ListPageFilterChipGrid, useListPageFilterRouter } from "@/components/ListPageFilterControls";

const SEARCH_PATH = "/killtony/comedians/search";

const ALL_ATTRIBUTES = Object.entries(ATTRIBUTE_LABELS).map(([value, label]) => ({ value, label }));

const SORT_OPTIONS = [
  { value: "set_count", label: "Sets" },
  { value: "avg_hit_ratio", label: "Hit ratio" },
  { value: "avg_punchline_tag_ratio", label: "Punch/tag ratio" },
  { value: "avg_bits_per_set", label: "Bits per set" },
  { value: "avg_beats_per_set", label: "Beats per set" },
];

export default function ComedianSearchFilters() {
  const { getParam, push } = useListPageFilterRouter({
    searchPath: SEARCH_PATH,
    trackedParams: ["attribute", "sort", "asc"],
  });

  const currentAttribute = getParam("attribute");
  const currentSort = getParam("sort");
  const currentAsc = getParam("asc") === "1";

  return (
    <div className="mb-6 space-y-4">
      <ListPageFilterChipGrid
        title="Filter"
        options={ALL_ATTRIBUTES}
        currentValue={currentAttribute}
        onSelect={(value) => push({ attribute: currentAttribute === value ? "" : value })}
      />
      <ListPageFilterChipGrid
        title="Sort"
        options={SORT_OPTIONS}
        currentValue={currentSort}
        currentAsc={currentAsc}
        onToggleAsc={() => push({ asc: currentAsc ? "" : "1" })}
        onSelect={(value) => push({ sort: currentSort === value ? "" : value })}
      />
    </div>
  );
}
