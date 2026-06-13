"use client";

import {
  ListPageFilterChipGrid,
  ListPageFilterSection,
  ListPageSortChipGrid,
  useListPageFilterRouter,
} from "@/components/ListPageFilterControls";

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
      <ListPageFilterSection title="Filter">
        <ListPageFilterChipGrid
          options={ATTRIBUTE_OPTIONS}
          currentValue={currentAttribute}
          onSelect={(value) => push({ attribute: currentAttribute === value ? "" : value })}
        />
        <div className="mt-2">
          <ListPageFilterChipGrid
            options={JOKE_BOOK_OPTIONS}
            currentValue={currentJokeBook}
            onSelect={(value) => push({ joke_book: currentJokeBook === value ? "" : value })}
          />
        </div>
      </ListPageFilterSection>
      <ListPageFilterSection title="Sort">
        <ListPageSortChipGrid
          options={SORT_OPTIONS}
          currentValue={currentSort}
          currentAsc={currentAsc}
          onToggleAsc={() => push({ asc: currentAsc ? "" : "1" })}
          onSelect={(value) => push({ sort: currentSort === value ? "" : value })}
        />
      </ListPageFilterSection>
    </div>
  );
}
