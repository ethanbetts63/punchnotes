"use client";

import { ListPageFilterChipGrid, useListPageFilterRouter } from "@/components/ListPageFilterControls";

const SEARCH_PATH = "/killtony/sets/search";

const ATTRIBUTE_OPTIONS = [
  { value: "bucket_pull", label: "Bucket Pull" },
  { value: "regular", label: "Regular" },
  { value: "golden_ticket", label: "Golden Ticket" },
  { value: "special", label: "Special" },
];

const JOKE_BOOK_OPTIONS = [
  { value: "small", label: "Small Joke Book" },
  { value: "medium", label: "Medium Joke Book" },
  { value: "large", label: "Large Joke Book" },
];

const SORT_OPTIONS = [
  { value: "bit_count", label: "Bits" },
  { value: "hit_ratio", label: "Hit ratio" },
  { value: "punchline_tag_ratio", label: "Punch/tag ratio" },
];

export default function SetSearchFilters() {
  const { getParam, push } = useListPageFilterRouter({
    searchPath: SEARCH_PATH,
    trackedParams: ["attribute", "joke_book", "sort", "asc"],
  });

  const currentAttribute = getParam("attribute");
  const currentJokeBook = getParam("joke_book");
  const currentSort = getParam("sort");
  const currentAsc = getParam("asc") === "1";

  return (
    <div className="mb-6 space-y-4">
      <ListPageFilterChipGrid
        title="Filter"
        options={[...ATTRIBUTE_OPTIONS, ...JOKE_BOOK_OPTIONS]}
        currentValue={currentAttribute || currentJokeBook}
        onSelect={(value) => {
          const isAttribute = ATTRIBUTE_OPTIONS.some((o) => o.value === value);
          if (isAttribute) push({ attribute: currentAttribute === value ? "" : value, joke_book: "" });
          else push({ joke_book: currentJokeBook === value ? "" : value, attribute: "" });
        }}
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
