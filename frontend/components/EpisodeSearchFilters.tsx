"use client";

import { ListPageFilterChipGrid, useListPageFilterRouter } from "@/components/ListPageFilterControls";

const SEARCH_PATH = "/killtony/episodes/search";

const SORT_OPTIONS = [
  { value: "date", label: "Date" },
  { value: "duration", label: "Duration" },
  { value: "set_count", label: "Set count" },
  { value: "bucket_pulls", label: "Bucket pulls" },
  { value: "golden_tickets", label: "Golden tickets" },
  { value: "large_joke_books", label: "Big joke books" },
  { value: "regulars", label: "Regulars" },
  { value: "view_count", label: "View count" },
  { value: "like_count", label: "Like count" },
  { value: "like_ratio", label: "View/like ratio" },
];

export default function EpisodeSearchFilters() {
  const { getParam, push } = useListPageFilterRouter({
    searchPath: SEARCH_PATH,
    trackedParams: ["sort", "asc"],
  });

  const currentSort = getParam("sort", "date");
  const currentAsc = getParam("asc") === "1";

  return (
    <div className="mb-6">
      <ListPageFilterChipGrid
        title="Sort"
        options={SORT_OPTIONS}
        currentValue={currentSort}
        currentAsc={currentAsc}
        onToggleAsc={() => push({ asc: currentAsc ? "" : "1" })}
        onSelect={(value) => push({ sort: value })}
      />
    </div>
  );
}
